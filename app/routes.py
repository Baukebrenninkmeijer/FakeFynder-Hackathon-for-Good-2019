import sys
sys.path.append('./classification')

sys.path.append('../classification')
sys.path.append('..')

from app import app
from classification.detect_from_video import test_full_image_network
from classification.network import models
from app.download_yt import download_video

import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = './classification/data_dir/uploads'
ALLOWED_EXTENSIONS = set(['mp4', 'avi'])
MODEL_PATH = './classification/weights/full/xception/full_c23.p'
OUTPUT_PATH = './classification/data_dir/results'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cuda = False

# model_full =
# model_77 =
# model_60 =


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('Upload.html')


# POST IMAGE 
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    if request.method =='POST':
              # check if the post request has the file part
        # if 'data_file' in request.files:
        if 'youtube_link' in request.files:
            print('turbo tetten')

        # if 'data_file' not in request.files and 'youtube_link' not in request.files:
        #     flash('No file part')
        #     return redirect(request.url)

        # # if user does not select file, browser also
        # # submit an empty part without filename
        # if file.filename == '':
        #     flash('No selected file')
        #     return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     print('filename = ', filename)
        # else:       
        #     return render_template('error.html')

        # if 'data_file' in request.files:
        #     file = request.files['data_file']
        #     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #     file.save(filepath)
        # elif 'youtube_link' in request.files:
        #     download_video(filename)
        #     file = request.files['youtube_link']
        # # if not 'data_file' in request.files:
        # #         download_video()

        # print(filename, ' was uploaded.')
        # print(filepath)



        # test_full_image_network(filepath, MODEL_PATH, OUTPUT_PATH,
        #                     start_frame=0, end_frame=None, cuda=cuda)

        return render_template('Upload.html')
    else:
        return render_template('error.html')

# if __name__ == "__main__":

#     # run app
#     app.run(host = "0.0.0.0", port = int("5000"))


# '''
# <!doctype html>
# <title>Upload new File</title>
# <h1>Upload new File</h1>
# <form method=post enctype=multipart/form-data>
#   <input type=file name=file>
#   <input type=submit value=Upload>
# </form>
# '''
