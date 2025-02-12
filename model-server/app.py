from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io

# initialize the Flask app
app = Flask(__name__)

# enable CORS
CORS(app)

# load the Trained Model
model = tf.keras.models.load_model('models/best_model.h5')

IMG_SIZE = (224, 224)

class_labels = ['adenocarcinoma','large.cell.carcinoma','normal','squamous.cell.carcinoma']

def preprocess_image(image_bytes):
    """
    Given image bytes, convert the image to RGB, resize it,
    convert it to a numpy array, and normalize the pixel values.
    """
    # Open the image using PIL
    image = Image.open(io.BytesIO(image_bytes))

    # Ensure image is in RGB format
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize the image to the expected size
    image = image.resize(IMG_SIZE)

    # convert the image to numpy array and normalize the pixel values to [0, 1]
    image_array = np.array(image).astype("float32") / 255.0

    # add a batch dimension 
    image_array = np.expand_dims(image_array, axis=0)

    return image_array

@app.route("/predict", methods=["POST"])
def predict():
    # check if a file was sent in the request
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # read image bytes and preprocess the image
        image_bytes = file.read()
        preprocess_image = preprocess_image(image_bytes)
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500
    
    # Get model prediction in a json file
    predictions = model.predict(preprocess_image)
    predicted_index = np.argmax(predictions, axis=1)[0]
    predicted_label = class_labels[predicted_index]
    confidence = float(np.max(predictions) * 100)

    return jsonify({
        "predicted_label": predicted_label,
        "confidence": confidence
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    