import cv2
import torch
import torch.nn as nn
import numpy as np
import mediapipe as mp
from collections import deque, Counter
import math
from ultralytics import YOLO
import os

# --- 1. 모델 클래스 정의 (학습 때와 동일한 구조) ---
class BehaviorLSTM(nn.Module):
    def __init__(self, input_size=113, hidden_size=256, num_layers=2, num_classes=4, dropout=0.5):
        super(BehaviorLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_classes)
        )

    def forward(self, x):
        # LSTM에 배치 차원 추가
        if x.dim() == 2:
            x = x.unsqueeze(0)
        # LSTM에 시퀀스 길이 차원 추가
        if x.dim() == 3 and x.shape[1] != 30: # (batch, features) -> (batch, seq, features)
             x = x.unsqueeze(1)

        out, _ = self.lstm(x)
        out = out[:, -1, :]
        
        # BatchNorm1d는 (N, C) 형태의 입력을 기대하므로 차원 확인
        if out.dim() == 1:
            out = out.unsqueeze(0)
            
        out = self.fc_layers(out)
        return out

# --- 2. 특징 추출 헬퍼 함수들 (학습 코드에서 가져옴) ---
def get_objects(img, yolo_model):
    """YOLO로 가방류 객체만 감지"""
    results = yolo_model(img, verbose=False)
    objects = []
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                cls = int(box.cls)
                conf = float(box.conf)
                # COCO 데이터셋 기준: 24=backpack, 26=handbag, 28=suitcase
                if cls in [24, 26, 28] and conf > 0.5:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    box_area = (x2 - x1) * (y2 - y1)
                    img_area = img.shape[0] * img.shape[1]
                    if box_area > img_area * 0.01:
                        objects.append([x1, y1, x2, y2, conf, cls])
    return objects

def find_nearest_objects(pose_keypoints, objects, img_width, img_height):
    """손목과 가장 가까운 객체 2개 찾기"""
    if len(pose_keypoints) < 99: return []
    
    left_wrist_x = pose_keypoints[15 * 3] * img_width
    left_wrist_y = pose_keypoints[15 * 3 + 1] * img_height
    right_wrist_x = pose_keypoints[16 * 3] * img_width
    right_wrist_y = pose_keypoints[16 * 3 + 1] * img_height
    
    near_objects = []
    for obj in objects:
        x1, y1, x2, y2, conf, cls = obj
        obj_center_x = (x1 + x2) / 2
        obj_center_y = (y1 + y2) / 2
        obj_width = x2 - x1
        obj_height = y2 - y1
        
        left_dist = math.sqrt((left_wrist_x - obj_center_x)**2 + (left_wrist_y - obj_center_y)**2)
        right_dist = math.sqrt((right_wrist_x - obj_center_x)**2 + (right_wrist_y - obj_center_y)**2)
        min_dist = min(left_dist, right_dist)
        
        diagonal = math.sqrt(img_width**2 + img_height**2)
        if min_dist < diagonal * 0.3:
            near_objects.append([
                obj_center_x / img_width, obj_center_y / img_height,
                obj_width / img_width, obj_height / img_height,
                conf, float(cls), min_dist / diagonal
            ])
            
    near_objects.sort(key=lambda x: x[6])
    return near_objects[:2]

def extract_features_realtime(img, pose_model, yolo_model):
    """
    실시간으로 113개 특징을 추출하고, 사람 감지 여부를 함께 반환합니다.
    """
    img_height, img_width = img.shape[:2]
    person_detected = False  # 사람 감지 플래그

    # 1. 포즈 키포인트 추출 (99개)
    pose_features = [0.0] * 99
    results = pose_model.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        person_detected = True # 사람이 감지됨
        pose_features = [v for landmark in results.pose_landmarks.landmark for v in (landmark.x, landmark.y, landmark.z)]

    # 사람이 감지된 경우에만 객체 특징을 찾음 (선택적 최적화)
    if person_detected:
        objects = get_objects(img, yolo_model)
        near_objects = find_nearest_objects(pose_features, objects, img_width, img_height)
    else:
        near_objects = []

    # 4. 특징 통합
    all_features = []
    all_features.extend(pose_features)
    for i in range(2):
        if i < len(near_objects):
            all_features.extend(near_objects[i])
        else:
            all_features.extend([0.0] * 7)
            
    return np.array(all_features, dtype=np.float32), person_detected

# --- 3. 메인 실행 함수 (수정) ---
def run_realtime_detection(video_path, model_path, sequence_length=30):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    class_names = ['Normal', 'Theft', 'Broken', 'Abandon']
    
    # 모델 로드
    model = BehaviorLSTM().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print("✅ LSTM 모델 로드 완료")

    # YOLO & MediaPipe 모델 초기화
    yolo_model = YOLO('yolov8n.pt') 
    mp_pose = mp.solutions.pose
    pose_model = mp_pose.Pose()
    print("✅ YOLO & MediaPipe 모델 초기화 완료")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 비디오 파일을 열 수 없습니다: {video_path}")
        return

    # --- 스무딩을 위한 변수 수정 ---
    sequence_data = deque(maxlen=sequence_length)
    prediction_history = deque(maxlen=15)  # 최근 15개 예측 저장
    stable_action = "Detecting..."         # 화면에 표시될 안정된 행동
    display_confidence = 0.0               # 화면에 표시될 신뢰도

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # 사람 감지 여부와 함께 특징 추출
        features, person_detected = extract_features_realtime(frame, pose_model, yolo_model)
        
        # 사람이 없으면, 상태를 'Normal'로 리셋
        if not person_detected:
            stable_action = 'Normal'
            prediction_history.clear() # 예측 기록 초기화
            confidence = 0.0
        else:
            # 사람이 있으면, 기존 로직 수행
            sequence_data.append(features)
            if len(sequence_data) == sequence_length:
                input_tensor = torch.FloatTensor(np.array(sequence_data)).unsqueeze(0).to(device)
                with torch.no_grad():
                    outputs = model(input_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    conf, pred = torch.max(probabilities, 1)
                    
                    # --- 스무딩 로직 적용 ---
                    prediction_history.append(pred.item())
                    display_confidence = conf.item()

                    if len(prediction_history) == prediction_history.maxlen:
                        # 가장 빈번하게 예측된 행동 찾기
                        most_common_action_idx = Counter(prediction_history).most_common(1)[0][0]
                        stable_action = class_names[most_common_action_idx]

        # 시각화 (안정된 예측값 사용)
        box_color = (0, 255, 0) # Normal
        if stable_action in ['Theft', 'Broken', 'Abandon']:
            box_color = (0, 0, 255) # Warning
        
        cv2.rectangle(frame, (10, 10), (450, 90), box_color, -1)
        text = f"Action: {stable_action}"
        conf_text = f"Confidence: {display_confidence:.2f}"
        cv2.putText(frame, text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, conf_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        cv2.imshow('Real-time Behavior Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pose_model.close()

# --- 5. 텍스트 리포트용 평가 함수 (수정) ---
def evaluate_and_report(video_path, model_path, sequence_length=30):
    """
    비디오를 화면 출력 없이 분석하고, 예측 정확도를 텍스트로 리포트합니다.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    class_names = ['Normal', 'Theft', 'Broken', 'Abandon']

    # 파일 경로에서 실제 라벨 추정
    true_label = "Unknown"
    for label in class_names:
        if f'/{label.lower()}/' in video_path:
            true_label = label
            break
    
    print(f"\n▶️ 분석 시작: {os.path.basename(video_path)} (실제 라벨: {true_label})")

    # 모델 로드 (YOLO, MediaPipe는 매번 초기화 필요)
    model = BehaviorLSTM().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    yolo_model = YOLO('yolov8n.pt')
    mp_pose = mp.solutions.pose
    pose_model = mp_pose.Pose()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ❌ 비디오 파일을 열 수 없습니다.")
        return

    sequence_data = deque(maxlen=sequence_length)
    predictions = []

    # 화면 출력 없이 비디오 프레임 처리
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 사람 감지 여부와 함께 특징 추출
        features, person_detected = extract_features_realtime(frame, pose_model, yolo_model)
        
        # 사람이 감지된 경우에만 예측을 수행하고 기록
        if person_detected:
            sequence_data.append(features)
            if len(sequence_data) == sequence_length:
                input_tensor = torch.FloatTensor(np.array(sequence_data)).unsqueeze(0).to(device)
                with torch.no_grad():
                    outputs = model(input_tensor)
                    _, pred = torch.max(outputs, 1)
                    predictions.append(class_names[pred.item()])

    cap.release()
    pose_model.close()

    if not predictions:
        print("  -> 예측이 생성되지 않았습니다.")
        return

    # 결과 리포트 출력
    print("  📊 예측 결과 분포:")
    total_predictions = len(predictions)
    prediction_counts = Counter(predictions)

    for action, count in prediction_counts.most_common():
        percentage = (count / total_predictions) * 100
        print(f"    - {action}: {count}회 ({percentage:.2f}%)")

    accuracy = (prediction_counts.get(true_label, 0) / total_predictions) * 100
    print(f"  ✅ 정확도: {accuracy:.2f}% ({total_predictions}개 예측 중 {prediction_counts.get(true_label, 0)}개 정답)")

# --- 6. 스크립트 실행 (모드 선택 기능 추가) ---
if __name__ == '__main__':
    # --- 분석 모드 선택 ---
    # 텍스트 리포트를 보려면 True, 실시간 영상을 보려면 False로 설정하세요.
    RUN_EVALUATION_REPORT = False

    # --- 분석할 비디오 파일 목록 ---
    video_list = [
        "/home/ckim/dev_ws/project_ws/mldl_project/data/videos/normal/val/video/C_2_4_49_BU_SMC_08-20_14-46-36_CA_RGB_DF1_M4.mp4",
        "/home/ckim/dev_ws/project_ws/mldl_project/data/videos/theft/val/video/C_3_12_40_BU_SMC_10-14_11-43-44_CD_RGB_DF2_M2.mp4",
        "/home/ckim/dev_ws/project_ws/mldl_project/data/videos/broken/val/video/C_3_8_53_BU_SMC_10-14_13-30-48_CB_RGB_DF2_F3.mp4",
        "/home/ckim/dev_ws/project_ws/mldl_project/data/videos/abandon/val/video/C_3_11_34_BU_DYA_08-10_16-33-05_CA_RGB_DF2_M2_F2.mp4"
    ]
    
    MODEL_PATH = "/home/ckim/dev_ws/project_ws/mldl_project/src/learning/best_sequential_model.pt"
    
    if RUN_EVALUATION_REPORT:
        print("--- 텍스트 기반 정확도 평가를 시작합니다 ---")
        for video_path in video_list:
            evaluate_and_report(video_path, MODEL_PATH)
        print("\n\n✅ 모든 영상 평가가 완료되었습니다.")
    else:
        print("--- 실시간 영상 분석을 시작합니다 ---")
        for video_path in video_list:
            print(f"\n▶️ 다음 영상 분석 시작: {video_path}")
            run_realtime_detection(video_path, MODEL_PATH)
        print("\n\n✅ 모든 영상 분석이 완료되었습니다.")