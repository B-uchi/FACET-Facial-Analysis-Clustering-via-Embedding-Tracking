import cv2
import numpy as np

def quality_score(face, landmarks):
    """
    Calculate a quality score based on blur, size, and pose.
    Favors frontal, sharp, and large faces.
    """
    if face.size == 0 or landmarks is None:
        return 0.0

    # 1. Sharpness (Laplacian variance)
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 2. Size (Normalize by a baseline of 112x112)
    h, w = face.shape[:2]
    size_score = (h * w) / (112 * 112)
    
    # 3. Pose (Yaw/Pitch approximation from 5-point landmarks)
    # Landmarks: [left_eye, right_eye, nose, left_mouth, right_mouth]
    eye_dist = np.linalg.norm(landmarks[0] - landmarks[1])
    nose = landmarks[2]
    eye_mid = (landmarks[0] + landmarks[1]) / 2.0
    
    # Vertical symmetry (Pitch approximation)
    # distance from nose to eyes vs nose to mouth
    mouth_mid = (landmarks[3] + landmarks[4]) / 2.0
    vert_ratio = np.linalg.norm(nose - eye_mid) / (np.linalg.norm(nose - mouth_mid) + 1e-6)
    pitch_score = 1.0 - abs(vert_ratio - 1.0) # Assume 1.0 is neutral
    
    # Horizontal symmetry (Yaw approximation)
    # distance from nose to left eye vs node to right eye
    dist_l = np.linalg.norm(nose - landmarks[0])
    dist_r = np.linalg.norm(nose - landmarks[1])
    yaw_ratio = dist_l / (dist_r + 1e-6)
    yaw_score = 1.0 - abs(yaw_ratio - 1.0)
    
    pose_score = (pitch_score + yaw_score) / 2.0

    # Weights: Focus heavily on pose and sharpness
    final_score = (blur * 0.4) + (size_score * 0.1) + (pose_score * 0.5 * 500) # multiplier to scale pose
    
    return float(final_score)
