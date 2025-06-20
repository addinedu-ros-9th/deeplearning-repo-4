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
    
    def __init__(self, base_dir='E:/mldl/편집영상', sequence_length=15, batch_size=64):
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.sequences = []  # 모든 시퀀스를 미리 추출하여 저장
        
        # YOLO 모델은 메인 프로세스에서만 생성
        with SuppressOutput():
            pose_model = YOLO('yolov8n-pose.pt')
        
        # 각 레이블 디렉토리에서 비디오 파일 로드
        for label_name, label in self.LABEL_MAP.items():
            label_dir = os.path.join(base_dir, label_name.lower())
            if not os.path.exists(label_dir):
                print(f"Warning: Directory not found: {label_dir}")
                continue
            
            # 해당 디렉토리의 모든 mp4 파일 처리
            for video_name in os.listdir(label_dir):
                if video_name.endswith('.mp4'):
                    video_path = os.path.join(label_dir, video_name)
                    print(f"Processing {video_path}...")
                    
                    # 비디오에서 관절 시퀀스 추출
                    cap = cv2.VideoCapture(video_path)
                    joints_sequence = []
                    frame_count = 0
                    sample_interval = 1
                    
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        if frame_count % sample_interval == 0:
                            try:
                                results = pose_model(frame, verbose=False)[0]
                                if results.keypoints is not None and len(results.keypoints) > 0:
                                    keypoints = results.keypoints[0].data[0].cpu().numpy()
                                    joints = np.zeros(17 * 4)
                                    # 실시간과 동일한 정규화 방식 사용 (256으로 나누기)
                                    for i, kp in enumerate(keypoints):
                                        if i < 17:
                                            joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
                                else:
                                    joints = np.zeros(17 * 4)
                            except Exception as e:
                                print(f"Error processing frame: {e}")
                                joints = np.zeros(17 * 4)
                            joints_sequence.append(joints)
                        frame_count += 1
                    cap.release()
                    
                    # 시퀀스 길이가 충분한 경우에만 처리
                    if len(joints_sequence) >= sequence_length:
                        # 슬라이딩 윈도우로 시퀀스 추출 (50% 오버랩)
                        stride = sequence_length // 2
                        for start in range(0, len(joints_sequence) - sequence_length + 1, stride):
                            seq = joints_sequence[start:start + sequence_length]
                            # 더 관대한 필터링 조건
                            valid_frames = sum([not np.all(j==0) for j in seq])
                            if valid_frames >= sequence_length * 0.5:  # 50% 이상 유효한 프레임
                                self.sequences.append((np.stack(seq), label))
        
        print(f"Total sequences extracted: {len(self.sequences)}")
        
        # 메모리 정리
        del pose_model
        torch.cuda.empty_cache()
    
    def __getitem__(self, idx):
        sequence, label = self.sequences[idx]
        return torch.FloatTensor(sequence), torch.LongTensor([label])
        
    def __len__(self):
        return len(self.sequences)

class AnomalyDetector(nn.Module):
    def __init__(self, input_size=17*4, hidden_size=512, num_layers=3, num_classes=4):
        super(AnomalyDetector, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.3  # dropout 감소
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 1024),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        logits = self.classifier(lstm_out)
        return logits  # shape: [batch, seq_len, num_classes]

def train_model(model, train_loader, num_epochs=50):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    
    # Learning rate 증가
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    
    # Learning rate scheduler 조정
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='min', 
        factor=0.5,
        patience=3,
        min_lr=1e-6
    )
    
    best_loss = float('inf')
    patience = 8
    counter = 0
    best_epoch = 0
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        num_batches = 0
        
        # 진행바에 loss 표시
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
        for sequences, labels in pbar:
            sequences = sequences.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            logits = model(sequences)
            logits_last = logits[:, -1, :]
            labels_flat = labels.view(-1)
            
            # 기본 Cross Entropy Loss
            loss = criterion(logits_last, labels_flat)
            
            # L2 정규화 감소
            l2_lambda = 0.0001
            l2_reg = torch.tensor(0., device=device)
            for param in model.parameters():
                l2_reg += torch.norm(param)
            loss += l2_lambda * l2_reg
            
            loss.backward()
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            # 정확도 계산
            pred = logits_last.argmax(dim=1)
            correct += (pred == labels_flat).sum().item()
            total += labels_flat.size(0)
            
            total_loss += loss.item()
            num_batches += 1
            
            # 진행바에 현재 loss와 정확도 표시
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.0 * correct / total:.2f}%'
            })
        
        avg_loss = total_loss / num_batches
        accuracy = 100.0 * correct / total
        
        print(f'Epoch {epoch+1}:')
        print(f'  Average Loss: {avg_loss:.4f}')
        print(f'  Accuracy: {accuracy:.2f}%')
        
        scheduler.step(avg_loss)
        
        # 최고 성능 모델 저장
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_epoch = epoch
            counter = 0
            print(f'  New best model saved! (loss: {best_loss:.4f})')
            torch.save(model.state_dict(), "best_anomaly_detector.pth")
        else:
            counter += 1
            
        if counter >= patience:
            print(f"\nEarly stopping at epoch {epoch+1}")
            print(f"Best model was from epoch {best_epoch+1} with loss {best_loss:.4f}")
            break

if __name__ == "__main__":
    model = AnomalyDetector(num_classes=4)
    print("Loading dataset...")
    # Linux 경로로 수정
    base_dir = "E:/mldl/편집영상"
    dataset = VideoDataset(base_dir=base_dir, batch_size=64)
    print(f"Total sequences: {len(dataset)}")
    label_names = ['normal', 'theft', 'abandon', 'broken']
    # 시퀀스의 레이블만 추출하여 카운트
    label_counts = Counter([label for _, label in dataset.sequences])
    for i, name in enumerate(label_names):
        print(f"{name} 데이터 개수: {label_counts[i]}")
    train_loader = DataLoader(
        dataset, 
        batch_size=16,  # 배치 사이즈 감소
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    print("\nTraining model...")
    train_model(model, train_loader)
    model_path = "actual_anomaly_detector.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")  