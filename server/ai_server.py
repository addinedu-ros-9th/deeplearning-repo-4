import sys
import os
# 이 파일(ai_server.py)의 부모 폴더(server)의 부모 폴더(deeplearning-repo-4)를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import torch
import cv2
import numpy as np
from anomaly_detection import AnomalyDetector
from ultralytics import YOLO
import torch.nn.functional as F
from collections import deque, Counter
import time
import datetime
import socket
import struct
import json
import subprocess

from config import RECIEVER_IP, RECIEVER_PORT, CENTRAL_IP, CENTRAL_PORT, CENTRAL_GUI_IP, CENTRAL_GUI_PORT

# GUI UDP 통신을 위한 설정 추가
GUI_UDP_IP = CENTRAL_GUI_IP  # GUI IP 주소
GUI_UDP_PORT = CENTRAL_GUI_PORT  # GUI UDP 포트

# ai_server.py가 있는 디렉토리의 부모 디렉토리를 경로에 추가
# 이렇게 하면 deeplearning-repo-4 폴더를 기준으로 anomaly_detection 모듈을 찾을 수 있음
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from anomaly_detection import AnomalyDetector

# --- 상수 정의 ---
LABEL_NAMES = ["Normal", "Theft", "Abandon", "Broken"]
CONFIDENCE_THRESHOLD = 0.8
KEYPOINT_CONFIDENCE_THRESHOLD = 0.2
MIN_VALID_KEYPOINTS = 8
MIN_VALID_POINTS_FOR_BBOX = 5
MIN_FACE_KEYPOINTS = 2
BODY_PADDING_RATIO = 0.1
FACE_PADDING_RATIO = 0.2
PREDICTION_BUFFER_SIZE = 10  # 연속성 감지를 위해 증가
VIDEO_BUFFER_SIZE = 45
PRE_BUFFER_SIZE = 15
SAVE_COUNTDOWN = 45
SEQUENCE_LENGTH = 15

# 관절점 연결 정의
LIMB_CONNECTIONS = [
    # 얼굴 연결
    (0, 1), (0, 2), (1, 3), (2, 4),  # 얼굴(눈, 귀)
    (0, 5), (0, 6),  # 어깨
    # 팔 연결
    (5, 7), (7, 9), (6, 8), (8, 10),  # 팔
    # 몸통 연결
    (5, 6), (5, 11), (6, 12), (11, 12),  # 몸통
    # 다리 연결
    (11, 13), (13, 15), (12, 14), (14, 16)  # 다리
]

FACE_KEYPOINT_INDICES = [0, 1, 2, 3, 4]  # 얼굴 관련 키포인트 (코, 눈, 귀)

# --- 모델 및 디바이스 설정 ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tcp_sock = None
gui_udp_sock = None
frame_counter = 0  # 프레임 ID 카운터
last_gui_send_time = 0
GUI_SEND_INTERVAL = 0.33  # 약 3 FPS (1초 / 3 = 0.33초)

def ensure_tcp_connection():
    """TCP 소켓 연결을 확인하고, 끊겼으면 재연결합니다."""
    global tcp_sock
    if tcp_sock:
        # 소켓의 유효성 검사 (간단한 방법)
        try:
            # 소켓 옵션을 확인하여 연결 상태를 간접적으로 체크
            tcp_sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            return True
        except socket.error:
            print("[AI 서버] TCP 연결이 끊어진 것을 확인했습니다. 재연결을 시도합니다.")
            tcp_sock.close()
            tcp_sock = None

    # 소켓이 없거나 끊겼을 경우 새로 연결
    try:
        print(f"[AI 서버] 중앙 서버({CENTRAL_IP}:{CENTRAL_PORT})에 연결 시도 중...")
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))
        print("[AI 서버] 중앙 서버에 연결 성공!")
        return True
    except socket.error as e:
        print(f"[AI 서버] TCP 연결 실패: {e}")
        tcp_sock = None
        return False

def send_frame_tcp(frame):
    """처리된 프레임을 중앙 서버로 전송 (패킷 헤더 형식 사용)"""
    global tcp_sock
    if not ensure_tcp_connection():
        time.sleep(1) # 연결 실패 시 잠시 대기
        return

    try:
        # 프레임을 JPEG로 인코딩
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if result:
            packet_data = encoded_frame.tobytes()
            
            # 패킷 헤더 형식: [timestamp(8bytes), frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
            timestamp = time.time()
            frame_id = int(timestamp * 1000)  # 밀리초 단위로 프레임 ID 생성
            packet_idx = 0  # 단일 패킷이므로 0
            num_packets = 1  # 단일 패킷
            data_size = len(packet_data)
            
            header = struct.pack('!dIIII', timestamp, frame_id, packet_idx, num_packets, data_size)
            packet = header + packet_data
            
            if tcp_sock:
                tcp_sock.sendall(packet)
                print(f"[AI 서버] 프레임 전송: {data_size} bytes")
        else:
            print("[AI 서버] 프레임 인코딩 실패")
    except socket.error as e:
        print(f"[AI 서버] TCP 전송 오류: {e}")
        if tcp_sock:
            tcp_sock.close()
        tcp_sock = None

def send_frame_udp_to_gui(frame):
    """처리된 프레임을 GUI로 UDP 전송 (패킷 분할 방식)"""
    global gui_udp_sock, frame_counter, last_gui_send_time
    
    # 프레임 전송 빈도 제한 (3 FPS)
    current_time = time.time()
    if current_time - last_gui_send_time < GUI_SEND_INTERVAL:
        return
    last_gui_send_time = current_time
    
    # UDP 소켓이 없으면 생성
    if gui_udp_sock is None:
        try:
            gui_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"[AI 서버] GUI UDP 소켓 생성: {GUI_UDP_IP}:{GUI_UDP_PORT}")
        except Exception as e:
            print(f"[AI 서버] GUI UDP 소켓 생성 실패: {e}")
            return

    try:
        # GUI용 해상도 축소 (640x480으로 리사이즈)
        gui_frame = cv2.resize(frame, (640, 480))
        
        # 프레임을 JPEG로 인코딩 (품질 낮춤)
        result, encoded_frame = cv2.imencode('.jpg', gui_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        if result:
            frame_data = encoded_frame.tobytes()
            total_size = len(frame_data)
            
            # 패킷 크기 설정 (cctv_udp_client.py와 동일)
            MAX_PACKET_SIZE = 60000
            num_packets = (total_size + MAX_PACKET_SIZE - 1) // MAX_PACKET_SIZE
            
            # 현재 타임스탬프 기록
            timestamp = time.time()
            frame_id = frame_counter % 0xFFFFFFFF
            
            for packet_idx in range(num_packets):
                start_idx = packet_idx * MAX_PACKET_SIZE
                end_idx = min(start_idx + MAX_PACKET_SIZE, total_size)
                packet_data = frame_data[start_idx:end_idx]
                
                # 패킷 헤더: [timestamp(8bytes), frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
                header = struct.pack('!dIIII', timestamp, frame_id, packet_idx, num_packets, len(packet_data))
                packet = header + packet_data
                
                gui_udp_sock.sendto(packet, (GUI_UDP_IP, GUI_UDP_PORT))
                print(f"[AI 서버] GUI로 UDP 전송: 프레임 {frame_id}, 패킷 {packet_idx+1}/{num_packets}, 크기: {len(packet_data)} bytes")
            
            # 카운터 증가
            frame_counter += 1
        else:
            print("[AI 서버] 프레임 인코딩 실패")
    except Exception as e:
        print(f"[AI 서버] GUI UDP 전송 오류: {e}")

def load_model(model_path):
    """
    모델 로드 함수 - TorchScript 모델도 지원
    """
    if model_path.endswith('.pt') and 'torchscript' in model_path:
        # TorchScript 모델 로드
        print(f"[AI 서버] TorchScript 모델 로딩: {model_path}")
        model = torch.jit.load(model_path, map_location=device)
        model.eval()
    else:
        # 일반 PyTorch 모델 로드
        print(f"[AI 서버] 일반 PyTorch 모델 로딩: {model_path}")
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

def draw_predictions(frame, probs, current_prediction, fps=None):
    """프레임에 예측 결과를 왼쪽 위에 표시"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 220), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.putText(frame, f"Prediction: {LABEL_NAMES[current_prediction]}", 
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y_offset = 80
    max_prob_idx = np.argmax(probs)
    for i, (label, prob) in enumerate(zip(LABEL_NAMES, probs)):
        if i == max_prob_idx:
            color = (0, 0, 255)
            cv2.putText(frame, f"{label}: {prob:.3f} (MAX)", 
                        (20, y_offset + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
            color = (200, 200, 200)
            cv2.putText(frame, f"{label}: {prob:.3f}", 
                        (20, y_offset + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    return frame

def count_valid_persons(keypoints):
    """유효한 사람 수를 계산"""
    if keypoints is None or len(keypoints) == 0:
        return 0
    
    person_count = 0
    for person_idx in range(len(keypoints)):
        valid_keypoints = 0
        for kp_idx in range(len(keypoints[person_idx])):
            if kp_idx < 17 and float(keypoints[person_idx][kp_idx][2]) > KEYPOINT_CONFIDENCE_THRESHOLD:
                valid_keypoints += 1
        
        if valid_keypoints >= MIN_VALID_KEYPOINTS:
            person_count += 1
    
    return person_count

def draw_keypoints_with_color(frame, keypoints, bbox_color=(255, 0, 0)):
    """프레임에 관절점 시각화 및 선으로 연결 (색상 지정 가능)"""
    if keypoints is None or len(keypoints) == 0:
        return frame
    
    # 각 사람별로 처리
    for person_idx in range(len(keypoints)):
        person_kps = keypoints[person_idx]
        
        # 관절점 그리기
        for kp_idx in range(len(person_kps)):
            if kp_idx < 17:  # 17개 키포인트만 처리
                kp = person_kps[kp_idx]
                conf = float(kp[2])  # 신뢰도를 float로 변환
                if conf > 0.1:  # confidence > 0.1
                    x, y = int(kp[0]), int(kp[1])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        # 관절점 연결선 그리기
        for connection in LIMB_CONNECTIONS:
            idx1, idx2 = connection
            if (idx1 < len(person_kps) and idx2 < len(person_kps)):
                conf1 = float(person_kps[idx1][2])
                conf2 = float(person_kps[idx2][2])
                if conf1 > KEYPOINT_CONFIDENCE_THRESHOLD and conf2 > KEYPOINT_CONFIDENCE_THRESHOLD:
                    pt1 = (int(person_kps[idx1][0]), int(person_kps[idx1][1]))
                    pt2 = (int(person_kps[idx2][0]), int(person_kps[idx2][1]))
                    # 0,0 좌표에 연결되는 것 방지
                    if pt1[0] > 10 and pt1[1] > 10 and pt2[0] > 10 and pt2[1] > 10:
                        cv2.line(frame, pt1, pt2, (0, 255, 255), 2)
        
        # 바운딩 박스 그리기
        valid_points = []
        for kp_idx in range(len(person_kps)):
            if kp_idx < 17:
                conf = float(person_kps[kp_idx][2])
                if conf > KEYPOINT_CONFIDENCE_THRESHOLD:
                    x, y = int(person_kps[kp_idx][0]), int(person_kps[kp_idx][1])
                    # 0,0 근처 좌표 제외
                    if x > 10 and y > 10:
                        valid_points.append((x, y))
        
        if len(valid_points) >= MIN_VALID_POINTS_FOR_BBOX:
            x_coords = [p[0] for p in valid_points]
            y_coords = [p[1] for p in valid_points]
            
            # 전체 사람 바운딩 박스
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # 패딩 추가
            width = x_max - x_min
            height = y_max - y_min
            x_min = max(0, x_min - int(width * BODY_PADDING_RATIO))
            y_min = max(0, y_min - int(height * BODY_PADDING_RATIO))
            x_max = min(frame.shape[1], x_max + int(width * BODY_PADDING_RATIO))
            y_max = min(frame.shape[0], y_max + int(height * BODY_PADDING_RATIO))
            
            # 사람 전체 바운딩 박스 그리기
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), bbox_color, 2)
            
            # 얼굴 바운딩 박스 그리기
            face_keypoints = []
            for idx in FACE_KEYPOINT_INDICES:
                if idx < len(person_kps):
                    conf = float(person_kps[idx][2])
                    if conf > KEYPOINT_CONFIDENCE_THRESHOLD:
                        x, y = int(person_kps[idx][0]), int(person_kps[idx][1])
                        if x > 10 and y > 10:
                            face_keypoints.append((x, y))
            
            if len(face_keypoints) >= MIN_FACE_KEYPOINTS:
                face_x_coords = [p[0] for p in face_keypoints]
                face_y_coords = [p[1] for p in face_keypoints]
                
                face_x_min, face_x_max = min(face_x_coords), max(face_x_coords)
                face_y_min, face_y_max = min(face_y_coords), max(face_y_coords)
                
                # 얼굴 패딩 추가
                face_width = face_x_max - face_x_min
                face_height = face_y_max - face_y_min
                face_x_min = max(0, face_x_min - int(face_width * FACE_PADDING_RATIO))
                face_y_min = max(0, face_y_min - int(face_height * FACE_PADDING_RATIO))
                face_x_max = min(frame.shape[1], face_x_max + int(face_width * FACE_PADDING_RATIO))
                face_y_max = min(frame.shape[0], face_y_max + int(face_height * FACE_PADDING_RATIO))
                
                # 얼굴 바운딩 박스 그리기 (빨간색)
                cv2.rectangle(frame, (face_x_min, face_y_min), (face_x_max, face_y_max), (0, 0, 255), 2)
    
    return frame

def draw_keypoints(frame, keypoints):
    """기본 키포인트 시각화 (파란색 바운딩 박스)"""
    return draw_keypoints_with_color(frame, keypoints, (255, 0, 0))

def setup_udp_socket(udp_ip, udp_port):
    """UDP 소켓을 설정하고 지정된 IP와 포트에 바인딩합니다."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    sock.settimeout(2.0)  # 수신 대기 시간 초과를 2초로 설정
    print(f"UDP 서버가 {udp_ip}:{udp_port}에서 수신 대기 중입니다.")
    return sock

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
            print(f"프레임 {frame_id}의 패킷 {i}번 누락됨.")
            return None  # 패킷 누락
    
    return frame_data

def receive_frame_udp_packetized(sock):
    """패킷 분할 방식으로 UDP 프레임 수신 (cctv_udp_client.py 호환)"""
    try:
        data, addr = sock.recvfrom(65536)
        
        if len(data) < 24: # 헤더 크기 변경: 8(double) + 4*4 = 24
            return None
        
        # 패킷 헤더 파싱: [timestamp(8bytes), frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
        header = data[:24]
        timestamp, frame_id, packet_idx, num_packets, data_size = struct.unpack('!dIIII', header)
        packet_data = data[24:24+data_size]
        
        return {
            'timestamp': timestamp,
            'frame_id': frame_id,
            'packet_idx': packet_idx,
            'num_packets': num_packets,
            'packet_data': packet_data,
            'addr': addr
        }
    except socket.timeout:
        return None
    except Exception as e:
        print(f"UDP 수신 오류: {e}")
        return None

def get_consecutive_abnormal_label(framewise_preds, consecutive_threshold=5):
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

def process_prediction_buffer(pred_buffer, current_prediction, prev_prediction):
    """예측 버퍼 처리 - 연속성 기반으로 개선"""
    if current_prediction is not None:
        if prev_prediction is not None and current_prediction != prev_prediction:
            pred_buffer.clear()
        pred_buffer.append(current_prediction)
        prev_prediction = current_prediction
    return prev_prediction

def should_start_saving(pred_buffer, saving, last_saved_action, light_off_frame_count, light_off_min_frames):
    """저장 시작 조건 확인 - 연속성 기반으로 개선"""
    # Light OFF 기반 저장 조건
    light_off_condition = (
        light_off_frame_count >= light_off_min_frames and
        not saving and
        "light_off" != last_saved_action
    )
    
    # 연속성 기반 AI 예측 저장 조건
    if len(pred_buffer) >= 5:  # 최소 5프레임 필요
        consecutive_action = get_consecutive_abnormal_label(list(pred_buffer), consecutive_threshold=5)
        ai_condition = (
            consecutive_action != 0 and  # Normal이 아닌 행위가 연속 감지
            not saving and
            consecutive_action != last_saved_action
        )
    else:
        ai_condition = False
    
    return ai_condition or light_off_condition

def create_video_writer(filename, frame_shape):
    """비디오 라이터 생성"""
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    height, width = frame_shape[:2]
    return cv2.VideoWriter(filename, fourcc, 5, (width, height))

def add_recording_overlay(frame, text="Recording..."):
    """녹화 중임을 표시하는 오버레이 추가"""
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_x = frame.shape[1] - text_size[0] - 20  # 오른쪽 정렬, 여백 20px
    cv2.putText(frame, text, 
                (text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.circle(frame, (frame.shape[1] - 30, 30), 15, (0, 0, 255), -1)  # 빨간 녹화 표시

def process_pre_buffer_frames(pre_buffer_frames, pose_model, out, current_clip_max_persons):
    """이전 버퍼 프레임들 처리"""
    for i, pre_frame in enumerate(pre_buffer_frames):
        vis_frame = pre_frame.copy()
        
        try:
            # 키포인트 추출 및 시각화
            pre_joints, pre_keypoints = extract_joints(vis_frame, pose_model)
            pre_person_count = count_valid_persons(pre_keypoints)
            
            # 클립 내 최대 사람 수 업데이트
            if pre_person_count > current_clip_max_persons:
                current_clip_max_persons = pre_person_count
            
            # 키포인트 시각화
            if pre_keypoints is not None:
                vis_frame = draw_keypoints(vis_frame, pre_keypoints)
        except Exception as e:
            pass  # 에러 무시
        
        # 녹화 표시 추가
        text = f"Recording... (pre-buffer {i+1}/{len(pre_buffer_frames)})"
        add_recording_overlay(vis_frame, text)
        out.write(vis_frame)
    
    return current_clip_max_persons

def detect_light_off(frame, prev_brightness):
    """프레임의 밝기를 기반으로 전등 끔 상태를 감지"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    curr_brightness = np.mean(gray)
    status = "Normal"
    if curr_brightness < 80:
        status = "Light OFF"
    elif prev_brightness is not None and (prev_brightness - curr_brightness) > 10:
        status = "Light OFF (Change)"
    return curr_brightness, status

def send_notification(event_type, person_count, confidence_str):
    """
    GUI로 UDP를 통해 알림 전송
    
    Args:
        event_type (str): 이벤트 타입 ("Light_OFF", "Theft", "Broken", "Abandon")
        person_count (int): 사람 수
        confidence_str (str): 신뢰도
    """
    global gui_udp_sock
    
    # GUI로 UDP 알림 전송
    if gui_udp_sock is None:
        try:
            gui_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"[AI 서버] GUI 알림 UDP 소켓 생성: {GUI_UDP_IP}:{GUI_UDP_PORT}")
        except Exception as e:
            print(f"[AI 서버] GUI 알림 UDP 소켓 생성 실패: {e}")
            return

    try:
        # 알림 데이터 생성
        notification_data = {
            'type': 'notification',
            'event_type': event_type,
            'person_count': person_count,
            'confidence': confidence_str,
            'timestamp': time.time()
        }
        
        # JSON으로 인코딩
        notification_json = json.dumps(notification_data).encode('utf-8')
        
        # 패킷 헤더 추가
        timestamp = time.time()
        frame_id = 0  # 알림용 특별 ID
        packet_idx = 0
        num_packets = 1
        data_size = len(notification_json)
        
        header = struct.pack('!dIIII', timestamp, frame_id, packet_idx, num_packets, data_size)
        packet = header + notification_json
        
        gui_udp_sock.sendto(packet, (GUI_UDP_IP, GUI_UDP_PORT))
        print(f"[AI 서버] GUI로 알림 전송: {event_type} (사람 수: {person_count}, 신뢰도: {confidence_str})")
        
    except Exception as e:
        print(f"[AI 서버] GUI 알림 전송 오류: {e}")

def realtime_anomaly_detection(model_path, pose_model_path='yolov8n-pose.pt', sequence_length=SEQUENCE_LENGTH, udp_ip="0.0.0.0", udp_port=5005):
    """실시간 UDP 스트림 이상 감지 (cctv_udp_client.py와 호환)"""
    print("Loading models...")
    model = load_model(model_path)
    pose_model = YOLO(pose_model_path)
    print("Models loaded successfully!")
    
    # UDP 소켓 설정
    sock = setup_udp_socket(udp_ip, udp_port)
    
    # 프레임 재조립을 위한 버퍼
    frame_buffers = {}  # {frame_id: {packet_idx: data, ...}}
    
    joints_sequence = deque(maxlen=sequence_length)
    print("Starting real-time anomaly detection from UDP stream at 5fps...")
    print("Press 'q' to quit, 'r' to reset sequence")
    
    video_buffer = deque(maxlen=VIDEO_BUFFER_SIZE)
    pred_buffer = deque(maxlen=PREDICTION_BUFFER_SIZE)
    saving = False
    save_countdown = 0
    clip_frames = []  # 클립 프레임들을 메모리에 저장
    detected_action = None
    last_saved_action = None
    prev_prediction = None
    clip_predictions = []
    clip_probabilities = []  # 클립 기간 동안의 모든 예측 확률 저장
    pre_buffer_frames = []
    
    # 사람 수 추적을 위한 변수
    max_person_count = 0
    current_clip_max_persons = 0

    # 전등 끔 프레임 감지
    prev_brightness = None
    light_off_frame_count = 0
    light_off_min_frames = 5
    
    try:
        while True:
            current_prediction = None

            # UDP로 패킷 수신
            packet_info = receive_frame_udp_packetized(sock)
            if packet_info is None:
                continue
            
            frame_id = packet_info['frame_id']
            packet_idx = packet_info['packet_idx']
            num_packets = packet_info['num_packets']
            packet_data = packet_info['packet_data']
            
            # 프레임 버퍼에 패킷 추가
            if frame_id not in frame_buffers:
                frame_buffers[frame_id] = {'num_packets': num_packets, 'packets': {}, 'timestamp': packet_info['timestamp']}
            
            frame_buffers[frame_id]['packets'][packet_idx] = packet_data
            
            # 모든 패킷이 수신되었는지 확인
            if len(frame_buffers[frame_id]['packets']) == num_packets:
                original_timestamp = frame_buffers[frame_id]['timestamp']
                complete_frame_data = reassemble_frame(frame_id, frame_buffers[frame_id])
                
                if complete_frame_data:
                    # JPEG 데이터를 프레임으로 디코딩
                    frame = cv2.imdecode(np.frombuffer(complete_frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        del frame_buffers[frame_id]
                        continue
                    
                    # 버그 수정을 위해 probs를 기본값으로 초기화
                    probs = np.array([1.0, 0.0, 0.0, 0.0])

                    # 이상 감지 로직
                    joints, keypoints = extract_joints(frame, pose_model)
                    
                    # 현재 프레임의 사람 수 계산
                    person_count = count_valid_persons(keypoints)
                    
                    # 프레임에 사람 수 표시
                    cv2.putText(frame, f"Persons: {person_count}", 
                                (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    curr_brightness, light_off_status = detect_light_off(frame, prev_brightness)
                    prev_brightness = curr_brightness

                    # 연속 조건 적용
                    if "Light OFF" in light_off_status:
                        light_off_frame_count += 1
                    else:
                        light_off_frame_count = 0

                    # 5프레임 이상 연속 감지 시에만 진짜로 표시
                    if light_off_frame_count >= light_off_min_frames:
                        display_light_status = light_off_status
                        display_color = (0, 0, 255)
                    elif "Light OFF" in light_off_status:
                        # Light OFF가 감지되었지만 아직 5프레임 미만일 때
                        display_light_status = light_off_status
                        display_color = (0, 165, 255)  # 주황색 (경고)
                    else:
                        display_light_status = "Normal"
                        display_color = (0, 255, 0)

                    cv2.putText(frame, f"Lighting: {display_light_status}", 
                                (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                display_color, 2)
                    
                    # 밝기 값 디버깅용 표시 추가
                    cv2.putText(frame, f"Brightness: {curr_brightness:.1f}", 
                                (20, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)
                    
                    # Light OFF 카운터 표시
                    cv2.putText(frame, f"Light OFF Count: {light_off_frame_count}/{light_off_min_frames}", 
                                (20, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)
                    
                    # Light OFF 상태 디버깅용 표시 추가
                    cv2.putText(frame, f"Light Status: {light_off_status}", 
                                (20, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)
                    
                    # 클립 저장 중이면 최대 사람 수 업데이트
                    if saving and person_count > current_clip_max_persons:
                        current_clip_max_persons = person_count
                    
                    # 전체 최대 사람 수 업데이트
                    if person_count > max_person_count:
                        max_person_count = person_count
                        cv2.putText(frame, f"Max Persons: {max_person_count}", 
                                    (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # 사람 감지 및 예측 처리
                    has_person = person_count > 0
                    
                    if has_person:
                        joints_sequence.append(joints)
                        if len(joints_sequence) >= sequence_length:
                            input_tensor = torch.FloatTensor(list(joints_sequence)).unsqueeze(0).to(device)
                            with torch.no_grad():
                                logits = model(input_tensor)
                                probs = F.softmax(logits, dim=1).cpu().numpy()[0]
                            
                            # 신뢰도가 0.8 이상일 때만 해당 라벨로 예측, 그 이하는 Normal
                            max_prob = np.max(probs)
                            if max_prob >= CONFIDENCE_THRESHOLD:
                                current_prediction = np.argmax(probs)
                            else:
                                current_prediction = 0  # Normal로 분류
                            
                            frame = draw_predictions(frame, probs, current_prediction)
                            joints_sequence.popleft()
                        else:
                            remaining = sequence_length - len(joints_sequence)
                            cv2.putText(frame, f"Collecting data... ({remaining} frames left)", 
                                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    else:
                        # 사람이 감지되지 않았을 때 시퀀스 초기화
                        joints_sequence.clear()
                        prev_prediction = None  # 이전 예측 리셋
                        cv2.putText(frame, "No person detected", 
                                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    video_buffer.append(frame.copy())
                    
                    # 프레임을 미리 저장 (이상 행위 시작 전용)
                    pre_buffer_frames.append(frame.copy())
                    if len(pre_buffer_frames) > PRE_BUFFER_SIZE:
                        pre_buffer_frames.pop(0)  # 가장 오래된 프레임 제거
                    
                    # 예측 버퍼 처리
                    prev_prediction = process_prediction_buffer(pred_buffer, current_prediction, prev_prediction)
                    
                    # 키포인트 시각화 (비정상 행동 감지 시 빨간색)
                    if current_prediction is not None and current_prediction != 0:
                        frame = draw_keypoints_with_color(frame, keypoints, (0, 0, 255))
                    else:
                        frame = draw_keypoints(frame, keypoints)
                    
                    # 저장 시작 조건 확인
                    if should_start_saving(pred_buffer, saving, last_saved_action, light_off_frame_count, light_off_min_frames):
                        # 사람이 감지되지 않았으면 저장하지 않음
                        if person_count == 0:
                            continue
                            
                        saving = True
                        save_countdown = SAVE_COUNTDOWN
                        
                        # Light OFF 상태인지 확인
                        if light_off_frame_count >= light_off_min_frames:
                            detected_action = "light_off"
                            action_name = "Light_OFF"
                            last_saved_action = "light_off"
                            # Light OFF 알림
                            send_notification("Light_OFF", person_count, "1.00")
                        else:
                            # 기존 AI 예측 기반
                            detected_action = get_consecutive_abnormal_label(pred_buffer)
                            action_name = LABEL_NAMES[detected_action]
                            last_saved_action = detected_action
                            # 이상 행위 시스템 알림
                            # 현재 프레임의 확률을 클립 확률에 저장
                            if 'probs' in locals():
                                clip_probabilities.append(probs.copy())
                                # 해당 행위의 confidence 사용
                                current_confidence = probs[detected_action]
                                clip_confidences = [probs[detected_action] for probs in clip_probabilities]
                                max_confidence = np.max(clip_confidences)
                            else:
                                max_confidence = 1.0
                            confidence_str = f"{max_confidence:.2f}"
                            send_notification(action_name, person_count, confidence_str)
                        
                        dt_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                        
                        # 클립 프레임 버퍼 초기화
                        clip_frames = []
                        # clip_probabilities는 이미 현재 프레임의 확률이 저장되어 있으므로 초기화하지 않음
                        
                        # 새 클립 시작 시 사람 수 초기화
                        current_clip_max_persons = person_count
                        
                        print(f"Started recording clip: {action_name}")
                        # 이전 버퍼 프레임들 처리
                        for pre_frame in pre_buffer_frames:
                            clip_frames.append(pre_frame.copy())
                            current_clip_max_persons = max(current_clip_max_persons, count_valid_persons(extract_joints(pre_frame, pose_model)[1]))
                    
                    # 저장 중 처리
                    if saving:
                        add_recording_overlay(frame)
                        
                        # 프레임을 메모리에 저장
                        clip_frames.append(frame.copy())

                        if current_prediction is not None:
                            clip_predictions.append(current_prediction)
                            # 현재 프레임의 예측 확률 저장
                            if 'probs' in locals():
                                clip_probabilities.append(probs.copy())
                        save_countdown -= 1

                        if save_countdown == 0:
                            saving = False
                            
                            # Light OFF 상태였는지 확인
                            if detected_action == "light_off":
                                # Light OFF 클립 저장
                                confidence_str = "1.00"  # Light OFF는 100% 확신
                                send_clip_frames_to_central_server(clip_frames, "Light_OFF", current_clip_max_persons, dt_str, confidence_str)
                            else:
                                # 기존 AI 예측 기반 처리
                                abnormal_preds = [p for p in clip_predictions if p not in (0, None)]
                                if abnormal_preds:
                                    # detected_action 사용 (저장 시작 시 결정된 행위)
                                    action_name = LABEL_NAMES[detected_action]
                                    # 해당 행위의 최대 confidence 사용
                                    if clip_probabilities:
                                        clip_confidences = [probs[detected_action] for probs in clip_probabilities]
                                        max_confidence = np.max(clip_confidences)
                                    else:
                                        max_confidence = 1.0
                                    confidence_str = f"{max_confidence:.2f}"
                                    # 파일명에 confidence 포함
                                    send_clip_frames_to_central_server(clip_frames, action_name, current_clip_max_persons, dt_str, confidence_str)
                                else:
                                    print("Clip was mostly Normal, so it was not sent.")
                            
                            last_saved_action = None
                            clip_predictions = []
                            clip_probabilities = []  # 클립 확률 버퍼 초기화
                            current_clip_max_persons = 0  # 클립 저장 후 사람 수 초기화
                            clip_frames = []  # 클립 프레임 버퍼 초기화
                    
                    cv2.imshow('AI Server Feed', frame)
                    send_frame_udp_to_gui(frame)  # GUI로 UDP 전송
                
                # 완성된 프레임 버퍼 삭제
                del frame_buffers[frame_id]
            
            # 오래된 프레임 버퍼 정리
            current_frame_id = max(frame_buffers.keys()) if frame_buffers else 0
            old_frames = [fid for fid in frame_buffers.keys() if fid < current_frame_id - 10]
            for old_frame in old_frames:
                del frame_buffers[old_frame]
            
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
        sock.close()
        if tcp_sock: # 프로그램 종료 시 소켓 닫기
            tcp_sock.close()
        if gui_udp_sock:  # GUI UDP 소켓 닫기
            gui_udp_sock.close()
        cv2.destroyAllWindows()
        print("UDP connection closed")

def send_clip_frames_to_central_server(clip_frames, action_name, person_count, timestamp_str, confidence_str):
    """프레임들을 비디오로 인코딩하여 Central 서버로 전송 (confidence 포함)"""
    global tcp_sock, frame_counter
    if not ensure_tcp_connection():
        print("[AI 서버] Central 서버 연결 실패 - 클립 전송 불가")
        return

    try:
        if not clip_frames:
            print("[AI 서버] 클립 프레임이 없음")
            return
            
        # 프레임들을 비디오로 인코딩
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_filename = f"temp_clip_{frame_counter}.mp4"
        
        # 첫 번째 프레임의 크기로 비디오 라이터 생성
        height, width = clip_frames[0].shape[:2]
        out = cv2.VideoWriter(temp_filename, cv2.VideoWriter.fourcc(*'mp4v'), 5, (width, height))
        if not out.isOpened():
            print("[AI 서버] 비디오 라이터 생성 실패")
            return
            
        # 프레임들을 비디오에 추가
        for frame in clip_frames:
            out.write(frame)
        out.release()
        
        # 인코딩된 비디오 파일 읽기
        with open(temp_filename, 'rb') as f:
            clip_data = f.read()
        
        # 임시 파일 삭제
        os.remove(temp_filename)
        
        # 클립 메타데이터 생성 (행위, 사람 수, 타임스탬프)
        metadata = {
            'action_name': action_name,
            'person_count': person_count,
            'timestamp': timestamp_str,
            'frame_count': len(clip_frames),
            'confidence': confidence_str
        }
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_size = len(metadata_json)
        
        # 클립 데이터를 패킷으로 전송 (메타데이터 + 비디오 데이터)
        timestamp = time.time()
        frame_id = frame_counter % 0xFFFFFFFF
        packet_idx = 0
        num_packets = 1
        data_size = metadata_size + len(clip_data)
        
        # 헤더: [timestamp, frame_id, packet_idx, num_packets, data_size, metadata_size]
        header = struct.pack('!dIIIII', timestamp, frame_id, packet_idx, num_packets, data_size, metadata_size)
        packet = header + metadata_json + clip_data
        
        tcp_sock.sendall(packet)
        # 파일명에 confidence 포함해서 로그 출력
        print(f"[AI 서버] Central 서버로 클립 전송: {action_name}_p{person_count}_{confidence_str}_{timestamp_str}, 크기: {data_size} bytes")
        frame_counter += 1
    except Exception as e:
        print(f"[AI 서버] 클립 전송 오류: {e}")
        if tcp_sock:
            tcp_sock.close()
        tcp_sock = None

if __name__ == "__main__":
    # 프로젝트 루트를 기준으로 모델 파일의 절대 경로 생성
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # TorchScript 최적화된 모델 사용
    model_path = os.path.join(project_root, "saved_models/스트그쓰느스트1_torchscript.pt")
    
    # UDP 설정 - cctv_udp_client.py와 호환
    udp_ip = "0.0.0.0"  # 모든 인터페이스에서 수신
    udp_port = 5005     # cctv_udp_client.py와 동일한 포트
    realtime_anomaly_detection(model_path=model_path, udp_ip=udp_ip, udp_port=udp_port) 