import os
import uuid
import shutil
import tempfile
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="insightface")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import cv2
import numpy as np

from models import Base, Media, FaceTrack, FaceEmbedding
from vision.pipeline import process_video, finalize_tracks
from vision.embedder import embed
from prometheus_client import Counter, generate_latest

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/faces"
)

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Ensure pgvector extension exists
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(engine)

# Migration: Add filename column to media if it exists but is missing the column
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE media ADD COLUMN filename VARCHAR"))
        conn.commit()
    except Exception:
        pass


# -------------------------------------------------------------------
# App + Metrics
# -------------------------------------------------------------------

app = FastAPI(title="FACET Engine")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

requests_total = Counter(
    "requests_total", "Total HTTP requests"
)

@app.middleware("http")
async def count_requests(request, call_next):
    requests_total.inc()
    return await call_next(request)

# -------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------

def decode_image(data: bytes):
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid image")
    return img

# -------------------------------------------------------------------
# Health / Metrics
# -------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return generate_latest()

@app.get("/media")
def list_media():
    session: Session = SessionLocal()
    try:
        media_list = session.query(Media).all()
        return [{"id": m.id, "url": f"/uploads/{m.filename}"} for m in media_list]
    finally:
        session.close()

@app.get("/media/{media_id}")
def get_media(media_id: str):
    session: Session = SessionLocal()
    try:
        m = session.query(Media).filter(Media.id == media_id).first()
        if not m:
            raise HTTPException(404, "Media not found")
        return {"id": m.id, "url": f"/uploads/{m.filename}"}
    finally:
        session.close()


# -------------------------------------------------------------------
# Upload + Process Media
# -------------------------------------------------------------------

@app.post("/media")
async def upload_media(file: UploadFile = File(...)):
    """
    Upload a video file.
    Immediately post-process it:
      - detect faces
      - track
      - select top 3 frames per track
      - extract embeddings
      - store in DB
    """
    media_id = str(uuid.uuid4())
    session: Session = SessionLocal()

    try:
        # Save file
        suffix = os.path.splitext(file.filename)[-1]
        saved_filename = f"{media_id}{suffix}"
        path = os.path.join(UPLOAD_DIR, saved_filename)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Insert media row
        session.add(Media(id=media_id, filename=saved_filename))
        session.commit()

        # Process video
        print(f"Starting video processing for {media_id}...")
        raw_tracks = process_video(path)
        finalized = finalize_tracks(raw_tracks)
        print(f"Finalized {len(finalized)} tracks for {media_id}")

        for track_id, samples, embeddings in finalized:
            start_ts = min(s[0] for s in samples)
            end_ts = max(s[0] for s in samples)

            track = FaceTrack(
                media_id=media_id,
                start_ts=start_ts,
                end_ts=end_ts
            )
            session.add(track)
            session.flush()  # get track.id

            print(f"Saving track {track.id} with {len(embeddings)} embeddings")
            for emb in embeddings:
                session.add(
                    FaceEmbedding(
                        track_id=track.id,
                        embedding=emb.tolist()
                    )
                )

        session.commit()
        print(f"Upload and processing complete for {media_id}. Committed to DB.")

        return {
            "media_id": media_id,
            "tracks": len(finalized)
        }

    finally:
        session.close()

# -------------------------------------------------------------------
# Search Faces Inside a Media
# -------------------------------------------------------------------

@app.post("/media/{media_id}/search")
async def search_face(
    media_id: str,
    file: UploadFile = File(...)
):
    session: Session = SessionLocal()

    try:
        img = decode_image(await file.read())
        query_emb = embed(img)

        if query_emb is None:
            raise HTTPException(400, "No face detected")

        # Use CAST(:q AS vector) instead of :q::vector
        query = text("""
            SELECT
                ft.start_ts,
                fe.embedding <=> CAST(:q AS vector) AS dist
            FROM face_embeddings fe
            JOIN face_tracks ft ON ft.id = fe.track_id
            WHERE ft.media_id = :mid
            ORDER BY dist
            LIMIT 1
        """)

        # query_emb.tolist() is correct; pgvector needs a standard list
        row = session.execute(
            query,
            {
                "q": query_emb.tolist(),
                "mid": media_id
            }
        ).fetchone()

        # Handle the result
        if row and row.dist < 0.35:
            return {
                "found": True,
                "timestamp": float(row.start_ts),
                "distance": float(row.dist)
            }

        return {
            "found": False,
            "reason": "No confident match"
        }

    except Exception as e:
        # It's good practice to log the error here
        print(f"Search Error: {e}")
        raise HTTPException(500, "Internal search error")

    finally:
        session.close()