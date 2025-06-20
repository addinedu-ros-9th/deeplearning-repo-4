import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
from ultralytics import YOLO
import logging
import warnings
import sys
from collections import Counter
import random

# Completely suppress all output
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

# Suppress all warnings and logging
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)
for logger_name in ['mediapipe', 'tensorflow', 'absl']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

class VideoDataset(Dataset):
    LABEL_MAP = {
        'normal': 0,
        'theft': 1,
        'abandon': 2,
        'broken': 3
    }
    
    def __init__(self, base_dir='E:/mldl/편집영상', sequence_length=15, stride=1):
        self.sequence_length = sequence_length
        self.stride = stride
        self.samples = []  # (sequence, label) 쌍의 리스트
        
        # YOLO 모델은 메인 프로세스에서만 생성
        with SuppressOutput():
            pose_model = YOLO('yolov8n-pose.pt')
        
        # 각 레이블 디렉토리에서 비디오 파일 로드
        for label_name, label in self.LABEL_MAP.items():
            label_dir = os.path.join(base_dir, label_name)
            if not os.path.isdir(label_dir):
                print(f"Warning: Directory not found: {label_dir}")
                continue
            
            # 해당 디렉토리의 모든 mp4 파일 처리
            for fname in os.listdir(label_dir):
                if not (fname.endswith('.mp4') and fname.startswith(label_name)):
                    continue
                video_path = os.path.join(label_dir, fname)
                print(f"Processing {video_path}...")
                
                # 비디오에서 관절 시퀀스 추출
                cap = cv2.VideoCapture(video_path)
                joints_sequence = []
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    joints = self._extract_joints(frame, pose_model)
                    joints_sequence.append(joints)
                cap.release()
                
                # 시퀀스 길이가 충분한 경우에만 처리
                if len(joints_sequence) >= sequence_length:
                    # 슬라이딩 윈도우로 시퀀스 추출 (stride=1)
                    for start in range(0, len(joints_sequence) - sequence_length + 1, stride):
                        seq = joints_sequence[start:start + sequence_length]
                        # 유효한 관절 데이터가 70% 이상인 시퀀스만 사용
                        if np.mean([np.all(j==0) for j in seq]) < 0.3:
                            self.samples.append((np.stack(seq), label))
        
        print(f"Total sequences extracted: {len(self.samples)}")
        
        # 메모리 정리
        del pose_model
        torch.cuda.empty_cache()
    
    def _extract_joints(self, frame, pose_model):
        """프레임에서 관절점 추출"""
        try:
            results = pose_model(frame, verbose=False)[0]
            if results.keypoints is not None and len(results.keypoints) > 0:
                keypoints = results.keypoints[0].data[0].cpu().numpy()
                joints = np.zeros(17 * 4)
                # 실시간과 동일한 정규화 방식 사용 (256으로 나누기)
                for i, kp in enumerate(keypoints):
                    if i < 17:
                        joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
                return joints
            else:
                return np.zeros(17 * 4)
        except Exception as e:
            print(f"Error processing frame: {e}")
            return np.zeros(17 * 4)
    
    def __getitem__(self, idx):
        sequence, label = self.samples[idx]
        return torch.FloatTensor(sequence), torch.LongTensor([label])
        
    def __len__(self):
        return len(self.samples)

class AnomalyDetector(nn.Module):
    def __init__(self, input_size=17*4, hidden_size=256, num_layers=2, num_classes=4):
        super(AnomalyDetector, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        logits = self.classifier(lstm_out)
        return logits  # shape: [batch, seq_len, num_classes]

def train_model(model, train_loader, num_epochs=50):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3, min_lr=1e-6)
    best_loss = float('inf')
    patience = 5
    counter = 0
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        for sequences, labels in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}'):
            sequences = sequences.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            logits = model(sequences)
            logits_last = logits[:, -1, :]
            labels_flat = labels.view(-1)
            loss = criterion(logits_last, labels_flat)
            l2_lambda = 0.01
            l2_reg = torch.tensor(0., device=device)
            for param in model.parameters():
                l2_reg += torch.norm(param)
            loss += l2_lambda * l2_reg
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item()
            num_batches += 1
        avg_loss = total_loss / num_batches
        print(f'Epoch {epoch+1}, Loss: {avg_loss:.4f}')
        scheduler.step(avg_loss)
        if avg_loss < best_loss:
            best_loss = avg_loss
            counter = 0
            torch.save(model.state_dict(), "best_anomaly_detector.pth")
        else:
            counter += 1
        if counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

if __name__ == "__main__":
    model = AnomalyDetector(num_classes=4)
    print("Loading dataset...")
    base_dir = "E:/mldl/편집영상"
    dataset = VideoDataset(base_dir=base_dir, stride=1)
    print(f"Total sequences: {len(dataset)}")
    label_names = ['normal', 'theft', 'abandon', 'broken']
    label_counts = Counter([label for _, label in dataset.samples])
    for i, name in enumerate(label_names):
        print(f"{name} 데이터 개수: {label_counts[i]}")
    
    train_loader = DataLoader(
        dataset, 
        batch_size=16,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    
    print("\nTraining model...")
    train_model(model, train_loader)
    model_path = "actual_anomaly_detector.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}") 