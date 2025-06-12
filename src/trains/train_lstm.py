from utils.keypoint_utils import LABELS, NUM_CLASSES, INV_LABELS, get_class_weights
from modules.lstm import KeypointSequenceDataset, AdvancedLSTMClassifier, process_features, evaluate
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import glob
import os
import re
from sklearn.metrics import classification_report, confusion_matrix

def main():
    feature_root = '/home/ckim/dev_ws/project_ws/mldl_project/data/features'
    seq_len = 120
    batch_size = 128
    num_epochs = 100
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    normal_ratio = 2
    patience = 15

    # 데이터셋 및 데이터로더
    train_dataset = KeypointSequenceDataset(feature_root, 'train', seq_len=seq_len, normal_ratio=normal_ratio)
    val_dataset = KeypointSequenceDataset(feature_root, 'val', seq_len=seq_len, normal_ratio=normal_ratio)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # 클래스 불균형 가중치 계산
    class_weights = get_class_weights(train_dataset.labels).to(device)
    print(f"Class weights: {class_weights}")

    # 모델, 손실함수, 옵티마이저, 스케줄러
    model = AdvancedLSTMClassifier(input_dim=17*4, hidden_dim=512, num_layers=4, num_classes=NUM_CLASSES, dropout=0.5, bidirectional=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=7)

    start_epoch = 0
    best_f1 = 0
    patience_counter = 0
    best_model_path = ""

    # --- 체크포인트 로드 로직 추가 ---
    checkpoint_files = glob.glob('lstm_dynamic_best_epoch*.pth')
    if checkpoint_files:
        latest_checkpoint = max(checkpoint_files, key=os.path.getctime)
        print(f"Resuming training from {latest_checkpoint}")
        
        model.load_state_dict(torch.load(latest_checkpoint))
        
        # 파일 이름에서 에포크와 f1 점수 파싱
        match = re.search(r'epoch(\d+)_f1([\d\.]+)\.pth', latest_checkpoint)
        if match:
            start_epoch = int(match.group(1))
            best_f1 = float(match.group(2))
            best_model_path = latest_checkpoint
            print(f"Loaded model from epoch {start_epoch} with F1 score {best_f1:.4f}. Starting next epoch.")
    # ------------------------------------

    for epoch in range(start_epoch, num_epochs):
        model.train()
        total_loss = 0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]")
        for X, y in pbar:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(X)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * y.size(0)
            pbar.set_postfix({'loss': loss.item()})
        avg_loss = total_loss / len(train_dataset)

        # 검증
        val_acc, val_f1, y_true, y_pred = evaluate(model, val_loader, device)
        print(f"Epoch {epoch+1}/{num_epochs} | Train Loss: {avg_loss:.4f} | Val Acc: {val_acc:.4f} | Val F1: {val_f1:.4f}")
        scheduler.step(val_f1)
        print(f"Current LR: {optimizer.param_groups[0]['lr']}")

        # best 모델 저장 로직 수정: 최고 성능 모델 하나만 저장
        if val_f1 > best_f1:
            best_f1 = val_f1
            patience_counter = 0
            
            # 이전 best 모델이 있다면 삭제
            if best_model_path and os.path.exists(best_model_path):
                os.remove(best_model_path)
            
            # 새로운 best 모델 정보 업데이트 및 저장
            # epoch 변수는 0부터 시작하므로 +1 해줌
            new_model_path = f'lstm_dynamic_best_epoch{epoch+1}_f1{val_f1:.4f}.pth'
            torch.save(model.state_dict(), new_model_path)
            best_model_path = new_model_path
            print(f"New best model saved to {best_model_path}")
        else:
            patience_counter += 1
        
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

    # 최종 평가 (best F1 모델)
    if not best_model_path:
        print("No best model was saved. Check training process.")
        return
        
    print(f"\n=== Best Model from {best_model_path} ===")
    model.load_state_dict(torch.load(best_model_path))
    val_acc, val_f1, y_true, y_pred = evaluate(model, val_loader, device)
    print(f"최종 검증 정확도: {val_acc:.4f}")
    print(f"최종 검증 F1-score: {val_f1:.4f}")
    print("\n[Classification Report]")
    print(classification_report(y_true, y_pred, target_names=[INV_LABELS[i] for i in range(NUM_CLASSES)], zero_division=0))
    print("\n[Confusion Matrix]")
    print(confusion_matrix(y_true, y_pred))
    print(f"\nBest 모델 저장 위치: {best_model_path}")

if __name__ == '__main__':
    main() 