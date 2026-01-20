"""
Face recognition service using face_recognition library.
"""
import base64
import io
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition library not available. Face verification will be simulated.")

from app.config import settings


def decode_base64_image(base64_string: str) -> Optional[np.ndarray]:
    """
    Decode a base64 image string to numpy array.
    
    Args:
        base64_string: Base64 encoded image (with or without data URL prefix)
        
    Returns:
        Numpy array of the image, or None if decoding fails
    """
    try:
        # Remove data URL prefix if present
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image then to numpy array
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        return np.array(image)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def extract_face_encoding(image: np.ndarray) -> Optional[List[float]]:
    """
    Extract face encoding from an image.
    
    Args:
        image: Numpy array of the image
        
    Returns:
        List of 128 floats representing the face encoding, or None if no face found
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Return a dummy encoding for testing when library not available
        print("WARNING: Returning dummy face encoding (face_recognition not available)")
        return [0.0] * 128
    
    try:
        # Find face locations
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return None
        
        # Get encoding for the first face found
        encodings = face_recognition.face_encodings(image, face_locations)
        
        if not encodings:
            return None
        
        return encodings[0].tolist()
    except Exception as e:
        print(f"Error extracting face encoding: {e}")
        return None


def compare_faces(
    known_encoding: List[float],
    unknown_encoding: List[float],
    tolerance: Optional[float] = None
) -> Tuple[bool, float]:
    """
    Compare two face encodings.
    
    Args:
        known_encoding: The stored face encoding
        unknown_encoding: The encoding to compare against
        tolerance: Match tolerance (lower = stricter). Uses config default if None.
        
    Returns:
        Tuple of (is_match, distance)
    """
    if tolerance is None:
        tolerance = settings.FACE_MATCH_TOLERANCE
    
    if not FACE_RECOGNITION_AVAILABLE:
        # Simulate a match for testing
        print("WARNING: Simulating face match (face_recognition not available)")
        return True, 0.3
    
    try:
        known = np.array(known_encoding)
        unknown = np.array(unknown_encoding)
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(known - unknown)
        
        is_match = distance <= tolerance
        
        return is_match, float(distance)
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return False, 1.0


def extract_encoding_from_base64(base64_image: str) -> Optional[List[float]]:
    """
    Extract face encoding directly from a base64 image string.
    
    Args:
        base64_image: Base64 encoded image
        
    Returns:
        Face encoding or None if extraction fails
    """
    image = decode_base64_image(base64_image)
    if image is None:
        return None
    
    return extract_face_encoding(image)

