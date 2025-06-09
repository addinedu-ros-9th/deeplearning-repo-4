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
    def __init__(self, base_dir, sequence_length=32, batch_size=16):
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.video_paths = []
        self.labels = []
        
        # Initialize YOLO model
        self.pose_model = YOLO('yolov8n-pose.pt')
        
        # Get all video directories
        video_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        for video_dir in video_dirs:
            video_folder_path = os.path.join(base_dir, video_dir)
            
            # Load normal sequences
            normal_dir = os.path.join(video_folder_path, "normal")
            if os.path.exists(normal_dir):
                for video_file in os.listdir(normal_dir):
                    if video_file.endswith('.mp4'):
                        video_path = os.path.join(normal_dir, video_file)
                        self.video_paths.append(video_path)
                        self.labels.append(0.0)  # normal
            
            # Load theft sequences
            theft_dir = os.path.join(video_folder_path, "theft")
            print(f"Checking: {theft_dir}")
            if os.path.exists(theft_dir):
                print(f"  Found theft dir: {theft_dir}")
                for video_file in os.listdir(theft_dir):
                    print(f"    Found file: {video_file}")
                    if video_file.endswith('.mp4'):
                        print(f"      MP4 file: {video_file}")
                        video_path = os.path.join(theft_dir, video_file)
                        self.video_paths.append(video_path)
                        self.labels.append(1.0)  # anomaly
    
    def _extract_joints(self, frame):
        # Resize frame for better performance
        frame = cv2.resize(frame, (640, 640))
        
        try:
            # Run YOLO inference
            results = self.pose_model(frame, verbose=False)[0]
            
            if results.keypoints is not None and len(results.keypoints) > 0:
                # Get the first person's keypoints
                keypoints = results.keypoints[0].data[0].cpu().numpy()
                # Convert to the same format as before (x, y, z, visibility)
                joints = np.zeros(17 * 4)  # Initialize with zeros
                for i, kp in enumerate(keypoints):
                    if i < 17:  # Ensure we don't exceed 17 keypoints
                        joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]  # Normalize coordinates
                return joints
            else:
                return np.zeros(17 * 4)  # YOLO-Pose uses 17 keypoints
        except Exception as e:
            print(f"Error processing frame: {e}")
            return np.zeros(17 * 4)
    
    def __getitem__(self, idx):
        video_path = self.video_paths[idx]
        label = self.labels[idx]
        
        cap = cv2.VideoCapture(video_path)
        joints_sequence = []
        frame_count = 0
        sample_interval = 5  # 5프레임마다 1개씩 추출
        
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
        
        # If sequence is too short, pad with the last frame
        if len(joints_sequence) < self.sequence_length:
            last_joints = joints_sequence[-1] if joints_sequence else np.zeros(17 * 4)
            while len(joints_sequence) < self.sequence_length:
                joints_sequence.append(last_joints)
        
        # If sequence is too long, randomly select a subsequence
        if len(joints_sequence) > self.sequence_length:
            start_idx = np.random.randint(0, len(joints_sequence) - self.sequence_length + 1)
            joints_sequence = joints_sequence[start_idx:start_idx + self.sequence_length]
        
        # Ensure all sequences have the same shape
        sequence = np.stack(joints_sequence)
        return torch.FloatTensor(sequence), torch.FloatTensor([label])
    
    def __len__(self):
        return len(self.video_paths)

class AnomalyDetector(nn.Module):
    def __init__(self, input_size=17*4, hidden_size=256, num_layers=2):  # Changed input size for YOLO-Pose
        super(AnomalyDetector, self).__init__()
        
        # LSTM for sequence learning
        self.lstm = nn.LSTM(
            input_size=input_size,  # 17 joints * 4 values (x,y,z,visibility)
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        
        # Anomaly classifier for each time step
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 512),  # *2 for bidirectional
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Process sequence using LSTM
        lstm_out, _ = self.lstm(x)  # lstm_out shape: [batch, seq_len, hidden_size*2]
        
        # Classify each time step
        anomaly_scores = self.classifier(lstm_out)  # shape: [batch, seq_len, 1]
        
        return anomaly_scores

def train_model(model, train_loader, num_epochs=20, num_normal=None, num_theft=None):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    # pos_weight 계산 (이상치에 더 큰 패널티)
    if num_normal is not None and num_theft is not None and num_theft > 0:
        pos_weight = torch.tensor([num_normal / num_theft], device=device)
        print(f"Using pos_weight for BCELoss: {pos_weight.item():.2f}")
        criterion = nn.BCELoss(pos_weight=pos_weight)
    else:
        criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3, min_lr=1e-6)
    
    best_loss = float('inf')
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        
        for sequences, labels in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}'):
            sequences = sequences.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            
            # Forward pass
            anomaly_scores = model(sequences)  # [batch, seq_len, 1]
            
            # Expand labels to match sequence length
            expanded_labels = labels.unsqueeze(1).expand(-1, sequences.size(1), -1)  # [batch, seq_len, 1]
            
            # Calculate loss
            loss = criterion(anomaly_scores, expanded_labels)
            
            # Add regularization loss
            l2_lambda = 0.01
            l2_reg = torch.tensor(0., device=device)
            for param in model.parameters():
                l2_reg += torch.norm(param)
            loss += l2_lambda * l2_reg
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches
        print(f'Epoch {epoch+1}, Loss: {avg_loss:.4f}')
        
        scheduler.step(avg_loss)
        
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), "best_anomaly_detector.pth")

if __name__ == "__main__":
    # (1) SuppressOutput 주석 처리
    # with SuppressOutput():
    #     # Initialize model
    #     model = AnomalyDetector()
    #     ...

    # Initialize model
    model = AnomalyDetector()

    # Create dataset and dataloader
    print("Loading dataset...")
    dataset = VideoDataset("extracted_videos", batch_size=8)
    print(f"Total sequences: {len(dataset)}")
    
    print(f"정상(normal) 데이터 개수: {sum([1 for l in dataset.labels if l == 0.0])}")
    print(f"이상(theft) 데이터 개수: {sum([1 for l in dataset.labels if l == 1.0])}")
    
    train_loader = DataLoader(
        dataset, 
        batch_size=8,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    
    # Train model
    print("\nTraining model...")
    train_model(model, train_loader)
    
    # Save model
    model_path = "best_anomaly_detector.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}") 