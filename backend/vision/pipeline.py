import cv2
import numpy as np
from .detector import detect_faces
from .tracker import update_tracks
from .quality import quality_score
from .embedder import embed

def process_video(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    tracks = {}
    frame_idx = 0
    
    # Adaptive sampling: skip frames if no active tracks/faces
    skip_counter = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if skip_counter > 0:
            skip_counter -= 1
            frame_idx += 1
            continue

        faces = detect_faces(frame)
        detections = []

        # Keep track of face objects (including landmarks and embeddings)
        face_map = {}
        for i, f in enumerate(faces):
            x1, y1, x2, y2 = map(int, f.bbox)
            # Detections for tracker should be [x1, y1, x2, y2, score]
            detections.append([x1, y1, x2, y2, f.det_score])
            face_map[i] = f

        # if detections:
        #     print(f"Frame {frame_idx}: detected {len(detections)} faces")

        active = update_tracks(np.array(detections)) if detections else []

        # If no faces/tracks, we can skip some frames (e.g. 0.5s)
        if not active:
            skip_counter = int(fps / 2)
        else:
            skip_counter = 0

            for t in active:
                x1, y1, x2, y2 = map(int, t.tlbr)
                # Handle potential out of bounds or negative coords
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    continue

                # Match tracker output back to insightface landmarks
                # Simple IOU or distance check between t.tlbr and face.bbox
                best_face = None
                best_iou = 0
                for i, f in face_map.items():
                    # Calculate IOU
                    fx1, fy1, fx2, fy2 = f.bbox
                    ix1 = max(x1, fx1)
                    iy1 = max(y1, fy1)
                    ix2 = min(x2, fx2)
                    iy2 = min(y2, fy2)
                    area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
                    union = (x2-x1)*(y2-y1) + (fx2-fx1)*(fy2-fy1) - area
                    iou = area / union if union > 0 else 0
                    if iou > best_iou:
                        best_iou = iou
                        best_face = f

                if best_face:
                    score = quality_score(crop, best_face.kps)
                    # Pass the embedding directly from detection
                    tracks.setdefault(t.track_id, []).append(
                        (frame_idx / fps, best_face.embedding, score)
                    )

        frame_idx += 1

    cap.release()
    print(f"Video processing finished. Tracks found: {len(tracks)}")
    return tracks

def finalize_tracks(tracks):
    """
    Select top 5 high-quality samples per track and average their embeddings.
    """
    print(f"Finalizing {len(tracks)} tracks...")
    finalized = []
    for track_id, samples in tracks.items():
        # samples is list of (ts, embedding, score)
        # Sort by quality score
        sorted_samples = sorted(samples, key=lambda x: x[2], reverse=True)
        top_samples = sorted_samples[:5]
        
        embeddings = [s[1] for s in top_samples if s[1] is not None]
        valid_samples = [(s[0], None, s[2]) for s in top_samples if s[1] is not None]
        
        if embeddings:
            # Average and normalize embeddings
            avg_emb = np.mean(embeddings, axis=0)
            norm = np.linalg.norm(avg_emb)
            if norm > 1e-6:
                avg_emb = avg_emb / norm
            
            finalized.append((track_id, valid_samples, [avg_emb]))
        else:
            print(f"Track {track_id} has no valid embeddings.")
            
    print(f"Finalized tracks: {len(finalized)}")
    return finalized