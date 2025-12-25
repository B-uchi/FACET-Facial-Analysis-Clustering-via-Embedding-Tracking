# FACET Backend Engine

The FACET backend is a high-performance FastAPI server responsible for video processing, face tracking, quality-aware identity extraction, and vector-based search.

## 🧠 Vision Pipeline

The core of FACET is a multi-stage vision pipeline that transforms raw video into searchable identity vectors.

1.  **Adaptive Sampler (`sampler.py`)**: Optimizes throughput by dynamically adjusting the frame rate. It skips frames when no activity is detected and increases density during face detection events.
2.  **Face Detector (`detector.py`)**: Uses InsightFace (Buffalo_L) to detect face landmarks and bounding boxes with high precision.
3.  **Identity Tracker (`tracker.py`)**: Implements **ByteTrack** to maintain consistent IDs across frames, even through temporary occlusions or motion blur.
4.  **Quality Scorer (`quality.py`)**: Analyzes head pose (Yaw, Pitch, Roll), sharpness, and face size to select the "best" representative frames for each track.
5.  **Face Embedder (`embedder.py`)**: Generates 512-dimensional feature vectors using **ArcFace**.

## 🔌 API Documentation

The backend exposes a RESTful API for media management and biometric search.

### Media Management
- `GET /media`: List all processed media.
- `POST /media`: Upload a new video file. This triggers the background vision pipeline.
- `GET /media/{id}`: Get metadata for a specific media file.

### Search & Analytics
- `POST /media/{id}/search`: Search for a specific person within a video by uploading a reference image.
- `GET /health`: System health status.
- `GET /metrics`: Prometheus-compatible metrics for monitoring pipeline performance.

## 🗄️ Database Schema

Powered by **PostgreSQL** and **pgvector** for lightning-fast similarity lookups.

- **`media`**: Stores metadata about uploaded video files.
- **`face_tracks`**: Represents a unique identity appearing over a specific time range in a video.
- **`face_embeddings`**: Stores the 512-D vectors associated with specific tracks. Indexed with **IVFFlat** for sub-millisecond retrieval.

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL with `pgvector` extension

### Installation
1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure Environment:
    ```bash
    export DATABASE_URL="postgresql://user:pass@localhost:5432/facet"
    ```
4.  Run the server:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
