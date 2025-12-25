def sampling_fps(active_tracks, motion_level):
    if active_tracks == 0:
        return 1
    if motion_level < 0.2:
        return 3
    return 6
