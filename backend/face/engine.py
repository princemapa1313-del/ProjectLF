"""
Lost & Finder — face/engine.py
Face recognition wrapper using face_recognition and numpy.
"""
import io
import numpy as np
from PIL import Image

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition module not found. Face matching will be mocked.")

def generate_encoding(file_bytes: bytes) -> list:
    """
    Reads image bytes, finds a face, and returns a 128-d encoding as a list.
    If no face is found, returns an empty list.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Mock encoding for testing without dlib: Hash the image bytes
        import hashlib
        h = hashlib.md5(file_bytes).digest()
        encoding = [float(b)/255.0 for b in h]
        encoding.extend([0.0] * (128 - len(encoding)))
        return encoding
        
    try:
        # Convert bytes to PIL Image, then to numpy array (RGB)
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        image_np = np.array(image)
        
        # Find face locations and encodings
        encodings = face_recognition.face_encodings(image_np)
        
        if len(encodings) > 0:
            # Return the first face found, converted to list for MongoDB
            return encodings[0].tolist()
        return []
    except Exception as e:
        print(f"Error generating encoding: {e}")
        return []

def compare_faces(known_encoding: list, unknown_encoding: list, tolerance: float = 0.5) -> float:
    """
    Compares two face encodings and returns the confidence percentage (0-100).
    A lower distance means higher confidence.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Compare manually
        import math
        if not known_encoding or not unknown_encoding:
            return 0.0
        dist = math.sqrt(sum((a - b)**2 for a, b in zip(known_encoding, unknown_encoding)))
        if dist < 0.1:
            return 99.0
        return 0.0

    if not known_encoding or not unknown_encoding:
        return 0.0

    known_np = np.array(known_encoding)
    unknown_np = np.array(unknown_encoding)
    
    # Calculate Euclidean distance
    distance = face_recognition.face_distance([known_np], unknown_np)[0]
    
    # Convert distance to a confidence score (0 to 100)
    # distance 0.0 == 100% match
    # distance > tolerance == 0% match (or very low)
    if distance > tolerance:
        # It's not a strong match, but let's give a low score
        confidence = max(0.0, 100.0 - (distance * 100.0))
        return confidence
    else:
        # Math: mapping distance [0, tolerance] to [100, 50] for example
        # Let's just use a simple linear conversion:
        confidence = (1.0 - distance) * 100.0
        return min(100.0, confidence)
