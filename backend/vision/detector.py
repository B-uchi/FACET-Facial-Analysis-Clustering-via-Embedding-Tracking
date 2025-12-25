from insightface.app import FaceAnalysis

# Initialize FaceAnalysis once
# We use providers=['CPUExecutionProvider'] for compatibility as seen in requirements.txt (torch+cpu)
app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1) # Use CPU

def detect_faces(img):
    return app.get(img)

