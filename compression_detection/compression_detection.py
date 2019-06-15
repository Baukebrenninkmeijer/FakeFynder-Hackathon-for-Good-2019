from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
from tqdm import tqdm
import subprocess
import pickle
import shlex
import json

COMPRESSION_DIR = 'compression_detection'
NUM_COLS = ['duration', 'duration_ts', 'nb_frames', 'width', 'bit_rate', 'width', 'height', 'coded_width',
            'coded_height', 'start_time', 'bits_per_raw_sample', 'nal_length_size']
DROP_COLS = ['disposition', 'tags']


def findVideoMetada(pathToInputVideo):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    # Only return video information
    return ffprobeOutput['streams'][0]


def create_compressed_dataset(source_path, target_path):
    for i in tqdm(os.scandir(source_path)):
        path = i.path.replace('\\', '/')
        metadata = findVideoMetada(path)
        assert len(metadata) in [1, 2], f'{metadata}'
        old_bitrate = int(metadata['bit_rate'])
        bitrate_percentages = [0.77, 0.6]
        crfs = [23, 40]
        new_bitrates = [int(old_bitrate * perc) for perc in bitrate_percentages]

        if not os.path.exists(f'{target_path}'):
            os.mkdir(f'{target_path}')

        for perc, bitrate, crf in zip(bitrate_percentages, new_bitrates, crfs):
            if not os.path.exists(f'{target_path}/{perc}'):
                os.mkdir(f'{target_path}/{perc}')
            cmd = f'ffmpeg -y -i {path} -c:v libx264 -crf {crf} {target_path}/{perc}/{i.name}'
            args = shlex.split(cmd)
            ffprobeOutput = subprocess.check_output(args).decode('utf-8')


def aggregate_metadata(path):
    target_path = path
    scandir = os.scandir(target_path)
    metadata_agg = []
    classes = []
    for p in scandir:
        if p.is_dir:
            for o in tqdm(os.scandir(p.path), total=1000):
                metadata_agg.append(findVideoMetada(o.path))
                classes.append(p.name)
    data = pd.DataFrame(metadata_agg)
    return data, classes


def train_classifier(data=None, X=None, Y=None, path=None, save=False):
    if path is not None:
        copy, classes = aggregate_metadata(path)
    elif X is not None and Y is not None:
        copy = X
        classes = Y
    else:
        copy = data.drop(['class'], axis=1)
        classes = data['class']

    copy = copy.drop(DROP_COLS, axis=1)

    # convert columns like 'bit_rate' to float dtype
    copy.loc[:, NUM_COLS] = copy[NUM_COLS].astype('float')

    copy = copy._get_numeric_data()

    model = DecisionTreeClassifier(max_depth=5)
    copy = copy.sort_index(axis=1)
    x_train, x_test, y_train, y_test = train_test_split(copy, classes, test_size=0.2, shuffle=True)
    model.fit(x_train, y_train)

    if save:
        pickle.dump(model, open('model.pkl', 'wb'))
        pickle.dump(copy.columns.tolist(), open('columns.pkl', 'wb'))

    score = model.score(x_test, y_test)
    preds = model.predict(x_test)
    print(np.unique(preds))
    print(f'Model saved. Model score: {score}')


def classify_video(path):
    columns = pickle.load(open(f'{COMPRESSION_DIR}/columns.pkl', 'rb'))
    medians = pickle.load(open(f'{COMPRESSION_DIR}/medians.pkl', 'rb'))

    metadata_dict = findVideoMetada(path)
    metadata = pd.DataFrame([metadata_dict])


    metadata = metadata.drop(DROP_COLS, axis=1)

    # convert columns like 'bit_rate' to float dtype
    # print(metadata)
    metadata[NUM_COLS] = metadata[NUM_COLS].astype('float')

    metadata = metadata._get_numeric_data()
    bool_cols = metadata.select_dtypes(include=['bool']).columns
    metadata[bool_cols] = metadata[bool_cols].astype('int')

    for col in columns:
        if col not in metadata.columns.tolist():
            metadata[col] = medians.get(col, 0)

    # cat_cols = metadata.select_dtypes(['object']).columns
    # dummies = pd.get_dummies(metadata[cat_cols])
    # metadata[dummies.columns] = dummies
    # metadata = metadata.drop(cat_cols, axis=1)
    metadata = metadata.sort_index(axis=1)

    model = pickle.load(open(f'{COMPRESSION_DIR}/model.pkl', 'rb'))
    prediction = model.predict(metadata)[0]
    return prediction


