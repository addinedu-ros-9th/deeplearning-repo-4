# 키포인트 관련 유틸리티 함수

import xml.etree.ElementTree as ET
import numpy as np
import torch
from sklearn.utils.class_weight import compute_class_weight

KEYPOINT_ORDER = [
    'Pelvis', 'Left hip', 'Left knee', 'Left foot',
    'Right  hip', 'Right knee', 'Right foot',
    'Spine naval', 'Spine chest', 'Neck base', 'Center head',
    'Right shoulder', 'Right elbow', 'Right hand',
    'Left shoulder', 'Left elbow', 'Left hand'
]

ACTION_LABELS = {
    'normal': 0,
    'theft': 1,
    'broken': 2,
    'abandon': 3
}

ACTIONS = ['abandon', 'broken', 'theft', 'normal']
SPLITS = ['train', 'val']
NUM_KEYPOINTS = 17

LABELS = ACTION_LABELS
NUM_CLASSES = len(LABELS)
INV_LABELS = {v: k for k, v in LABELS.items()}

# XML에서 관절점, id, 프레임별로 추출

def parse_xml_keypoints(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # 관절점별 track을 모두 모음
    tracks = root.findall('track')
    # 관절점별로 {label: [track]} 구조
    kp_tracks = {}
    for tr in tracks:
        label = tr.attrib['label']
        if label not in kp_tracks:
            kp_tracks[label] = []
        kp_tracks[label].append(tr)
    return kp_tracks

def get_action_frames(xml_path, action):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    action_frames = []
    
    # 모든 track을 순회하면서 action_start와 action_end 찾기
    start_frames = []
    end_frames = []
    
    for tr in root.findall('track'):
        if tr.attrib['label'] == f'{action}_start':
            for box in tr.findall('box'):
                start_frames.append(int(box.attrib['frame']))
        elif tr.attrib['label'] == f'{action}_end':
            for box in tr.findall('box'):
                end_frames.append(int(box.attrib['frame']))
    
    # start와 end 프레임을 정렬하고 매칭
    start_frames.sort()
    end_frames.sort()
    
    for start, end in zip(start_frames, end_frames):
        action_frames.append((start, end))
    
    return action_frames

def get_class_weights(labels):
    class_weights = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES), y=labels)
    return torch.tensor(class_weights, dtype=torch.float32)