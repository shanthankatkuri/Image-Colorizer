from flask import Flask, render_template, request, send_file, url_for
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DISPLAY_WIDTH = 800

os.makedirs(UPLOAD_FOLDER, exist_ok = True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models") 
PROTOTXT = os.path.join(MODELS_DIR, r"colorization_deploy_v2.prototxt")
POINTS = os.path.join(MODELS_DIR, r"pts_in_hull.npy")
MODEL = os.path.join(MODELS_DIR, r"colorization_release_v2.caffemodel")

net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
pts = np.load(POINTS)


# Load centers for ab channel quantization used for rebalancing.
class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")
pts = pts.transpose().reshape(2, 313, 1, 1)
net.getLayer(class8).blobs = [pts.astype("float32")]
net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_for_display(img, width=800):
    aspect_ratio = img.shape[1] / img.shape[0]
    height = int(width / aspect_ratio)
    return cv2.resize(img, (width, height))

def colorize_image(image_path):
    image = cv2.imread(image_path)
    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)

    colorized = (255 * colorized).astype("uint8")
    
    display_colorized = resize_for_display(colorized)
    return display_colorized

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) 
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('upload.html', error="No file part in the request")
        file = request.files['image']
        print("Filename:", file.filename)
        if file.filename == '':
            return render_template('upload.html', error="No file selected")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            colorized = colorize_image(filepath)

            colorized_filename = 'colorized_' + filename
            colorized_filepath = os.path.join(app.config['UPLOAD_FOLDER'], colorized_filename)
            cv2.imwrite(colorized_filepath, colorized)

            return render_template('result.html',
                original = url_for('static', filename=f'uploads/{filename}'),
                colorized = url_for('static', filename=f'uploads/{colorized_filename}')
            )
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)    