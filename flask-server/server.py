from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def upload_image():
    #handle image upload + process w/ model
    image = request.files['image']
    #process image
    plant_name, disease_name = diagnosis(image)
    return jsonify({'plant_name': plant_name, 'disease_name': disease_name})

def diagnosis(image):
    return 'tomato','poisoned'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
