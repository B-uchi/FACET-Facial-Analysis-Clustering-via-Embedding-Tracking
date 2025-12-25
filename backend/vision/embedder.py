from .detector import app as face_app
import numpy as np

def embed(img):
    """
    Extract embedding from an image (used for query images).
    """
    try:
        faces = face_app.get(img)
        if not faces:
            return None
        return faces[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

