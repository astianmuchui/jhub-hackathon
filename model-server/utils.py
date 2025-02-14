import os
import io
import sys
import logging
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'model-server')))

# Define image size and class labels
IMG_SIZE = (224, 224)
class_labels = ['adenocarcinoma', 'large.cell.carcinoma', 'normal', 'squamous.cell.carcinoma']

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Given image bytes, convert the image to RGB, resize it,
    convert it to a numpy array, and normalize the pixel values.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Ensure image is in RGB format
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize the image to the expected size
        image = image.resize(IMG_SIZE)

        # Convert the image to a numpy array and normalize pixel values to [0, 1]
        image_array = np.array(image).astype("float32") / 255.0

        # Add a batch dimension
        image_array = np.expand_dims(image_array, axis=0)

        return image_array
    except Exception as e:
        logging.error(f"Error preprocessing image: {str(e)}")
        raise

def get_explanation(predicted_label: str, confidence: float) -> str:
    """
    Calls the GPT API using the new client interface to generate a detailed explanation
    based on the prediction result.
    """
    explanations = {
        "adenocarcinoma": (
            "Your CT scan suggests adenocarcinoma, the most common type of lung cancer. "
            "This cancer originates in the glandular tissues of the lung, which produce mucus, "
            "and is often found in the outer parts of the lung. Symptoms may include a persistent cough, "
            "hoarseness, weight loss, and fatigue. Early detection improves treatment options, which may include "
            "surgery, chemotherapy, radiation therapy, or targeted therapy. It is important to consult a doctor "
            "for further evaluation and guidance."
        ),
        "large.cell.carcinoma": (
            "Your CT scan suggests large cell carcinoma, a fast-growing type of lung cancer that can appear anywhere in the lungs. "
            "This type of cancer spreads quickly and accounts for about 10-15% of non-small cell lung cancer cases. "
            "Because of its rapid growth, early medical intervention is crucial. Treatment options may include "
            "surgery, chemotherapy, immunotherapy, or radiation therapy. Please seek immediate medical consultation to discuss further steps."
        ),
        "squamous.cell.carcinoma": (
            "Your CT scan suggests squamous cell carcinoma, a type of lung cancer typically linked to smoking. "
            "It occurs in the larger airways (bronchi) of the lungs and accounts for about 30% of non-small cell lung cancers. "
            "Symptoms may include chronic coughing, chest pain, and difficulty breathing. Treatment options may include "
            "surgery, radiation therapy, chemotherapy, or targeted therapies. Please consult a healthcare provider to confirm the diagnosis and explore the best treatment approach."
        ),
        "normal": (
            "Your CT scan appears normal, with no signs of lung cancer detected. This is a positive result, but if you experience "
            "any persistent symptoms such as coughing, chest pain, or difficulty breathing, it is always a good idea to follow up with your doctor. "
            "Maintaining regular check-ups and a healthy lifestyle can help ensure long-term lung health."
        ),
    }

    # Get explanation based on the predicted label, or provide a generic response
    explanation = explanations.get(
        predicted_label,
        "The AI model has identified an unfamiliar category. Please consult a healthcare provider for further evaluation."
    )

    # Format the final response with confidence level
    response = (
        f"The image analysis model has classified the chest CT scan as '{predicted_label}' "
        f"with a confidence of {confidence:.2f}%.\n\n{explanation}\n\n"
        "Please note that this is not a definitive diagnosis but a general explanation to help you understand the result. "
        "Consult a medical professional for accurate diagnosis and guidance."
    )

    return response