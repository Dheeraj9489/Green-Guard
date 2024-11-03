import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
CORS(app)

REPORTS_FILE = 'reports.json'
# Ensure the reports file exists
if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'w') as f:
        json.dump([], f)  # Start with an empty list

num_classes = 10

class Classifier(nn.Module):
    def __init__(self, num_classes):
        super(Classifier, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(32 * 64 * 64, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


model = torch.load('disease_detection.pth')
model.eval()

# Image processing
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,),(0.5,))
    ])

    img_tensor = transform(image)
    img_tensor = img_tensor.unsqueeze(0)
    return img_tensor



def magic_kernel_resize(input_filename, output_filename, target_size=(256,256), extra_sharpening=0):
    # open input
    img = Image.open(input_filename)
    # resize image
    img = img.resize(target_size,Image.LANCZOS)
    if extra_sharpening > 0:
        sharpener = ImageFilter.UnsharpMask(radius=2,percent=extra_sharpening, threshold=3)
        img = img.filter(sharpener)

    # Save resized img
    img.save(output_filename)





@app.route('/report', methods=['POST'])
def report_disease():
    # Get submission from upload
    data = request.json
    plant = data.get('plant')
    disease = data.get('disease')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Make sure its not empty
    print(f'plant: {plant}, disease: {disease}, latitude: {latitude}, longitude: {longitude}')
    if not plant or not disease or not latitude or not longitude:
        return jsonify({'error': 'Description, latitude, and longitude are required.'}), 400

    # Create a new report entry
    new_report = {
        'plant': plant,
        'disease': disease,
        'latitude': latitude,
        'longitude': longitude
    }

    # Load existing reports
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)

    # Add the new report to the list
    reports.append(new_report)

    # Save back to the JSON file
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f)

    return jsonify({'message': 'Report submitted successfully!'}), 201




@app.route('/get_reports', methods=['GET'])
def get_reports():
    with open(REPORTS_FILE, 'r') as f:
        reports = json.load(f)
    return jsonify(reports), 200



@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'})

    # Read in arguments
    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'No selected file.'})

    # Image saving stuff
    filename = secure_filename(image.filename)
    image_path = os.path.join('uploads',filename)
    os.makedirs('uploads', exist_ok=True)

    image.save(image_path)

    print(f"Uploaded file type: {image.mimetype}")

    try:
        file_size = os.path.getsize(image_path)
        if file_size < 8:
            return jsonify({'error': 'File too small.'}), 400

        # With == os.remove works :)
        with Image.open(image_path) as img:
            img.verify() # Closes the image for some ungodly reason.
        with Image.open(image_path) as img:
            img.show()

            new_size = (256,256)
            resized_image_path = os.path.join('uploads', 'resized_'+filename)
            magic_kernel_resize(image_path, resized_image_path, new_size)
        # Resized image
        with Image.open(resized_image_path) as img:
            img.show()

            img_tensor = preprocess_image(img) # Preprocess image for AI
            response = diagnosis(img_tensor) # Get response from AI
    except IOError as e:
        return jsonify({'error': f"IOError: {str(e)} - Check if the file is a valid image."}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    # Cleanup files
    try:
        time.sleep(0.5) # Resolve file concurrent access issues
        os.remove(image_path)
        os.remove(resized_image_path)
    except PermissionError:
        return jsonify({"error":"Could not delete file. File may be in use,"}), 500



    return jsonify(response), 200



def diagnosis(img_tensor):
    with torch.no_grad():
        prediction = model(img_tensor)
    class_names = ['Tomato___Bacterial_Spot', 'Tomato___Early_Blight', 'Tomato___Late_Blight', 'Tomato___Leaf_Mold',
                   'Tomato___Septoria_Leaf_Spot', 'Tomato___Two_Spotted_Spider_Mite', 'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_Mosaic_Virus', 'Tomato___Healthy']

    probabilities = F.softmax(prediction, dim=1)

    predicted_index = torch.argmax(probabilities, dim=1).item()
    predicted_class = class_names[predicted_index]

    plant = predicted_class.split('___')[0]
    disease = " ".join(predicted_class.split('___')[1].split('_'))
    # Json formatting
    response = {
        "plant": plant,
        "disease": disease
    }

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
