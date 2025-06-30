import torch
import torch.nn as nn
import torch.nn.functional as F
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

# Define the spatial configuration of human joints
# COCO format keypoint connections
HUMAN_EDGES = [
    (0, 1),   # nose - left_eye
    (0, 2),   # nose - right_eye
    (1, 3),   # left_eye - left_ear
    (2, 4),   # right_eye - right_ear
    (5, 6),   # left_shoulder - right_shoulder
    (5, 7),   # left_shoulder - left_elbow
    (6, 8),   # right_shoulder - right_elbow
    (7, 9),   # left_elbow - left_wrist
    (8, 10),  # right_elbow - right_wrist
    (5, 11),  # left_shoulder - left_hip
    (6, 12),  # right_shoulder - right_hip
    (11, 12), # left_hip - right_hip
    (11, 13), # left_hip - left_knee
    (12, 14), # right_hip - right_knee
    (13, 15), # left_knee - left_ankle
    (14, 16)  # right_knee - right_ankle
]

class GraphConvolution(nn.Module):
    def __init__(self, in_channels, out_channels, A):
        super(GraphConvolution, self).__init__()
        self.A = A
        self.num_subset = 3
        
        self.conv_d = nn.ModuleList()
        for i in range(self.num_subset):
            self.conv_d.append(nn.Conv2d(in_channels, out_channels, 1))

        if in_channels != out_channels:
            self.down = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.down = lambda x: x

        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def forward(self, x):
        N, C, T, V = x.size()
        A = self.A.cuda(x.get_device()) if x.is_cuda else self.A

        y = None
        for i in range(self.num_subset):
            A1 = A[i]
            A2 = x.view(N, C * T, V)
            z = self.conv_d[i](torch.matmul(A2, A1).view(N, C, T, V))
            y = z + y if y is not None else z

        y = self.bn(y)
        y += self.down(x)
        return self.relu(y)

class TemporalConvolution(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=9, stride=1):
        super(TemporalConvolution, self).__init__()
        pad = int((kernel_size - 1) / 2)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=(kernel_size, 1), padding=(pad, 0), stride=(stride, 1))
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x

class STGCNBlock(nn.Module):
    def __init__(self, in_channels, out_channels, A, stride=1, residual=True):
        super(STGCNBlock, self).__init__()
        
        self.gcn = GraphConvolution(in_channels, out_channels, A)
        self.tcn = TemporalConvolution(out_channels, out_channels, stride=stride)
        self.relu = nn.ReLU(inplace=True)
        
        if not residual:
            self.residual = lambda x: 0
        elif (in_channels == out_channels) and (stride == 1):
            self.residual = lambda x: x
        else:
            self.residual = TemporalConvolution(in_channels, out_channels, kernel_size=1, stride=stride)

    def forward(self, x):
        res = self.residual(x)
        x = self.gcn(x)
        x = self.tcn(x)
        return self.relu(x + res)

class VideoDataset(Dataset):
    LABEL_MAP = {
        'normal': 0,
        'theft': 1,
        'abandon': 2,
        'broken': 3
    }
    
    def __init__(self, base_dir='E:/mldl/편집영상', sequence_length=15):
        self.sequence_length = sequence_length
        self.sequences = []
        
        # YOLO 모델은 메인 프로세스에서만 생성
        with SuppressOutput():
            pose_model = YOLO('yolov8n-pose.pt')
        
        # tqdm으로 진행상황 표시
        label_dirs = [(label_name, label) for label_name, label in self.LABEL_MAP.items()]
        for label_name, label in tqdm(label_dirs, desc="Processing labels"):
            label_dir = os.path.join(base_dir, label_name.lower())
            if not os.path.exists(label_dir):
                print(f"Warning: Directory not found: {label_dir}")
                continue
            
            video_files = [f for f in os.listdir(label_dir) if f.endswith('.mp4')]
            for video_name in tqdm(video_files, desc=f"Processing {label_name} videos", leave=False):
                video_path = os.path.join(label_dir, video_name)
                
                try:
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        print(f"Warning: Could not open video: {video_path}")
                        continue
                        
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    joints_sequence = []
                    frame_count = 0
                    sample_interval = 1
                    
                    # 프레임 처리를 위한 내부 tqdm
                    with tqdm(total=total_frames, desc="Processing frames", leave=False) as pbar:
                        while frame_count < total_frames:
                            ret, frame = cap.read()
                            if not ret:
                                break
                                
                            if frame_count % sample_interval == 0:
                                try:
                                    results = pose_model(frame, verbose=False)[0]
                                    if results.keypoints is not None and len(results.keypoints) > 0:
                                        keypoints = results.keypoints[0].data[0].cpu().numpy()
                                        joints = np.zeros(17 * 4)
                                        for i, kp in enumerate(keypoints):
                                            if i < 17:
                                                joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
                                    else:
                                        joints = np.zeros(17 * 4)
                                except Exception as e:
                                    print(f"Error processing frame in {video_path}: {e}")
                                    joints = np.zeros(17 * 4)
                                joints_sequence.append(joints)
                            
                            frame_count += 1
                            pbar.update(1)
                            
                    cap.release()
                    
                    # 시퀀스 추출 최적화
                    if len(joints_sequence) >= sequence_length:
                        stride = 1  # 1프레임씩 이동하면서 시퀀스 추출
                        for start in range(0, len(joints_sequence) - sequence_length + 1, stride):
                            seq = joints_sequence[start:start + sequence_length]
                            # confidence 값을 이용한 더 정확한 필터링
                            conf_scores = [np.mean([j[i*4+3] for i in range(17)]) for j in seq]
                            valid_frames = sum([score > 0.3 for score in conf_scores])
                            
                            if valid_frames >= sequence_length * 0.5:
                                self.sequences.append((np.stack(seq), label))
                                
                except Exception as e:
                    print(f"Error processing video {video_path}: {e}")
                    continue
                
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
    def __init__(self, num_classes=4, in_channels=2, graph_args=None):
        super(AnomalyDetector, self).__init__()

        # Initialize adjacency matrix
        self.graph = self._get_adjacency_matrix()
        self.register_buffer('A', torch.FloatTensor(self.graph))  # GPU 메모리에 고정
        
        # Network architecture
        self.data_bn = nn.BatchNorm1d(in_channels * 17)
        
        # ST-GCN layers with residual connections
        self.st_gcn_networks = nn.ModuleList((
            STGCNBlock(in_channels, 64, self.A, residual=False),
            STGCNBlock(64, 64, self.A),
            STGCNBlock(64, 64, self.A),
            STGCNBlock(64, 128, self.A, stride=2),
            STGCNBlock(128, 128, self.A),
            STGCNBlock(128, 128, self.A),
            STGCNBlock(128, 256, self.A, stride=2),
            STGCNBlock(256, 256, self.A),
            STGCNBlock(256, 256, self.A),
        ))

        # Classification head with dropout
        self.dropout = nn.Dropout(0.5)
        self.fcn = nn.Conv2d(256, num_classes, kernel_size=1)

    def _get_adjacency_matrix(self):
        # Convert edge list to adjacency matrix
        num_nodes = 17  # number of joints
        A = np.zeros((3, num_nodes, num_nodes))
        
        # Self connections
        A[0] = np.eye(num_nodes)
        
        # Spatial connections
        for i, j in HUMAN_EDGES:
            A[1, i, j] = 1
            A[1, j, i] = 1
            
        # Second-order connections
        A[2] = np.matmul(A[1], A[1])
        
        # Normalize adjacency matrices
        for i in range(3):
            D = np.sum(A[i], axis=0)
            D = np.where(D > 0, np.power(D, -0.5), 0)
            D = np.diag(D)
            A[i] = np.matmul(np.matmul(D, A[i]), D)
            
        return torch.FloatTensor(A)

    def forward(self, x):
        # Input x shape: [N, T, V*4]
        N = x.size(0)
        T = x.size(1)
        
        # Reshape and get confidence mask
        x = x.view(N, T, 17, 4)
        conf = x[:, :, :, 3]
        mask = (conf > 0.3).float().unsqueeze(-1)
        
        # Get x, y coordinates and apply confidence mask
        coords = x[:, :, :, :2] * mask
        
        # Permute and normalize
        x = coords.permute(0, 3, 1, 2).contiguous()
        x = x.view(N, -1, T)
        x = self.data_bn(x)
        x = x.view(N, 2, T, 17)
        
        # Forward through ST-GCN blocks with residual connections
        for gcn in self.st_gcn_networks:
            x = gcn(x)
        
        # Global pooling and classification
        x = F.adaptive_avg_pool2d(x, (1, 1))
        x = self.dropout(x)
        x = self.fcn(x)
        x = x.view(x.size(0), -1)
        
        return x

def train_model(model, train_loader, num_epochs=50):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    
    # Learning rate와 optimizer 조정
    optimizer = optim.AdamW(model.parameters(), lr=0.0005, weight_decay=0.01)
    
    # Cosine Annealing 스케줄러 사용
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=num_epochs,
        eta_min=1e-6
    )
    
    best_loss = float('inf')
    patience = 10
    counter = 0
    best_epoch = 0
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        num_batches = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
        for sequences, labels in pbar:
            sequences = sequences.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            
            logits = model(sequences)
            loss = criterion(logits, labels.squeeze())
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            
            pred = logits.argmax(dim=1)
            correct += (pred == labels.squeeze()).sum().item()
            total += labels.size(0)
            
            total_loss += loss.item()
            num_batches += 1
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.0 * correct / total:.2f}%',
                'lr': f'{scheduler.get_last_lr()[0]:.6f}'
            })
        
        avg_loss = total_loss / num_batches
        accuracy = 100.0 * correct / total
        
        print(f'Epoch {epoch+1}:')
        print(f'  Average Loss: {avg_loss:.4f}')
        print(f'  Accuracy: {accuracy:.2f}%')
        print(f'  Learning Rate: {scheduler.get_last_lr()[0]:.6f}')
        
        scheduler.step()
        
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
    model = AnomalyDetector(num_classes=4, in_channels=2)
    print("Loading dataset...")
    # Linux 경로로 수정
    base_dir = "E:/mldl/편집영상"
    dataset = VideoDataset(base_dir=base_dir)
    print(f"Total sequences: {len(dataset)}")
    
    label_names = ['normal', 'theft', 'abandon', 'broken']
    # 시퀀스의 레이블만 추출하여 카운트
    label_counts = Counter([label for _, label in dataset.sequences])
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