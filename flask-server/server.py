import time

import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter
import torch
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



# Load AI model
# model_path = ''
# model = torch.load(model_path)
# model.eval()


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


# Image processing
def preprocess_image(image_data):

    transform = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
    ])

    img_tensor = transform(image_data)
    img_tensor = img_tensor.unsqueeze(0)
    return img_tensor

@app.route('/report', methods=['POST'])
def report_disease():
    # Get submission from upload
    description = request.form.get('description')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Make sure its not empty
    if not description or latitude is None or longitude is None:
        return jsonify({'error': 'Description, latitude, and longitude are required.'}), 400

    # Create a new report entry
    new_report = {
        'description': description,
        'location': {
            'latitude': latitude,
            'longitude': longitude
        }
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
            magic_kernel_resize(image_path, resized_image_path, new_size, extra_sharpening=150)
        # Resized image
        with Image.open(resized_image_path) as img:
            img.show()

            img_tensor = preprocess_image(img) # Preprocess image for AI
            # response = diagnosis(img_tensor) # Get response from AI
    except IOError as e:
        return jsonify({'error': f"IOError: {str(e)} - Check if the file is a valid image."}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Testing for before model is complete
    response = {
        "disease": "Dheeraj is wonderful."
    }

    # Cleanup files
    try:
        time.sleep(0.5) # Resolve file concurrent access issues
        os.remove(image_path)
        os.remove(resized_image_path)
    except PermissionError:
        return jsonify({"error":"Could not delete file. File may be in use,"}), 500



    return jsonify(response), 200


# # Model code, uncomment when merge w/ feature-ml-model
# def diagnosis(img_tensor):
#     with torch.no_grad():
#         prediction = model(img_tensor)
#
#     # Parse model output
#     model_output = prediction[0]
#     diagnosis = model_output.item() if isinstance(model_output, torch.Tensor) else model_output
#
#     # Json formatting
#     response = {
#         "diagnosis": diagnosis
#     }
#
#     return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
