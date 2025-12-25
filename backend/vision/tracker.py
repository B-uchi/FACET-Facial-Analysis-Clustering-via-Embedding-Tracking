from yolox.tracker.byte_tracker import BYTETracker
import numpy as np

class TrackerArgs:
    def __init__(self, track_thresh, track_buffer, match_thresh):
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.mot20 = False

args = TrackerArgs(
    track_thresh=0.5, 
    track_buffer=30, 
    match_thresh=0.8
)

tracker = BYTETracker(args, frame_rate=30)

def update_tracks(detections):
    if len(detections) == 0:
        return []
        
    detections_np = np.array(detections)
    return tracker.update(detections_np, [640, 640], [640, 640])
