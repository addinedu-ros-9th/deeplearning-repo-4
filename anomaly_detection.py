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
    
    def __init__(self, base_dir='E:/mldl/실제영상', sequence_length=15, batch_size=64):
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.video_paths = []
        self.labels = []
        self.pose_model = YOLO('yolov8n-pose.pt')
        
        # Define specific video mappings
        video_mappings = {
            '정상1.mp4': 0,  # normal
            '정상2.mp4': 0,  # normal
            '절도1.mp4': 1,  # theft
            '절도2.mp4': 1,  # theft
            '유기1.mp4': 2,  # abandon
            '유기2.mp4': 2,  # abandon
            '파손1.mp4': 3,  # broken
            '파손2.mp4': 3   # broken
            }
        
        # Add only the specified videos
        for video_name, label in video_mappings.items():
            video_path = os.path.join(base_dir, video_name)
            if os.path.exists(video_path):
                self.video_paths.append(video_path)
                self.labels.append(label)
            else:
                print(f"Warning: Video file not found: {video_path}")
    
    def _extract_joints(self, frame):
        # Remove resizing, use original frame
        try:
            results = self.pose_model(frame, verbose=False)[0]
            if results.keypoints is not None and len(results.keypoints) > 0:
                keypoints = results.keypoints[0].data[0].cpu().numpy()
                joints = np.zeros(17 * 4)
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
        video_path = self.video_paths[idx]
        label = self.labels[idx]
        cap = cv2.VideoCapture(video_path)
        joints_sequence = []
        frame_count = 0
        sample_interval = 1
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % sample_interval == 0:
                    joints = self._extract_joints(frame)
                    joints_sequence.append(joints)
                frame_count += 1
        finally:
            cap.release()
        if len(joints_sequence) < self.sequence_length:
            last_joints = joints_sequence[-1] if joints_sequence else np.zeros(17 * 4)
            while len(joints_sequence) < self.sequence_length:
                joints_sequence.append(last_joints)
        if len(joints_sequence) > self.sequence_length:
            start_idx = np.random.randint(0, len(joints_sequence) - self.sequence_length + 1)
            joints_sequence = joints_sequence[start_idx:start_idx + self.sequence_length]
        sequence = np.stack(joints_sequence)
        return torch.FloatTensor(sequence), torch.LongTensor([label])
    
    def __len__(self):
        return len(self.video_paths)

class AnomalyDetector(nn.Module):
    def __init__(self, input_size=17*4, hidden_size=512, num_layers=3, num_classes=4):
        super(AnomalyDetector, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
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
            logits = model(sequences)  # [batch, seq_len, num_classes]
            # Use only the last time step for classification
            logits_last = logits[:, -1, :]  # [batch, num_classes]
            labels_flat = labels.view(-1)   # [batch]
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
        else:
            counter += 1
        if counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break
        torch.save(model.state_dict(), "best_anomaly_detector.pth")

if __name__ == "__main__":
    model = AnomalyDetector(num_classes=4)
    print("Loading dataset...")
    # Use absolute path
    base_dir = "E:/mldl/실제영상"
    dataset = VideoDataset(base_dir=base_dir, batch_size=64)
    print(f"Total sequences: {len(dataset)}")
    label_names = ['normal', 'theft', 'abandon', 'broken']
    label_counts = Counter(dataset.labels)
    for i, name in enumerate(label_names):
        print(f"{name} 데이터 개수: {label_counts[i]}")
    train_loader = DataLoader(
        dataset, 
        batch_size=8,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    print("\nTraining model...")
    train_model(model, train_loader)
    model_path = "actual_anomaly_detector.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}") 