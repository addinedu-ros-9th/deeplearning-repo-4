# LSTM 모델 모듈

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from utils.config import KEYPOINT_ORDER, NUM_KEYPOINTS
from utils.keypoint_utils import LABELS, get_class_weights
from sklearn.metrics import f1_score
from tqdm import tqdm
import random
import glob
import os

PELVIS_IDX = 0
NECK_IDX = 9

def process_features(kps_seq):
    """
    키포인트 시퀀스에 대해 정규화 및 동적 특징(속도)을 계산합니다.
    Feature: (num_frames, 17, 3) -> (x, y, conf)
    Output: (num_frames, 17 * 4) -> (norm_x, norm_y, vel_x, vel_y) for each keypoint
    """
    # 1. 정규화
    pelvis = kps_seq[:, PELVIS_IDX, :2].reshape(-1, 1, 2)
    neck = kps_seq[:, NECK_IDX, :2].reshape(-1, 1, 2)
    
    # 척추 길이를 기준으로 스케일링
    spine_length = np.linalg.norm(pelvis - neck, axis=2)
    spine_length[spine_length == 0] = 1e-6 # 0으로 나누는 것 방지
    
    # 골반을 원점으로 이동
    relative_kps = kps_seq[:, :, :2] - pelvis
    # 척추 길이로 정규화
    normalized_kps = relative_kps / spine_length[..., np.newaxis]

    # 2. 동적 특징 (속도)
    # 마지막 프레임을 복제하여 길이를 맞춤
    padded_kps = np.pad(normalized_kps, ((0, 1), (0, 0), (0, 0)), mode='edge')
    velocity = padded_kps[1:] - padded_kps[:-1]
    
    # 3. 특징 결합 (normalized_kps, velocity)
    # (num_frames, num_keypoints, 2), (num_frames, num_keypoints, 2)
    # -> (num_frames, num_keypoints, 4)
    dynamic_features = np.concatenate([normalized_kps, velocity], axis=-1)
    
    # (num_frames, 17 * 4) 형태로 flatten
    return dynamic_features.reshape(len(kps_seq), -1)


class KeypointSequenceDataset(Dataset):
    def __init__(self, feature_root, split, seq_len=120, normal_ratio=2, seed=42):
        self.samples = []
        self.labels = []
        self.seq_len = seq_len
        random.seed(seed)
        np.random.seed(seed)
        
        all_files = []
        # 비정상 샘플 수 세기
        abnormal_count = 0
        for label_name, label_idx in LABELS.items():
            if label_name == 'normal': continue
            npy_files = glob.glob(os.path.join(feature_root, label_name, split, '*.npy'))
            abnormal_count += len(npy_files)
            for file_path in npy_files:
                all_files.append((file_path, label_idx))
                
        # 정상 샘플 undersampling
        normal_files = glob.glob(os.path.join(feature_root, 'normal', split, '*.npy'))
        normal_count = min(len(normal_files), abnormal_count * normal_ratio)
        normal_files_sampled = random.sample(normal_files, normal_count)
        for file_path in normal_files_sampled:
            all_files.append((file_path, LABELS['normal']))
            
        random.shuffle(all_files)

        print(f"Processing {split} data...")
        for npy_path, label_idx in tqdm(all_files):
            arr = np.load(npy_path)
            kps_raw = arr[:, 1:]
            
            # (num_frames, 51) -> (num_frames, 17, 3)
            kps_seq = kps_raw.reshape(len(kps_raw), -1, 3)

            # 특징 처리 (정규화 + 동적 특징)
            features = process_features(kps_seq)

            if len(features) < seq_len:
                pad = np.zeros((seq_len - len(features), features.shape[1]))
                features = np.concatenate([features, pad], axis=0)
            else:
                features = features[:seq_len]
            
            self.samples.append(features)
            self.labels.append(label_idx)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        kps = self.samples[idx]
        label = self.labels[idx]
        return torch.tensor(kps, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

class AdvancedLSTMClassifier(nn.Module):
    # 입력 차원이 17*4 = 68로 변경됨
    def __init__(self, input_dim=68, hidden_dim=512, num_layers=4, num_classes=4, dropout=0.5, bidirectional=True):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=dropout, bidirectional=bidirectional)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * (2 if bidirectional else 1), 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.dropout(out)
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def evaluate(model, loader, device):
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for X, y in loader:
            X, y = X.to(device), y.to(device)
            logits = model(X)
            preds = torch.argmax(logits, dim=1)
            y_true.extend(y.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
    acc = np.mean(np.array(y_true) == np.array(y_pred))
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    return acc, f1, y_true, y_pred