import os
from flask import Flask, request, jsonify, render_template
import cv2
import pytesseract
import re
from PIL import Image
import io

app = Flask(__name__)

# Path to your Tesseract OCR executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_pan_details(image_path):
    """Process the image and extract PAN card details."""
    # Read and preprocess the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    processed_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Extract text
    text = pytesseract.image_to_string(processed_image, config='--psm 6')

    # Use regex to find specific fields
    details = {
        'name': re.search(r'(?:Name\s*:\s*|Name\s+)([A-Za-z\s]+)', text, re.IGNORECASE),
        "fatherName": re.search(r"(?:Father's\s+Name\s*:\s*|Father's\s+Name\s+)([A-Za-z\s]+)", text, re.IGNORECASE),
        'dob': re.search(r'(?:DOB|Date of Birth|Birth\s*Date)\s*:\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE),
        'panNumber': re.search(r'\b([A-Z]{5}\d{4}[A-Z])\b', text)  # PAN format
    }

    # Format the extracted details
    return {
        'name': details['name'].group(1).strip() if details['name'] else 'Not found',
        'fatherName': details["fatherName"].group(1).strip() if details["fatherName"] else 'Not found',
        'dob': details['dob'].group(1).strip() if details['dob'] else 'Not found',
        'panNumber': details['panNumber'].group(1).strip() if details['panNumber'] else 'Not found'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded image to a temporary file
    temp_path = 'temp_image.jpg'
    file.save(temp_path)

    # Extract details from the image
    details = extract_pan_details(temp_path)

    # Clean up the temporary image file
    os.remove(temp_path)

    return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True)

# Path to the PAN card image
# image_path = 'path/to/your/pan_card_image.jpg'
# test_img_path = "../Image/"
# create_path = lambda f : os.path.join(test_img_path, f)
# image_path = "pan.jpg"
# path = create_path(image_path)
# main(path)
