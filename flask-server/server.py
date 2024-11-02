import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
import torchvision.transforms as transforms
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
CORS(app)

# Load AI model
# model_path = ''
# model = torch.load(model_path)
# model.eval()

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

        with Image.open(image_path) as img:
            img.verify() # Closes the image for some ungodly reason.
        with Image.open(image_path) as img:
            img.show()
            # img_tensor = preprocess_image(img) # Preprocess image for AI
            # response = diagnosis(img_tensor) # Get response from AI
    except IOError as e:
        return jsonify({'error': f"IOError: {str(e)} - Check if the file is a valid image."}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Testing
    response = {
        "disease": "Dheeraj is too beautiful."
    }

    try:
        time.sleep(0.5) # Resolve file concurrent access issues
        os.remove(image_path)
    except PermissionError:
        return jsonify({"error":"Could not delete file. File may be in use,"}), 500
    # Cleanup files


    return jsonify(response), 200



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
