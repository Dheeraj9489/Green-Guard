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
model_path = ''
model = torch.load(model_path)
model.eval()

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
    # Read in arguments
    image = request.files['image']

    # Handle no file upload
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded image temp
    filename = secure_filename(image.filename)
    image_path = os.path.join('uploads',filename)
    image.save(image_path)

    # Open image
    img = Image.open(image_path)

    # Preprocess the image
    img_tensor = preprocess_image(img)

    # Contact AI model
    response = diagnosis(img_tensor)

    # Cleanup files
    os.remove(image_path)

    return jsonify({response})



def diagnosis(img_tensor):
    with torch.no_grad():
        prediction = model(img_tensor)

    # Parse model output
    model_output = prediction[0]
    diagnosis = model_output.item() if isinstance(model_output, torch.Tensor) else model_output

    # Json formatting
    response = {
        "diagnosis": diagnosis
    }

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
