import torch
import cv2
import numpy as np
from anomaly_detection import AnomalyDetector
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import torch.nn.functional as F
import torchvision.transforms as transforms
from collections import Counter

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_path):
    model = AnomalyDetector()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def extract_joints(frame, pose_model):
    # Remove resizing, use original frame
    try:
        results = pose_model(frame, verbose=False)[0]
        if results.keypoints is not None and len(results.keypoints) > 0:
            keypoints = results.keypoints[0].data[0].cpu().numpy()
            joints = np.zeros(17 * 4)
            for i, kp in enumerate(keypoints):
                if i < 17:
                    # Use 256 normalization to match training data
                    joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
            return joints, keypoints
        else:
            return np.zeros(17 * 4), None
    except Exception as e:
        print(f"Error processing frame: {e}")
        return np.zeros(17 * 4), None

def get_abnormal_label(framewise_preds, anomaly_scores, consecutive_threshold=5):
    """
    연속성 기반 이상 행위 라벨 결정 함수
    - 연속으로 Normal이 아닌 프레임이 consecutive_threshold개 이상 감지되면 해당 라벨로 인식
    - 실시간 반영 가능
    """
    if len(framewise_preds) == 0:
        return 0
    
    current_label = None
    consecutive_count = 0
    
    for i, pred in enumerate(framewise_preds):
        if pred != 0:  # Normal이 아닌 경우
            if current_label is None:
                # 새로운 이상 행위 시작
                current_label = pred
                consecutive_count = 1
            elif pred == current_label:
                # 같은 라벨이 연속
                consecutive_count += 1
                # 임계값 도달하면 즉시 반환
                if consecutive_count >= consecutive_threshold:
                    return current_label
            else:
                # 다른 라벨이 감지되면 리셋
                current_label = pred
                consecutive_count = 1
        else:
            # Normal이 감지되면 리셋
            current_label = None
            consecutive_count = 0
    
    # 마지막까지 임계값에 도달하지 못하면 Normal
    return 0

def predict_video(model, video_path, pose_model, threshold=0.5, frame_interval=1, result_dir=None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None, None, None, None
    
    frames = []
    anomaly_scores = []
    frame_count = 0
    
    sequence_length = 15
    joints_sequence = []

    # Prepare video writer for output
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if result_dir is None:
        result_dir = os.path.join(os.path.dirname(video_path), 'result')
    os.makedirs(result_dir, exist_ok=True)
    output_path = os.path.join(result_dir, os.path.splitext(os.path.basename(video_path))[0] + '_output.mp4')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 프레임 샘플링 (frame_interval 프레임마다 처리)
        if frame_count % frame_interval == 0:
            joints, keypoints = extract_joints(frame, pose_model)
            
            # 관절점 시각화 및 감지 여부
            has_person = False
            if keypoints is not None:
                for kp in keypoints[:17]:
                    if len(kp) == 3:
                        x, y, conf = kp
                    elif len(kp) == 4:
                        x, y, _, conf = kp
                    else:
                        continue
                    if conf > 0.1:
                        has_person = True
                        cv2.circle(frame, (int(x), int(y)), 4, (255, 0, 0), -1)

            if has_person:
                joints_sequence.append(joints)
            else:
                # 관절점이 없으면 시퀀스에 넣지 않고, No person detected만 오버레이
                cv2.putText(frame, "No person detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                out.write(frame)
                frame_count += 1
                continue

            if len(joints_sequence) < sequence_length:
                cv2.putText(frame, "Normal", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                out.write(frame)
                frame_count += 1
                continue
                
            # 모델 예측
            input_tensor = torch.FloatTensor(joints_sequence).unsqueeze(0).to(device)
            with torch.no_grad():
                logits = model(input_tensor)
                probs = F.softmax(logits, dim=1).cpu().numpy()[0]
                
            anomaly_scores.append(probs)
            frames.append(frame)
            
            # 오버레이: 예측 결과
            cv2.putText(frame, f"Normal: {probs[0]:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f"Theft: {probs[1]:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f"Abandon: {probs[2]:.2f}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f"Broken: {probs[3]:.2f}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            pred_label = np.argmax(probs)
            pred_label_name = ["Normal", "Theft", "Abandon", "Broken"][pred_label]
            cv2.putText(frame, f"Prediction: {pred_label_name}", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            out.write(frame)
            joints_sequence.pop(0)
        else:
            # 샘플링 안 된 프레임도 그대로 저장
            out.write(frame)
        frame_count += 1
    cap.release()
    out.release()
    
    if not anomaly_scores:
        return None, None, None, None
        
    anomaly_scores_array = np.array(anomaly_scores)
    max_score = np.max(anomaly_scores_array)
    # 다중 클래스 분류를 위한 임계값 설정
    framewise_preds = np.argmax(anomaly_scores_array, axis=1)
    predicted_label = get_abnormal_label(framewise_preds, anomaly_scores_array, consecutive_threshold=5)
    return max_score, anomaly_scores, frames, predicted_label

def get_label_from_filename(filename):
    prefix = filename.split('.')[0]
    if prefix.startswith('abandon'):
        return 2  # Abandon
    elif prefix.startswith('broken'):
        return 3  # Broken
    elif prefix.startswith('theft'):
        return 1  # Theft
    else:
        return 0  # Normal (or other)

def process_directory(model, base_dir, pose_model, threshold=0.5, frame_interval=1):
    results = []
    # 모든 mp4 파일을 가져와서 라벨 매핑
    video_files = []
    for fname in os.listdir(base_dir):
        if fname.endswith('.mp4'):
            label = get_label_from_filename(fname)
            video_files.append((os.path.join(base_dir, fname), label))
    print(f"\nProcessing {len(video_files)} videos...")
    result_dir = os.path.join(base_dir, 'result')
    for video_path, true_label in tqdm(video_files):
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            continue
        max_score, anomaly_scores, frames, predicted_label = predict_video(model, video_path, pose_model, threshold, frame_interval, result_dir=result_dir)
        if max_score is not None:
            anomaly_scores_array = np.array(anomaly_scores)
            framewise_preds = np.argmax(anomaly_scores_array, axis=1)
            results.append({
                'video': os.path.basename(video_path),
                'true_label': true_label,
                'predicted_label': predicted_label,
                'max_score': max_score,
                'scores': anomaly_scores
            })
            os.makedirs('test_results', exist_ok=True)
            video_name = os.path.basename(video_path)
            plt.figure(figsize=(15, 5))
            plt.plot(anomaly_scores, label='Anomaly Score')
            plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
            plt.title(f'Anomaly Detection Results - {video_name}\nTrue: {"Theft" if true_label == 1 else "Normal" if true_label == 0 else "Abandon" if true_label == 2 else "Broken"}, Predicted: {"Theft" if predicted_label == 1 else "Normal" if predicted_label == 0 else "Abandon" if predicted_label == 2 else "Broken"}')
            plt.xlabel('Frame')
            plt.ylabel('Anomaly Score')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'test_results/{video_name}_scores.png')
            plt.close()
    return results

def print_results_summary(results):
    if not results:
        print("No results to analyze!")
        return
    
    print("\n=== Results Summary ===")
    
    # 혼동 행렬을 위한 카운터 초기화
    confusion_matrix = {
        'Theft': {'Theft': 0, 'Normal': 0, 'Abandon': 0, 'Broken': 0},
        'Normal': {'Theft': 0, 'Normal': 0, 'Abandon': 0, 'Broken': 0},
        'Abandon': {'Theft': 0, 'Normal': 0, 'Abandon': 0, 'Broken': 0},
        'Broken': {'Theft': 0, 'Normal': 0, 'Abandon': 0, 'Broken': 0}
    }
    
    # 결과 분석
    for result in results:
        label_names = ["Normal", "Theft", "Abandon", "Broken"]
        true_label_name = label_names[result['true_label']]
        pred_label_name = label_names[result['predicted_label']]
        confusion_matrix[true_label_name][pred_label_name] += 1
    
    # 메트릭 계산
    total = len(results)
    correct_predictions = sum(confusion_matrix[label][label] for label in confusion_matrix)
    accuracy = correct_predictions / total if total > 0 else 0
    
    print(f"\nTotal videos processed: {total}")
    print(f"Accuracy: {accuracy:.2%}")
    
    print("\nConfusion Matrix:")
    print("                Predicted Theft  Predicted Normal  Predicted Abandon  Predicted Broken")
    for true_label in confusion_matrix:
        row = f"{true_label:15}"
        for pred_label in confusion_matrix[true_label]:
            row += f"{confusion_matrix[true_label][pred_label]:17d}"
        print(row)
    
    # 개별 비디오 결과
    print("\nDetailed Results:")
    for result in results:
        print(f"\nVideo: {result['video']}")
        label_names = ["Normal", "Theft", "Abandon", "Broken"]
        true_label_name = label_names[result['true_label']]
        pred_label_name = label_names[result['predicted_label']]
        print(f"True Label: {true_label_name}")
        print(f"Predicted: {pred_label_name}")
        print(f"Max Anomaly Score: {result['max_score']:.4f}")

if __name__ == "__main__":
    model_path = "saved_models/스트그쓰느.pth"
    model = load_model(model_path)
    pose_model = YOLO('yolov8n-pose.pt')
    test_dir = "/home/koo4802/Desktop/test_videos"
    results = process_directory(model, test_dir, pose_model, threshold=0.5, frame_interval=1)
    print_results_summary(results)
    print("\nAnalysis complete! Check 'test_results' directory for individual video visualizations.") 