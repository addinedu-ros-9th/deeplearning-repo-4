import os
import glob
import numpy as np
from tqdm import tqdm
from utils.keypoint_utils import ACTIONS, SPLITS, parse_xml_keypoints, get_action_frames, NUM_KEYPOINTS
from modules.keypoint_extractor import extract_keypoints_all

DATA_ROOT = '/home/ckim/dev_ws/project_ws/mldl_project/data/videos'
FEATURE_ROOT = '/home/ckim/dev_ws/project_ws/mldl_project/data/features'

def main():
    # 모든 행동/분할에 대해 처리
    for action in ACTIONS:
        for split in SPLITS:
            label_dir = os.path.join(DATA_ROOT, action, split, 'label')
            if not os.path.exists(label_dir):
                continue
            feature_dir = os.path.join(FEATURE_ROOT, action, split)
            os.makedirs(feature_dir, exist_ok=True)
            xml_files = glob.glob(os.path.join(label_dir, '*.xml'))
            for xml_path in tqdm(xml_files, desc=f'{action}/{split}'):
                base = os.path.splitext(os.path.basename(xml_path))[0]
                
                # 'normal' 클래스는 전체 프레임 저장
                if action == 'normal':
                    kp_tracks = parse_xml_keypoints(xml_path)
                    keypoints = extract_keypoints_all(kp_tracks)
                    if keypoints.size == 0:
                        continue
                    # [frame_id, keypoints ...] 형태로 저장
                    arr = np.zeros((keypoints.shape[0], 1 + NUM_KEYPOINTS*3))
                    arr[:, 0] = keypoints[:, 0]  # 프레임 번호
                    arr[:, 1:] = keypoints[:, 1:]
                    np.save(os.path.join(feature_dir, f'{base}.npy'), arr)
                else:
                    # 다른 액션들은 행동 구간만 추출하여 저장
                    action_frames = get_action_frames(xml_path, action)
                    if not action_frames:
                        continue
                        
                    kp_tracks = parse_xml_keypoints(xml_path)
                    all_keypoints = extract_keypoints_all(kp_tracks)
                    if all_keypoints.size == 0:
                        continue

                    for i, (start_frame, end_frame) in enumerate(action_frames):
                        # 해당 액션 구간에 포함되는 프레임만 필터링
                        action_keypoints = all_keypoints[
                            (all_keypoints[:, 0] >= start_frame) & (all_keypoints[:, 0] <= end_frame)
                        ]
                        
                        if action_keypoints.size == 0:
                            continue
                        
                        # [frame_id, keypoints ...] 형태로 저장
                        arr = np.zeros((action_keypoints.shape[0], 1 + NUM_KEYPOINTS*3))
                        arr[:, 0] = action_keypoints[:, 0]  # 프레임 번호
                        arr[:, 1:] = action_keypoints[:, 1:]
                        
                        # 동일 영상에 여러 액션이 있을 경우 _0, _1, ... 와 같이 저장
                        np.save(os.path.join(feature_dir, f'{base}_{action}_{i}.npy'), arr)


if __name__ == '__main__':
    main()