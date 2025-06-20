import torch
import cv2
import numpy as np
from anomaly_detection import AnomalyDetector
from ultralytics import YOLO
import torch.nn.functional as F
from collections import deque, Counter
import time
import datetime
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_path):
    """모델 로드 함수"""
    model = AnomalyDetector()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def extract_joints(frame, pose_model):
    """프레임에서 관절점 추출"""
    try:
        results = pose_model(frame, verbose=False)[0]
        if results.keypoints is not None and len(results.keypoints) > 0:
            keypoints = results.keypoints[0].data[0].cpu().numpy()
            joints = np.zeros(17 * 4)
            for i, kp in enumerate(keypoints):
                if i < 17:
                    joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
            return joints, keypoints
        else:
            return np.zeros(17 * 4), None
    except Exception as e:
        print(f"Error processing frame: {e}")
        return np.zeros(17 * 4), None

def draw_predictions(frame, probs, current_prediction, fps=None):
    """프레임에 예측 결과를 왼쪽 위에 표시"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    label_names = ["Normal", "Theft", "Abandon", "Broken"]
    cv2.putText(frame, f"Prediction: {label_names[current_prediction]}", 
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y_offset = 80
    max_prob_idx = np.argmax(probs)
    for i, (label, prob) in enumerate(zip(label_names, probs)):
        if i == max_prob_idx:
            color = (0, 0, 255)
            cv2.putText(frame, f"{label}: {prob:.3f} (MAX)", 
                        (20, y_offset + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
            color = (200, 200, 200)
            cv2.putText(frame, f"{label}: {prob:.3f}", 
                        (20, y_offset + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame

def realtime_anomaly_detection(model_path="transfer_learned_model.pth", 
                              pose_model_path='yolov8n-pose.pt',
                              sequence_length=15):
    """실시간 웹캠 이상 감지 (정확히 5fps, test_anormaly.py와 동일한 예측 방식)"""
    print("Loading models...")
    model = load_model(model_path)
    pose_model = YOLO(pose_model_path)
    print("Models loaded successfully!")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    joints_sequence = deque(maxlen=sequence_length)
    print("Starting real-time anomaly detection at 5fps...")
    print("Press 'q' to quit, 'r' to reset sequence")
    fps = 5
    frame_interval = 1.0 / fps
    last_frame_time = time.time()
    video_buffer = deque(maxlen=45)
    pred_buffer = deque(maxlen=7)
    saving = False
    save_countdown = 0
    out = None
    filename = None
    detected_action = None
    last_saved_action = None
    prev_prediction = None
    clip_predictions = []
    try:
        while True:
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                continue
            last_frame_time = current_time

            current_prediction = None

            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            joints, keypoints = extract_joints(frame, pose_model)
            has_person = False
            if keypoints is not None:
                for kp in keypoints[:17]:
                    if len(kp) >= 3:
                        x, y, conf = kp[0], kp[1], kp[2]
                        if conf > 0.1:
                            has_person = True
                            cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
            if has_person:
                joints_sequence.append(joints)
                if len(joints_sequence) >= sequence_length:
                    input_tensor = torch.FloatTensor(list(joints_sequence)).unsqueeze(0).to(device)
                    with torch.no_grad():
                        logits = model(input_tensor)
                        probs = F.softmax(logits[:, -1, :], dim=-1).cpu().numpy()[0]
                    current_prediction = np.argmax(probs)
                    frame = draw_predictions(frame, probs, current_prediction, None)
                    joints_sequence.popleft()
                else:
                    remaining = sequence_length - len(joints_sequence)
                    cv2.putText(frame, f"Collecting data... ({remaining} frames left)", 
                                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                cv2.putText(frame, "No person detected", 
                            (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                pass
            video_buffer.append(frame.copy())
            if current_prediction is not None:
                if prev_prediction is not None and current_prediction != prev_prediction:
                    pred_buffer.clear()
                pred_buffer.append(current_prediction)
                prev_prediction = current_prediction
                frame = draw_predictions(frame, probs, current_prediction, None)
            if (
                len(pred_buffer) == 7 and
                len(set(pred_buffer)) == 1 and
                pred_buffer[0] != 0 and
                not saving and
                pred_buffer[0] != last_saved_action
            ):
                saving = True
                save_countdown = 45
                detected_action = list(set(pred_buffer))[0]
                last_saved_action = detected_action
                dt_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                action_name = ["Normal", "Theft", "Abandon", "Broken"][detected_action]
                filename = f"{action_name}_{dt_str}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                height, width = frame.shape[:2]
                out = cv2.VideoWriter(filename, fourcc, 5, (width, height))
                print(f"Started saving clip: {filename}")
            if saving:
                out.write(frame)
                if current_prediction is not None:
                    clip_predictions.append(current_prediction)
                save_countdown -= 1
                if save_countdown == 0:
                    out.release()
                    saving = False
                    # Normal(0)과 None 제외한 다수결
                    abnormal_preds = [p for p in clip_predictions if p not in (0, None)]
                    if abnormal_preds:
                        major_action = Counter(abnormal_preds).most_common(1)[0][0]
                        action_name = ["Normal", "Theft", "Abandon", "Broken"][major_action]
                        new_filename = f"{action_name}_{dt_str}.mp4"
                        os.rename(filename, new_filename)
                        print(f"Clip saved: {new_filename}")
                    else:
                        os.remove(filename)
                        print("Clip was mostly Normal, so it was deleted.")
                    last_saved_action = None
                    clip_predictions = []
            cv2.imshow('Real-time Anomaly Detection', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('r'):
                print("Resetting sequence...")
                joints_sequence.clear()
                video_buffer.clear()
                pred_buffer.clear()
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                snapname = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(snapname, frame)
                print(f"Screenshot saved as {snapname}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if out is not None and saving:
            out.release()
        print("Webcam released")

if __name__ == "__main__":
    model_path = "/home/ckim/dev_ws/project_ws/deeplearning-repo-4/saved_models/추가학습패딩없이(최고).pth"
    realtime_anomaly_detection(model_path=model_path) 