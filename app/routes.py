import sys
import glob
sys.path.append('./classification')
sys.path.append('..')

from app import app
from classification.detect_from_video import test_full_image_network
from classification.network import models
import torch
from app.download_yt import download_video
from compression_detection import compression_detection

import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from library import *
import hashlib


UPLOAD_FOLDER = './classification/data_dir/uploads'
ALLOWED_EXTENSIONS = set(['mp4', 'avi'])
MODEL_PATH = './classification/weights/full/xception/full_c23.p'
OUTPUT_PATH = './classification/data_dir/results'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cuda = False

base_weights_path = 'classification/weights/face_detection/xception'
model_full_path = f'{base_weights_path}/all_raw.p'
model_77_path = f'{base_weights_path}/all_c23.p'
model_60_path = f'{base_weights_path}/all_c40.p'

model_full = torch.load(model_full_path, map_location=lambda storage, loc: storage)
model_77 = torch.load(model_77_path, map_location=lambda storage, loc: storage)
model_60 = torch.load(model_60_path, map_location=lambda storage, loc: storage)

dbio = DatabaseIO()



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('Upload2.html')


# POST IMAGE 
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    if request.method =='POST':
        fake = None
        youtube_url = None
        history = dbio.read_history()

        # if 'youtube_link' in request.form:
        #     print(request.form['youtube_link'])

        if 'data_file' not in request.files and 'youtube_link' not in request.form:
            flash('No file part')
            return redirect(request.url)

        if 'data_file' in request.files:
            file = request.files['data_file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print('filename = ', filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        elif 'youtube_link' in request.form:
            youtube_url = request.form['youtube_link']

            if youtube_url in history['link'].values:
                fake = history.loc[history['link'] == youtube_url, 'fake'][0]

            if fake is not None:
                return render_template('fake.html') if fake else render_template('real.html')

            os.chdir(UPLOAD_FOLDER)
            download_video(youtube_url)
            os.chdir('../../..')
            list_of_files = glob.glob(f'{UPLOAD_FOLDER}/*')
            latest_file = max(list_of_files, key=os.path.getctime)
            filepath = latest_file
        else:
            return render_template('error.html')

        hasher = hashlib.sha512()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        hash = hasher.hexdigest()
        if hash in history.hash.values:
            fake = history.loc[history.hash == hash, 'hash'][0]

        if fake is not None:
            return render_template('fake.html') if fake else render_template('real.html')

        predicted_class = compression_detection.classify_video(filepath)

        if predicted_class == '0.6':
            fake_prediction = test_full_image_network(filepath, model=model_60, output_path=OUTPUT_PATH,
                                    start_frame=0, end_frame=None, cuda=cuda)
        elif predicted_class == '0.77':
            fake_prediction = test_full_image_network(filepath, model=model_77, output_path=OUTPUT_PATH,
                                    start_frame=0, end_frame=None, cuda=cuda)
        elif predicted_class == 'original':
            fake_prediction = test_full_image_network(filepath, model=model_full, output_path=OUTPUT_PATH,
                                    start_frame=0, end_frame=None, cuda=cuda)
        else:
            fake_prediction = None

        # print(f'fake_prediction: {fake_prediction}')
        if fake_prediction is not None:
            history = history.append({'hash': hash, 'link': youtube_url, 'fake': fake_prediction}, ignore_index=True)
            dbio.write_history(history)

        if fake_prediction == 1:
            return render_template('fake.hmtl')
        elif fake_prediction == 0:
            return render_template('real.html')
        else:
            return render_template('error.html')

    else:
        return render_template('error.html')
