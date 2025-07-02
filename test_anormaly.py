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
import koreanize_matplotlib
import time
import psutil
import gc
from datetime import datetime

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.gpu_memory_usage = []
        
    def start(self):
        self.start_time = time.time()
        self.memory_usage.append(psutil.virtual_memory().percent)
        if torch.cuda.is_available():
            self.gpu_memory_usage.append(torch.cuda.memory_allocated() / 1024**3)  # GB
            
    def end(self):
        self.end_time = time.time()
        self.memory_usage.append(psutil.virtual_memory().percent)
        if torch.cuda.is_available():
            self.gpu_memory_usage.append(torch.cuda.memory_allocated() / 1024**3)  # GB
            
    def get_elapsed_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
        
    def get_memory_stats(self):
        if len(self.memory_usage) >= 2:
            return {
                'start_memory': self.memory_usage[0],
                'end_memory': self.memory_usage[-1],
                'max_memory': max(self.memory_usage),
                'avg_memory': sum(self.memory_usage) / len(self.memory_usage)
            }
        return {}
        
    def get_gpu_stats(self):
        if len(self.gpu_memory_usage) >= 2:
            return {
                'start_gpu_memory': self.gpu_memory_usage[0],
                'end_gpu_memory': self.gpu_memory_usage[-1],
                'max_gpu_memory': max(self.gpu_memory_usage),
                'avg_gpu_memory': sum(self.gpu_memory_usage) / len(self.gpu_memory_usage)
            }
        return {}

def generate_dummy_data(sequence_length=15, num_sequences=100):
    """더미 데이터 생성 함수"""
    dummy_sequences = []
    for _ in range(num_sequences):
        # 랜덤한 관절점 데이터 생성 (17개 관절점 * 4개 값)
        sequence = []
        for _ in range(sequence_length):
            joints = np.random.rand(17 * 4)
            # 신뢰도 값은 0~1 사이로 제한
            for i in range(3, 17 * 4, 4):
                joints[i] = np.random.uniform(0.1, 1.0)
            sequence.append(joints)
        dummy_sequences.append(sequence)
    return dummy_sequences

def test_dummy_data_performance(model, num_sequences=100, sequence_length=15):
    """더미 데이터로 모델 성능 테스트"""
    print(f"\n🧪 더미 데이터 성능 테스트 시작...")
    print(f"   - 시퀀스 수: {num_sequences}")
    print(f"   - 시퀀스 길이: {sequence_length}")
    
    monitor = PerformanceMonitor()
    monitor.start()
    
    dummy_data = generate_dummy_data(sequence_length, num_sequences)
    
    predictions = []
    inference_times = []
    
    for i, sequence in enumerate(dummy_data):
        input_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(device)
        
        # 개별 추론 시간 측정
        start_inference = time.time()
        with torch.no_grad():
            logits = model(input_tensor)
            if logits.ndim == 3:
                logits = logits[:, -1, :]
            elif logits.ndim == 2:
                logits = logits[-1, :]
            probs = F.softmax(logits, dim=-1).cpu().numpy().flatten()
        end_inference = time.time()
        
        predictions.append(np.argmax(probs))
        inference_times.append(end_inference - start_inference)
        
        if (i + 1) % 20 == 0:
            print(f"   진행률: {i+1}/{num_sequences}")
    
    monitor.end()
    
    total_time = monitor.get_elapsed_time()
    avg_inference_time = np.mean(inference_times)
    fps = num_sequences / total_time
    
    memory_stats = monitor.get_memory_stats()
    gpu_stats = monitor.get_gpu_stats()
    
    print(f"✅ 더미 데이터 테스트 완료!")
    print(f"   - 총 처리 시간: {total_time:.2f}초")
    print(f"   - 평균 추론 시간: {avg_inference_time*1000:.2f}ms")
    print(f"   - 처리 속도: {fps:.2f} FPS")
    print(f"   - 메모리 사용량: {memory_stats.get('avg_memory', 0):.1f}%")
    if gpu_stats:
        print(f"   - GPU 메모리 사용량: {gpu_stats.get('avg_gpu_memory', 0):.2f}GB")
    
    return {
        'total_time': total_time,
        'avg_inference_time': avg_inference_time,
        'fps': fps,
        'memory_stats': memory_stats,
        'gpu_stats': gpu_stats,
        'predictions': predictions
    }

def load_model(model_path):
    """
    모델을 로드합니다. TorchScript 모델인지 확인하여 적절히 로드합니다.
    """
    if model_path.endswith('.pt') or model_path.endswith('.torchscript'):
        try:
            # TorchScript 모델 시도
            model = torch.jit.load(model_path, map_location=device)
            model.eval()
            print(f"TorchScript 모델 로딩: {model_path}")
            return model
        except Exception:
            # 일반 state_dict 시도
            print(f"일반 PyTorch 모델 로딩: {model_path}")
            model = AnomalyDetector()
            model.load_state_dict(torch.load(model_path, map_location=device))
            model = model.to(device)
            model.eval()
            return model
    else:
        # 기본: 일반 PyTorch 모델
        print(f"일반 PyTorch 모델 로딩: {model_path}")
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
            keypoints = results.keypoints.data.cpu().numpy()  # [num_people, 17, 3] 형태
            
            joints = np.zeros(17 * 4)
            for i, kp in enumerate(keypoints[0][:17]):  # 첫 번째 사람의 관절점만 사용
                if i < 17:
                    # Use 256 normalization to match training data
                    joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
            return joints, keypoints
        else:
            return np.zeros(17 * 4), None
    except Exception as e:
        print(f"Error processing frame: {e}")
        return np.zeros(17 * 4), None

def count_valid_persons(keypoints):
    """유효한 사람 수를 계산 (AI 서버와 동일한 방식)"""
    if keypoints is None or len(keypoints) == 0:
        return 0
    
    person_count = 0
    for person_idx in range(len(keypoints)):
        valid_keypoints = 0
        for kp_idx in range(len(keypoints[person_idx])):
            if kp_idx < 17 and float(keypoints[person_idx][kp_idx][2]) > 0.1:  # KEYPOINT_CONFIDENCE_THRESHOLD
                valid_keypoints += 1
        
        if valid_keypoints >= 8:  # MIN_VALID_KEYPOINTS
            person_count += 1
    
    return person_count

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

def predict_video(model, video_path, pose_model, threshold=0.5, frame_interval=1, result_dir=None, measure_performance=False):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None, None, None, None
    
    anomaly_scores = []
    frame_count = 0
    total_frames = 0
    processed_frames = 0
    
    sequence_length = 15
    joints_sequence = []
    
    # 성능 측정 변수들
    performance_stats = {}
    if measure_performance:
        monitor = PerformanceMonitor()
        monitor.start()
        inference_times = []
        pose_detection_times = []
    
    # 전체 프레임 수 계산
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 프레임 샘플링 (frame_interval 프레임마다 처리)
        if frame_count % frame_interval == 0:
            if measure_performance:
                start_pose = time.time()
            
            joints, keypoints = extract_joints(frame, pose_model)
            
            if measure_performance:
                end_pose = time.time()
                pose_detection_times.append(end_pose - start_pose)
            
            person_count = count_valid_persons(keypoints)
            if person_count > 0:
                joints_sequence.append(joints)
            else:
                frame_count += 1
                continue
            if len(joints_sequence) < sequence_length:
                frame_count += 1
                continue
            
            # 모델 예측
            input_tensor = torch.FloatTensor(joints_sequence).unsqueeze(0).to(device)
            
            if measure_performance:
                start_inference = time.time()
            
            with torch.no_grad():
                logits = model(input_tensor)
                if logits.ndim == 3:
                    logits = logits[:, -1, :]
                elif logits.ndim == 2:
                    logits = logits[-1, :]
                probs = F.softmax(logits, dim=-1).cpu().numpy().flatten()
            
            if measure_performance:
                end_inference = time.time()
                inference_times.append(end_inference - start_inference)
            
            anomaly_scores.append(probs)
            joints_sequence.pop(0)
            processed_frames += 1
        frame_count += 1
    
    cap.release()
    
    if measure_performance:
        monitor.end()
        performance_stats = {
            'total_time': monitor.get_elapsed_time(),
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'avg_inference_time': np.mean(inference_times) if inference_times else 0,
            'avg_pose_detection_time': np.mean(pose_detection_times) if pose_detection_times else 0,
            'fps': processed_frames / monitor.get_elapsed_time() if monitor.get_elapsed_time() > 0 else 0,
            'memory_stats': monitor.get_memory_stats(),
            'gpu_stats': monitor.get_gpu_stats()
        }
    
    if not anomaly_scores:
        return None, None, None, None, performance_stats if measure_performance else None
    
    anomaly_scores_array = np.array(anomaly_scores)
    max_score = np.max(anomaly_scores_array)
    framewise_preds = np.argmax(anomaly_scores_array, axis=1)
    predicted_label = get_abnormal_label(framewise_preds, anomaly_scores_array, consecutive_threshold=5)
    
    return max_score, anomaly_scores, None, predicted_label, performance_stats if measure_performance else None

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

def process_directory(model, base_dir, pose_model, threshold=0.5, frame_interval=1, measure_performance=False):
    results = []
    performance_summary = {
        'total_videos': 0,
        'total_processing_time': 0,
        'total_frames_processed': 0,
        'avg_fps': 0,
        'avg_inference_time': 0,
        'avg_pose_detection_time': 0,
        'memory_usage': [],
        'gpu_memory_usage': []
    }
    
    # 모든 mp4 파일을 가져와서 라벨 매핑
    video_files = []
    for fname in os.listdir(base_dir):
        if fname.endswith('.mp4'):
            label = get_label_from_filename(fname)
            video_files.append((os.path.join(base_dir, fname), label))
    
    print(f"\nProcessing {len(video_files)} videos...")
    if measure_performance:
        print("📊 성능 측정 모드 활성화")
    
    result_dir = os.path.join(base_dir, 'result')
    
    for video_path, true_label in tqdm(video_files):
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            continue
        
        max_score, anomaly_scores, frames, predicted_label, perf_stats = predict_video(
            model, video_path, pose_model, threshold, frame_interval, 
            result_dir=result_dir, measure_performance=measure_performance
        )
        
        if max_score is not None:
            anomaly_scores_array = np.array(anomaly_scores)
            framewise_preds = np.argmax(anomaly_scores_array, axis=1)
            
            result_item = {
                'video': os.path.basename(video_path),
                'true_label': true_label,
                'predicted_label': predicted_label,
                'max_score': max_score,
                'scores': anomaly_scores
            }
            
            # 성능 통계 추가
            if measure_performance and perf_stats:
                result_item['performance'] = perf_stats
                performance_summary['total_videos'] += 1
                performance_summary['total_processing_time'] += perf_stats['total_time']
                performance_summary['total_frames_processed'] += perf_stats['processed_frames']
                performance_summary['memory_usage'].append(perf_stats['memory_stats'].get('avg_memory', 0))
                if perf_stats['gpu_stats']:
                    performance_summary['gpu_memory_usage'].append(perf_stats['gpu_stats'].get('avg_gpu_memory', 0))
            
            results.append(result_item)
            
            # 그래프 생성
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
    
    # 성능 요약 계산
    if measure_performance and performance_summary['total_videos'] > 0:
        performance_summary['avg_fps'] = performance_summary['total_frames_processed'] / performance_summary['total_processing_time']
        performance_summary['avg_inference_time'] = np.mean([r['performance']['avg_inference_time'] for r in results if 'performance' in r])
        performance_summary['avg_pose_detection_time'] = np.mean([r['performance']['avg_pose_detection_time'] for r in results if 'performance' in r])
        performance_summary['avg_memory_usage'] = np.mean(performance_summary['memory_usage'])
        if performance_summary['gpu_memory_usage']:
            performance_summary['avg_gpu_memory_usage'] = np.mean(performance_summary['gpu_memory_usage'])
    
    return results, performance_summary if measure_performance else results

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
    
    # 전체 결과 시각화
    visualize_overall_results(results, confusion_matrix, accuracy)

def visualize_overall_results(results, confusion_matrix, accuracy):
    """
    전체 결과를 시각화하는 함수
    """
    os.makedirs('test_results', exist_ok=True)
    
    # 1. 혼동 행렬 히트맵
    plt.figure(figsize=(10, 8))
    labels = ['Normal', 'Theft', 'Abandon', 'Broken']
    cm_array = np.array([[confusion_matrix[true_label][pred_label] 
                          for pred_label in labels] 
                         for true_label in labels])
    
    plt.imshow(cm_array, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix (Accuracy: {accuracy:.2%})', fontsize=16, pad=20)
    plt.colorbar()
    
    # 셀에 숫자 표시
    thresh = cm_array.max() / 2.
    for i in range(cm_array.shape[0]):
        for j in range(cm_array.shape[1]):
            plt.text(j, i, format(cm_array[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm_array[i, j] > thresh else "black", fontsize=12)
    
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.xticks(range(len(labels)), labels, rotation=45)
    plt.yticks(range(len(labels)), labels)
    plt.tight_layout()
    plt.savefig('test_results/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 클래스별 정확도
    plt.figure(figsize=(12, 6))
    class_accuracies = []
    class_names = []
    
    for label in labels:
        if sum(confusion_matrix[label].values()) > 0:
            class_acc = confusion_matrix[label][label] / sum(confusion_matrix[label].values())
            class_accuracies.append(class_acc)
            class_names.append(label)
    
    bars = plt.bar(class_names, class_accuracies, color=['#2E8B57', '#FF6B6B', '#4ECDC4', '#45B7D1'])
    plt.title('Accuracy by Class', fontsize=16, pad=20)
    plt.ylabel('Accuracy', fontsize=12)
    plt.xlabel('Class', fontsize=12)
    plt.ylim(0, 1)
    
    # 막대 위에 정확도 표시
    for bar, acc in zip(bars, class_accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.2%}', ha='center', va='bottom', fontsize=11)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('test_results/class_accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 비디오별 예측 결과 비교
    plt.figure(figsize=(16, 10))
    
    # 서브플롯 1: 예측 vs 실제 라벨
    plt.subplot(2, 2, 1)
    video_names = [result['video'] for result in results]
    true_labels = [result['true_label'] for result in results]
    pred_labels = [result['predicted_label'] for result in results]
    
    x = range(len(video_names))
    plt.scatter(x, true_labels, c='blue', s=100, alpha=0.7, label='True Label', marker='o')
    plt.scatter(x, pred_labels, c='red', s=100, alpha=0.7, label='Predicted Label', marker='s')
    
    # 잘못 예측된 것들 연결선 표시
    for i, (true, pred) in enumerate(zip(true_labels, pred_labels)):
        if true != pred:
            plt.plot([i, i], [true, pred], 'r--', alpha=0.5, linewidth=1)
    
    plt.yticks([0, 1, 2, 3], ['Normal', 'Theft', 'Abandon', 'Broken'])
    plt.xlabel('Video Index')
    plt.ylabel('Label')
    plt.title('True vs Predicted Labels by Video')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 2: 최대 이상 점수 분포
    plt.subplot(2, 2, 2)
    max_scores = [result['max_score'] for result in results]
    correct_predictions = [1 if result['true_label'] == result['predicted_label'] else 0 for result in results]
    
    colors = ['green' if correct else 'red' for correct in correct_predictions]
    plt.bar(range(len(max_scores)), max_scores, color=colors, alpha=0.7)
    plt.xlabel('Video Index')
    plt.ylabel('Max Anomaly Score')
    plt.title('Max Anomaly Score by Video\n(Green: Correct, Red: Incorrect)')
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 3: 클래스별 비디오 수
    plt.subplot(2, 2, 3)
    true_label_counts = Counter(true_labels)
    pred_label_counts = Counter(pred_labels)
    
    x = np.arange(len(labels))
    width = 0.35
    
    plt.bar(x - width/2, [true_label_counts.get(i, 0) for i in range(4)], 
            width, label='True', alpha=0.8, color='blue')
    plt.bar(x + width/2, [pred_label_counts.get(i, 0) for i in range(4)], 
            width, label='Predicted', alpha=0.8, color='red')
    
    plt.xlabel('Class')
    plt.ylabel('Number of Videos')
    plt.title('Video Distribution by Class')
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 4: 전체 통계 요약
    plt.subplot(2, 2, 4)
    plt.axis('off')
    
    # 텍스트 정보 표시
    stats_text = f"""
    Overall Statistics:
    
    Total Videos: {len(results)}
    Overall Accuracy: {accuracy:.2%}
    
    Class-wise Results:
    """
    
    for i, label in enumerate(labels):
        total_class = sum(confusion_matrix[label].values())
        if total_class > 0:
            class_acc = confusion_matrix[label][label] / total_class
            stats_text += f"{label}: {confusion_matrix[label][label]}/{total_class} ({class_acc:.2%})\n"
    
    plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
             fontsize=12, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('test_results/overall_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. 이상 점수 분포 히스토그램
    plt.figure(figsize=(12, 8))
    
    # 클래스별로 이상 점수 분리
    class_scores = {0: [], 1: [], 2: [], 3: []}
    for result in results:
        class_scores[result['true_label']].append(result['max_score'])
    
    colors = ['green', 'red', 'orange', 'purple']
    for i, (class_idx, scores) in enumerate(class_scores.items()):
        if scores:
            plt.hist(scores, bins=10, alpha=0.6, label=f'{labels[class_idx]} (n={len(scores)})', 
                    color=colors[i], edgecolor='black')
    
    plt.xlabel('Max Anomaly Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Max Anomaly Scores by True Class')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('test_results/score_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n📊 시각화 완료! 다음 파일들을 확인하세요:")
    print(f"   - test_results/confusion_matrix.png: 혼동 행렬")
    print(f"   - test_results/class_accuracy.png: 클래스별 정확도")
    print(f"   - test_results/overall_analysis.png: 전체 분석 결과")
    print(f"   - test_results/score_distribution.png: 이상 점수 분포")

def visualize_performance_results(all_results, all_performance_summaries, dummy_performance_results):
    """
    성능 결과를 시각화하는 함수
    """
    os.makedirs('test_results', exist_ok=True)
    
    # 1. 모델별 전체 성능 비교
    plt.figure(figsize=(15, 10))
    
    # 서브플롯 1: 처리 속도 (FPS) 비교
    plt.subplot(2, 3, 1)
    model_names = [os.path.basename(name).replace('.pt', '') for name in all_results.keys()]
    fps_values = [summary.get('avg_fps', 0) for summary in all_performance_summaries.values()]
    
    bars = plt.bar(model_names, fps_values, color='skyblue', alpha=0.8)
    plt.title('Processing Speed (FPS) by Model', fontsize=14, pad=20)
    plt.ylabel('Frames Per Second', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    plt.xticks(rotation=45)
    
    # 막대 위에 값 표시
    for bar, fps in zip(bars, fps_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{fps:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    
    # 서브플롯 2: 평균 추론 시간 비교
    plt.subplot(2, 3, 2)
    inference_times = [summary.get('avg_inference_time', 0) * 1000 for summary in all_performance_summaries.values()]  # ms로 변환
    
    bars = plt.bar(model_names, inference_times, color='lightcoral', alpha=0.8)
    plt.title('Average Inference Time by Model', fontsize=14, pad=20)
    plt.ylabel('Time (ms)', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    plt.xticks(rotation=45)
    
    for bar, time_ms in zip(bars, inference_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{time_ms:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    
    # 서브플롯 3: 메모리 사용량 비교
    plt.subplot(2, 3, 3)
    memory_usage = [summary.get('avg_memory_usage', 0) for summary in all_performance_summaries.values()]
    
    bars = plt.bar(model_names, memory_usage, color='lightgreen', alpha=0.8)
    plt.title('Average Memory Usage by Model', fontsize=14, pad=20)
    plt.ylabel('Memory Usage (%)', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    plt.xticks(rotation=45)
    
    for bar, mem in zip(bars, memory_usage):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{mem:.1f}%', ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    
    # 서브플롯 4: 더미 데이터 vs 실제 데이터 성능 비교
    plt.subplot(2, 3, 4)
    if dummy_performance_results:
        dummy_fps = [result['fps'] for result in dummy_performance_results.values()]
        real_fps = [summary.get('avg_fps', 0) for summary in all_performance_summaries.values()]
        
        x = np.arange(len(model_names))
        width = 0.35
        
        plt.bar(x - width/2, dummy_fps, width, label='Dummy Data', alpha=0.8, color='orange')
        plt.bar(x + width/2, real_fps, width, label='Real Video Data', alpha=0.8, color='blue')
        
        plt.title('Dummy vs Real Data Performance', fontsize=14, pad=20)
        plt.ylabel('FPS', fontsize=12)
        plt.xlabel('Model', fontsize=12)
        plt.xticks(x, model_names, rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
    
    # 서브플롯 5: 전체 처리 시간 비교
    plt.subplot(2, 3, 5)
    total_times = [summary.get('total_processing_time', 0) for summary in all_performance_summaries.values()]
    
    bars = plt.bar(model_names, total_times, color='gold', alpha=0.8)
    plt.title('Total Processing Time by Model', fontsize=14, pad=20)
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    plt.xticks(rotation=45)
    
    for bar, time_sec in zip(bars, total_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{time_sec:.1f}s', ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    
    # 서브플롯 6: 성능 요약 테이블
    plt.subplot(2, 3, 6)
    plt.axis('off')
    
    # 요약 테이블 생성
    summary_data = []
    for i, model_name in enumerate(model_names):
        summary_data.append([
            model_name,
            f"{fps_values[i]:.1f}",
            f"{inference_times[i]:.1f}ms",
            f"{memory_usage[i]:.1f}%",
            f"{total_times[i]:.1f}s"
        ])
    
    table = plt.table(cellText=summary_data,
                     colLabels=['Model', 'FPS', 'Inference', 'Memory', 'Total Time'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    plt.title('Performance Summary', fontsize=14, pad=20)
    
    plt.tight_layout()
    plt.savefig('test_results/performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 상세 성능 분석 그래프
    plt.figure(figsize=(16, 12))
    
    # 서브플롯 1: 모델별 추론 시간 분포
    plt.subplot(2, 2, 1)
    for model_path, results in all_results.items():
        model_name = os.path.basename(model_path).replace('.pt', '')
        inference_times = [r['performance']['avg_inference_time'] * 1000 for r in results if 'performance' in r]
        if inference_times:
            plt.hist(inference_times, alpha=0.6, label=model_name, bins=10)
    
    plt.xlabel('Inference Time (ms)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Inference Times by Model')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 2: 모델별 FPS 분포
    plt.subplot(2, 2, 2)
    for model_path, results in all_results.items():
        model_name = os.path.basename(model_path).replace('.pt', '')
        fps_values = [r['performance']['fps'] for r in results if 'performance' in r]
        if fps_values:
            plt.hist(fps_values, alpha=0.6, label=model_name, bins=10)
    
    plt.xlabel('FPS')
    plt.ylabel('Frequency')
    plt.title('Distribution of FPS by Model')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 3: 메모리 사용량 추이
    plt.subplot(2, 2, 3)
    for model_path, results in all_results.items():
        model_name = os.path.basename(model_path).replace('.pt', '')
        memory_values = [r['performance']['memory_stats']['avg_memory'] for r in results if 'performance' in r]
        if memory_values:
            plt.plot(memory_values, alpha=0.7, label=model_name, marker='o')
    
    plt.xlabel('Video Index')
    plt.ylabel('Memory Usage (%)')
    plt.title('Memory Usage Trend by Model')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 4: 성능 vs 정확도 관계
    plt.subplot(2, 2, 4)
    for model_path, results in all_results.items():
        model_name = os.path.basename(model_path).replace('.pt', '')
        fps_values = [r['performance']['fps'] for r in results if 'performance' in r]
        accuracies = [1 if r['true_label'] == r['predicted_label'] else 0 for r in results if 'performance' in r]
        
        if fps_values and accuracies:
            avg_fps = np.mean(fps_values)
            avg_accuracy = np.mean(accuracies)
            plt.scatter(avg_fps, avg_accuracy, s=100, alpha=0.7, label=model_name)
    
    plt.xlabel('Average FPS')
    plt.ylabel('Accuracy')
    plt.title('Performance vs Accuracy Trade-off')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_results/detailed_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n🚀 성능 분석 완료! 다음 파일들을 확인하세요:")
    print(f"   - test_results/performance_comparison.png: 모델별 성능 비교")
    print(f"   - test_results/detailed_performance_analysis.png: 상세 성능 분석")

def print_performance_summary(all_performance_summaries, dummy_performance_results):
    """
    성능 요약을 출력하는 함수
    """
    print("\n" + "="*80)
    print("📊 성능 분석 결과 요약")
    print("="*80)
    
    # 모델별 성능 요약
    print("\n🔍 모델별 성능 비교:")
    print("-" * 60)
    print(f"{'Model':<20} {'FPS':<8} {'Inference(ms)':<15} {'Memory(%)':<12} {'Total Time(s)':<15}")
    print("-" * 60)
    
    for model_path, summary in all_performance_summaries.items():
        model_name = os.path.basename(model_path).replace('.pt', '')
        fps = summary.get('avg_fps', 0)
        inference_time = summary.get('avg_inference_time', 0) * 1000
        memory = summary.get('avg_memory_usage', 0)
        total_time = summary.get('total_processing_time', 0)
        
        print(f"{model_name:<20} {fps:<8.1f} {inference_time:<15.1f} {memory:<12.1f} {total_time:<15.1f}")
    
    # 더미 데이터 성능
    if dummy_performance_results:
        print("\n🧪 더미 데이터 성능 테스트:")
        print("-" * 60)
        print(f"{'Model':<20} {'FPS':<8} {'Inference(ms)':<15} {'Memory(%)':<12}")
        print("-" * 60)
        
        for model_path, result in dummy_performance_results.items():
            model_name = os.path.basename(model_path).replace('.pt', '')
            fps = result.get('fps', 0)
            inference_time = result.get('avg_inference_time', 0) * 1000
            memory = result.get('memory_stats', {}).get('avg_memory', 0)
            
            print(f"{model_name:<20} {fps:<8.1f} {inference_time:<15.1f} {memory:<12.1f}")
    
    # 최고 성능 모델 찾기
    best_fps_model = max(all_performance_summaries.items(), key=lambda x: x[1].get('avg_fps', 0))
    best_inference_model = min(all_performance_summaries.items(), key=lambda x: x[1].get('avg_inference_time', float('inf')))
    best_memory_model = min(all_performance_summaries.items(), key=lambda x: x[1].get('avg_memory_usage', float('inf')))
    
    print(f"\n🏆 최고 성능 모델:")
    print(f"   - 최고 FPS: {os.path.basename(best_fps_model[0])} ({best_fps_model[1].get('avg_fps', 0):.1f} FPS)")
    print(f"   - 최고 추론 속도: {os.path.basename(best_inference_model[0])} ({best_inference_model[1].get('avg_inference_time', 0)*1000:.1f}ms)")
    print(f"   - 최저 메모리 사용: {os.path.basename(best_memory_model[0])} ({best_memory_model[1].get('avg_memory_usage', 0):.1f}%)")
    
    # 시스템 정보
    print(f"\n💻 시스템 정보:")
    print(f"   - Device: {device}")
    print(f"   - CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   - GPU: {torch.cuda.get_device_name()}")
        print(f"   - GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

if __name__ == "__main__":
    model_paths = [
        "saved_models/L2A.pt",
        "saved_models/L2BA.pt",
        "saved_models/L2P.pt",
        "saved_models/L2PL.pt",
        "saved_models/L3.pt",
        "saved_models/L3DU.pt",
        "saved_models/SG.pt",
        "saved_models/SGB.pt",
        "saved_models/SGQ.pt",
    ]
    pose_model = YOLO('yolov8n-pose.pt')
    test_dir = "/home/koo4802/Desktop/test_videos"

    # 성능 측정 모드 활성화
    MEASURE_PERFORMANCE = True
    TEST_DUMMY_DATA = True
    
    print("🚀 이상 행위 감지 모델 성능 테스트 시작")
    print(f"📁 테스트 디렉토리: {test_dir}")
    print(f"🔧 성능 측정: {'활성화' if MEASURE_PERFORMANCE else '비활성화'}")
    print(f"🧪 더미 데이터 테스트: {'활성화' if TEST_DUMMY_DATA else '비활성화'}")
    print(f"💻 사용 디바이스: {device}")
    
    all_results = {}
    all_performance_summaries = {}
    dummy_performance_results = {}
    
    for model_path in model_paths:
        print(f"\n{'='*60}")
        print(f"🔍 모델 평가 중: {os.path.basename(model_path)}")
        print(f"{'='*60}")
        
        # 모델 로드
        model = load_model(model_path)
        
        # 더미 데이터 성능 테스트
        if TEST_DUMMY_DATA:
            dummy_result = test_dummy_data_performance(model, num_sequences=200, sequence_length=15)
            dummy_performance_results[model_path] = dummy_result
        
        # 실제 비디오 데이터 처리
        if MEASURE_PERFORMANCE:
            results, performance_summary = process_directory(
                model, test_dir, pose_model, threshold=0.5, frame_interval=1, 
                measure_performance=True
            )
            all_performance_summaries[model_path] = performance_summary
        else:
            results = process_directory(
                model, test_dir, pose_model, threshold=0.5, frame_interval=1, 
                measure_performance=False
            )
        
        all_results[model_path] = results
        
        # 개별 모델 결과 요약
        if results:
            total = len(results)
            correct = sum(1 for r in results if r['true_label'] == r['predicted_label'])
            accuracy = correct / total if total > 0 else 0
            print(f"✅ {os.path.basename(model_path)} 처리 완료")
            print(f"   - 정확도: {accuracy:.2%} ({correct}/{total})")
            if MEASURE_PERFORMANCE and performance_summary:
                print(f"   - 평균 FPS: {performance_summary.get('avg_fps', 0):.1f}")
                print(f"   - 평균 추론 시간: {performance_summary.get('avg_inference_time', 0)*1000:.1f}ms")
        
        # 메모리 정리
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # 성능 요약 출력
    if MEASURE_PERFORMANCE and all_performance_summaries:
        print_performance_summary(all_performance_summaries, dummy_performance_results)
        
        # 성능 시각화
        visualize_performance_results(all_results, all_performance_summaries, dummy_performance_results)

    # 기존 정확도 비교 그래프
    model_names = list(all_results.keys())
    accuracies = []
    for model_path, results in all_results.items():
        total = len(results)
        correct = sum(1 for r in results if r['true_label'] == r['predicted_label'])
        acc = correct / total if total > 0 else 0
        accuracies.append(acc)
    short_names = [os.path.basename(name).replace('.pt', '') for name in model_names]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(short_names, accuracies, color='lightblue', alpha=0.8)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Model Accuracy Comparison', fontsize=14, pad=20)
    plt.ylim(0, 1)
    
    # 막대 위에 정확도 표시
    for bar, acc in zip(bars, accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.2%}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('test_results/model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n🎉 모든 테스트 완료!")
    print(f"📊 결과 파일들:")
    print(f"   - test_results/model_comparison.png: 모델별 정확도 비교")
    if MEASURE_PERFORMANCE:
        print(f"   - test_results/performance_comparison.png: 모델별 성능 비교")
        print(f"   - test_results/detailed_performance_analysis.png: 상세 성능 분석")
    print(f"   - test_results/*_scores.png: 개별 비디오 이상 점수 그래프") 