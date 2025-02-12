import io
import os
import logging
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from typing import Tuple

from utils import preprocess_image, get_explanation

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the Trained Model
model_path = os.getenv('MODEL_PATH', os.path.join(os.path.dirname(__file__), 'models/chest_ct_scan_model.h5'))
model = tf.keras.models.load_model(model_path)

# Define image size and class labels
IMG_SIZE = (224, 224)
class_labels = ['adenocarcinoma', 'large.cell.carcinoma', 'normal', 'squamous.cell.carcinoma']

def load_image(file) -> np.ndarray:
    """Load and preprocess the image."""
    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        return processed_image
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise

def get_prediction(image: np.ndarray) -> Tuple[str, float]:
    """Get model prediction and confidence."""
    predictions = model.predict(image)
    predicted_index = np.argmax(predictions, axis=1)[0]
    predicted_label = class_labels[predicted_index]
    confidence = float(np.max(predictions) * 100)
    return predicted_label, confidence

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    try:
        processed_image = load_image(file)
        predicted_label, confidence = get_prediction(processed_image)
        explanation = get_explanation(predicted_label, confidence)
        
        return jsonify({
            "predicted_label": predicted_label,
            "confidence": confidence,
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'True') == 'True')