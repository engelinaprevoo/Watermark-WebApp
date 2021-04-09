"""
    Written by: Caroline Prevoo

    Date start: 6 april 2021

    Goal      : Watermark Photo
"""

import imghdr
import os

from PIL import Image
from flask import Flask, render_template, request, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/uploads'

def watermark_with_image(input_image_path, output_image_path):
    watermark_image = Image.open('static/img/watermark.png')
    w_width, w_height = watermark_image.size
    image = Image.open(input_image_path)
    width, height = image.size

    size = (width, height)
    watermark_image = watermark_image.resize(size, Image.ANTIALIAS)

    pos = (0, 0)
    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(image, (0, 0))
    transparent.paste(watermark_image, pos, mask=watermark_image)

    transparent.save(output_image_path)


def delete_uploaded_files():
    folder = app.config['UPLOAD_PATH']
    files = [f for f in os.listdir(folder)]
    for file in files:
        os.remove(os.path.join(folder, file))


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['file']
        filename = secure_filename(image.filename)
        # Solving spaces in filename (replaced by secure _)
        image.filename = filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(image.stream):
                # TODO: flash file not allowed
                abort(400)
            image.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return render_template('watermark.html', filename=filename)
        # return redirect('watermark.html')

    # 'GET' request
    return render_template('watermark.html')


@app.route('/watermark', methods=['POST'])
def watermark():
    # Add watermark to the image
    # Get path of the uploaded image
    filename = request.args.get('filename')
    img_path = os.path.join(app.config['UPLOAD_PATH'], filename)

    # Remove .jpg, .jpeg or .tif -> output ..._watermarked.png
    name, _ext = os.path.splitext(filename)
    w_filename = f"{name}_watermarked.png"
    w_img_path = os.path.join(app.config['UPLOAD_PATH'], w_filename)

    watermark_with_image(img_path, w_img_path)
    return render_template('watermark.html', filename=w_filename)


@app.route('/download', methods=['POST'])
def download():
    # Download image with watermark
    filename = request.args.get('filename')
    return send_from_directory("static/uploads", filename, as_attachment=True)


@app.route('/delete')
def delete():
    delete_uploaded_files()
    return render_template('watermark.html')


if __name__ == '__main__':
    delete_uploaded_files()
    app.run(debug=True)
