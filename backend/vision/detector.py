from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1)

def detect_faces(img):
    return app.get(img)

