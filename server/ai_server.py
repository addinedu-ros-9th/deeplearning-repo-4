# ai_server.py
import socket
import threading
import cv2
import numpy as np
import time
import struct
import torch
from ultralytics import YOLO
from collections import deque
import torch.nn.functional as F
import sys
import os

# ai_server.py가 있는 디렉토리의 부모 디렉토리를 경로에 추가
# 이렇게 하면 deeplearning-repo-4 폴더를 기준으로 anomaly_detection 모듈을 찾을 수 있음
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from anomaly_detection import AnomalyDetector


# --- 모델 및 디바이스 설정 ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"[AI 서버] 사용 디바이스: {device}")

def load_anomaly_model(model_path):
    """이상 행동 탐지 모델 로드"""
    model = AnomalyDetector()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

# 모델 경로 설정
anomaly_model_path = "/home/ckim/dev_ws/project_ws/mldl_project/model/actual_anomaly_detector.pth"
pose_model_path = 'yolov8n-pose.pt'

print("[AI 서버] 모델 로딩 중...")
anomaly_model = load_anomaly_model(anomaly_model_path)
pose_model = YOLO(pose_model_path)
print("[AI 서버] 모델 로딩 완료!")

# --- 이상 행동 탐지 관련 설정 ---
sequence_length = 15
joints_sequence = deque(maxlen=sequence_length)
label_names = ["Normal", "Theft", "Abandon", "Broken"]
pred_buffer = deque(maxlen=7) # 7프레임 동안의 예측을 저장하여 안정성 확보
last_stable_prediction = 0 # 가장 마지막의 안정된 예측 (기본값: Normal)
last_probs = None # 마지막 확률 값 저장


def extract_joints(frame, pose_model):
    """프레임에서 관절점 추출"""
    try:
        # 모델 학습 시 정규화 방식과 동일하게 256x256 기준으로 정규화
        results = pose_model(cv2.resize(frame, (256, 256)), verbose=False)[0]
        if results.keypoints is not None and len(results.keypoints) > 0:
            keypoints = results.keypoints[0].data[0].cpu().numpy()
            
            # 원본 프레임 비율에 맞게 keypoints 좌표 복원
            orig_h, orig_w = frame.shape[:2]
            keypoints_orig = np.copy(keypoints)
            keypoints_orig[:, 0] = keypoints[:, 0] * (orig_w / 256.0)
            keypoints_orig[:, 1] = keypoints[:, 1] * (orig_h / 256.0)

            joints = np.zeros(17 * 4)
            for i, kp in enumerate(keypoints):
                if i < 17:
                    joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
            return joints, keypoints_orig
        return np.zeros(17 * 4), None
    except Exception as e:
        print(f"[AI 서버] 관절점 추출 오류: {e}")
        return np.zeros(17 * 4), None

def draw_predictions(frame, probs, current_prediction):
    """프레임에 예측 결과를 왼쪽 위에 상세히 표시 (realtime_webcam.py 스타일)"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 150), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    prediction_label = label_names[current_prediction] if current_prediction is not None else "Detecting"
    
    cv2.putText(frame, f"Prediction: {prediction_label}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    if probs is not None:
        y_offset = 70
        max_prob_idx = np.argmax(probs)
        for i, (label, prob) in enumerate(zip(label_names, probs)):
            color = (0, 0, 255) if i == max_prob_idx else (200, 200, 200)
            thickness = 2 if i == max_prob_idx else 1
            text = f"{label}: {prob:.3f}"
            if i == max_prob_idx:
                 text += " (MAX)"
            cv2.putText(frame, text, (20, y_offset + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
    return frame

def draw_keypoints(frame, keypoints):
    """프레임에 관절점 시각화"""
    if keypoints is not None:
        for kp in keypoints[:17]:
            if len(kp) >= 3 and kp[2] > 0.1: # confidence > 0.1
                x, y = int(kp[0]), int(kp[1])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    return frame


# --- 네트워크 설정 ---
# UDP 수신
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

# TCP 송신
CENTRAL_IP = "192.168.0.21"
CENTRAL_PORT = 6006
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TCP 연결 시도
while True:
    try:
        print(f"[AI 서버] 중앙 서버({CENTRAL_IP}:{CENTRAL_PORT})에 연결 시도 중...")
        tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))
        print("[AI 서버] 중앙 서버에 연결 성공!")
        break
    except socket.error as e:
        print(f"[AI 서버] 연결 실패: {e}. 5초 후 재시도합니다.")
        time.sleep(5)


# 프레임 재조립을 위한 버퍼
frame_buffers = {}  # {frame_id: {packet_idx: data, ...}}

print(f"[AI서버] CCTV 클라이언트로부터 UDP 수신 대기 중... (Port: {UDP_PORT})")

def reassemble_frame(frame_id, packets_info):
    """패킷들을 재조립하여 완전한 프레임 생성"""
    num_packets = packets_info['num_packets']
    packets = packets_info['packets']
    
    # 모든 패킷이 수신되었는지 확인
    if len(packets) != num_packets:
        return None
    
    # 패킷들을 순서대로 결합
    frame_data = b''
    for i in range(num_packets):
        if i in packets:
            frame_data += packets[i]
        else:
            print(f"[AI 서버] 프레임 {frame_id}의 패킷 {i}번 누락됨.")
            return None  # 패킷 누락
    
    return frame_data

# AI 서버 화면 설정
cv2.namedWindow("AI Server - Processed Frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow("AI Server - Processed Frame", 1280, 720)

while True:
    try:
        data, addr = udp_sock.recvfrom(65536)
        
        if len(data) < 16:
            continue
        
        header = data[:16]
        frame_id, packet_idx, num_packets, data_size = struct.unpack('!IIII', header)
        packet_data = data[16:16+data_size]
        
        if frame_id not in frame_buffers:
            frame_buffers[frame_id] = {'num_packets': num_packets, 'packets': {}}
        
        frame_buffers[frame_id]['packets'][packet_idx] = packet_data
        
        if len(frame_buffers[frame_id]['packets']) == num_packets:
            complete_frame_data = reassemble_frame(frame_id, frame_buffers[frame_id])
            
            if complete_frame_data:
                # 1. 프레임 디코딩
                nparr = np.frombuffer(complete_frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    print(f"[AI 서버] 프레임 {frame_id} 디코딩 실패.")
                    del frame_buffers[frame_id]
                    continue
                
                # 2. AI 모델 추론
                joints, keypoints = extract_joints(frame, pose_model)
                current_prediction = None
                
                if keypoints is not None:
                    joints_sequence.append(joints)
                    if len(joints_sequence) == sequence_length:
                        input_tensor = torch.FloatTensor(list(joints_sequence)).unsqueeze(0).to(device)
                        with torch.no_grad():
                            logits = anomaly_model(input_tensor)
                            probs = F.softmax(logits[:, -1, :], dim=-1).cpu().numpy()[0]
                        
                        last_probs = probs # 확률 저장
                        current_prediction = np.argmax(probs)
                        pred_buffer.append(current_prediction)
                else:
                    # 사람이 탐지되지 않으면 버퍼를 초기화하고 Normal로 간주
                    pred_buffer.clear()
                    pred_buffer.append(0) 

                # 3. 안정적인 예측 결정 (민감도 조절)
                # 버퍼가 가득 차고, 모든 예측이 동일하며, Normal이 아닐 때만 안정적인 예측으로 간주
                if len(pred_buffer) == 7 and len(set(pred_buffer)) == 1:
                    last_stable_prediction = pred_buffer[0]
                
                # 4. 결과 시각화
                # 키포인트 먼저 그리기
                processed_frame = draw_keypoints(frame.copy(), keypoints)
                # 그 위에 예측 결과 텍스트 표시
                processed_frame = draw_predictions(processed_frame, last_probs, last_stable_prediction)
                
                # 5. 처리된 프레임을 중앙 서버로 전송
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if ret:
                    encoded_frame = buffer.tobytes()
                    tcp_sock.sendall(struct.pack('!I', len(encoded_frame)) + encoded_frame)
                
                # 6. AI 서버 화면에 표시
                cv2.imshow("AI Server - Processed Frame", processed_frame)

            # 완성된 프레임 버퍼 삭제
            del frame_buffers[frame_id]
        
        # 오래된 프레임 버퍼 정리
        current_frame_id = max(frame_buffers.keys()) if frame_buffers else 0
        old_frames = [fid for fid in frame_buffers.keys() if fid < current_frame_id - 10]
        for old_frame in old_frames:
            del frame_buffers[old_frame]
        
        if cv2.waitKey(1) == 27: # ESC 키 누르면 종료
            break

    except Exception as e:
        print(f"[AI 서버] 메인 루프 오류: {e}")
        # TCP 연결이 끊어졌을 경우 재연결 시도
        if isinstance(e, (BrokenPipeError, ConnectionResetError)):
            print("[AI 서버] TCP 연결이 끊어졌습니다. 재연결을 시도합니다...")
            tcp_sock.close()
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))
                    print("[AI 서버] 중앙 서버에 재연결 성공!")
                    break
                except socket.error as se:
                    print(f"[AI 서버] 재연결 실패: {se}. 5초 후 재시도합니다.")
                    time.sleep(5)

print("[AI 서버] 종료 중...")
tcp_sock.close()
udp_sock.close()
cv2.destroyAllWindows()