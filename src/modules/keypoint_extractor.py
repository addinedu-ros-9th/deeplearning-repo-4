# 키포인트 추출 모듈

import numpy as np
from utils.config import KEYPOINT_ORDER, NUM_KEYPOINTS

def extract_keypoints_all(kp_tracks):
    frame_dict = {}
    for kp_name, tracks in kp_tracks.items():
        for track in tracks:
            for points in track.findall('points'):
                frame = int(points.attrib['frame'])
                xy = points.attrib['points'].split(',')
                x, y = float(xy[0]), float(xy[1])
                if frame not in frame_dict:
                    frame_dict[frame] = [0.0] * (NUM_KEYPOINTS * 3)
                kp_idx = KEYPOINT_ORDER.index(kp_name)
                frame_dict[frame][kp_idx*3] = x
                frame_dict[frame][kp_idx*3+1] = y
                frame_dict[frame][kp_idx*3+2] = 1.0
                
    # 프레임 번호 순 정렬
    frames = []
    for f in sorted(frame_dict.keys()):
        frames.append([f] + frame_dict[f])
    return np.array(frames)