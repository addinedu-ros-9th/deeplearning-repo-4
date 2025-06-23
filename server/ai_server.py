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

from config import RECIEVER_IP, RECIEVER_PORT, CENTRAL_IP, CENTRAL_PORT

# ai_server.py가 있는 디렉토리의 부모 디렉토리를 경로에 추가
# 이렇게 하면 deeplearning-repo-4 폴더를 기준으로 anomaly_detection 모듈을 찾을 수 있음
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from anomaly_detection import AnomalyDetector


# --- 모델 및 디바이스 설정 ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tcp_sock = None # TCP 소켓을 전역 변수로 관리

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
    """처리된 프레임을 중앙 서버로 전송 (연결 확인 기능 포함)"""
    global tcp_sock
    if not ensure_tcp_connection():
        time.sleep(1) # 연결 실패 시 잠시 대기
        return

    try:
        # 프레임을 JPEG로 인코딩
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if result:
            data = encoded_frame.tobytes()
            # 데이터 길이를 먼저 보내고 그 다음 실제 데이터를 전송
            if tcp_sock:
                tcp_sock.sendall(struct.pack('!I', len(data)) + data)
        else:
            print("[AI 서버] 프레임 인코딩 실패")
    except socket.error as e:
        print(f"[AI 서버] TCP 전송 오류: {e}")
        if tcp_sock:
            tcp_sock.close()
        tcp_sock = None

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
            keypoints = results.keypoints.data.cpu().numpy()  # [num_people, 17, 3] 형태
            
            # 디버깅: 키포인트 형태 출력
            if len(keypoints) > 0:
                print(f"키포인트 배열 형태: {keypoints.shape}")
                print(f"첫 번째 사람의 첫 번째 키포인트: {keypoints[0][0]}")
            
            joints = np.zeros(17 * 4)
            for i, kp in enumerate(keypoints[0][:17]):  # 첫 번째 사람의 관절점만 사용
                if i < 17:
                    joints[i*4:(i+1)*4] = [kp[0]/256, kp[1]/256, 0.0, kp[2]]
            return joints, keypoints
        else:
            return np.zeros(17 * 4), None
    except Exception as e:
        print(f"Error processing frame: {e}")
        return np.zeros(17 * 4), None

def draw_predictions(frame, probs, current_prediction, fps=None, delay=None):
    """프레임에 예측 결과를 왼쪽 위에 표시"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 220), (0, 0, 0), -1)
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
    
    if delay:
        cv2.putText(frame, delay, (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

    return frame

def draw_keypoints(frame, keypoints):
    """프레임에 관절점 시각화 및 선으로 연결"""
    if keypoints is None or len(keypoints) == 0:
        return frame
        
    # 디버깅: 키포인트 정보 출력
    print(f"draw_keypoints 함수 - keypoints 배열 형태: {keypoints.shape}")
    
    # 관절점 연결 (COCO 포맷 기준)
    limb_connections = [
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
    
    # 각 사람별로 처리
    for person_idx in range(len(keypoints)):
        person_kps = keypoints[person_idx]
        
        # 디버깅: 이 사람의 키포인트 정보 출력
        valid_keypoints_count = sum(1 for kp in person_kps if float(kp[2]) > 0.1)
        print(f"사람 {person_idx} - 유효한 키포인트 수: {valid_keypoints_count}")
        if valid_keypoints_count > 0:
            print(f"첫 번째 유효한 키포인트 위치: {next((kp[:2] for kp in person_kps if float(kp[2]) > 0.1), None)}")
        
        # 관절점 그리기
        for kp_idx in range(len(person_kps)):
            if kp_idx < 17:  # 17개 키포인트만 처리
                kp = person_kps[kp_idx]
                conf = float(kp[2])  # 신뢰도를 float로 변환
                if conf > 0.1:  # confidence > 0.1
                    x, y = int(kp[0]), int(kp[1])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                    # 키포인트 번호 표시
                    cv2.putText(frame, f"{kp_idx}", (x+5, y-5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # 관절점 연결선 그리기 - 신뢰도 기준 상향 조정
        for connection in limb_connections:
            idx1, idx2 = connection
            if (idx1 < len(person_kps) and idx2 < len(person_kps)):
                conf1 = float(person_kps[idx1][2])
                conf2 = float(person_kps[idx2][2])
                # 신뢰도 기준을 0.2로 상향 조정
                if conf1 > 0.2 and conf2 > 0.2:
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
                if conf > 0.2:  # 신뢰도 기준 상향
                    x, y = int(person_kps[kp_idx][0]), int(person_kps[kp_idx][1])
                    # 0,0 근처 좌표 제외
                    if x > 10 and y > 10:
                        valid_points.append((x, y))
        
        if len(valid_points) >= 5:  # 최소 5개 이상의 유효한 점이 있을 때만 바운딩 박스 그리기
            x_coords = [p[0] for p in valid_points]
            y_coords = [p[1] for p in valid_points]
            
            # 전체 사람 바운딩 박스
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # 패딩 추가 (10%)
            width = x_max - x_min
            height = y_max - y_min
            x_min = max(0, x_min - int(width * 0.1))
            y_min = max(0, y_min - int(height * 0.1))
            x_max = min(frame.shape[1], x_max + int(width * 0.1))
            y_max = min(frame.shape[0], y_max + int(height * 0.1))
            
            # 사람 전체 바운딩 박스 그리기 (파란색)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
            
            # 얼굴 바운딩 박스 그리기 (빨간색)
            face_keypoints = []
            for idx in [0, 1, 2, 3, 4]:  # 얼굴 관련 키포인트 (코, 눈, 귀)
                if idx < len(person_kps):
                    conf = float(person_kps[idx][2])
                    if conf > 0.2:  # 신뢰도 기준 상향
                        x, y = int(person_kps[idx][0]), int(person_kps[idx][1])
                        # 0,0 근처 좌표 제외
                        if x > 10 and y > 10:
                            face_keypoints.append((x, y))
            
            if len(face_keypoints) >= 2:  # 최소 2개 이상의 얼굴 키포인트가 있을 때만
                face_x_coords = [p[0] for p in face_keypoints]
                face_y_coords = [p[1] for p in face_keypoints]
                
                face_x_min, face_x_max = min(face_x_coords), max(face_x_coords)
                face_y_min, face_y_max = min(face_y_coords), max(face_y_coords)
                
                # 얼굴 패딩 추가 (20%)
                face_width = face_x_max - face_x_min
                face_height = face_y_max - face_y_min
                face_x_min = max(0, face_x_min - int(face_width * 0.2))
                face_y_min = max(0, face_y_min - int(face_height * 0.2))
                face_x_max = min(frame.shape[1], face_x_max + int(face_width * 0.2))
                face_y_max = min(frame.shape[0], face_y_max + int(face_height * 0.2))
                
                # 얼굴 바운딩 박스 그리기 (빨간색)
                cv2.rectangle(frame, (face_x_min, face_y_min), (face_x_max, face_y_max), (0, 0, 255), 2)
    
    return frame

def setup_udp_socket(udp_ip, udp_port):
    """UDP 소켓을 설정하고 지정된 IP와 포트에 바인딩합니다."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    sock.settimeout(2.0)  # 수신 대기 시간 초과를 2초로 설정
    print(f"UDP 서버가 {udp_ip}:{udp_port}에서 수신 대기 중입니다.")
    return sock


# --- 네트워크 설정 ---
# 이 부분의 기존 TCP 연결 로직은 ensure_tcp_connection 함수로 대체되었으므로 제거합니다.
# tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# while True: ...

# 프레임 재조립을 위한 버퍼
frame_buffers = {}  # {frame_id: {packet_idx: data, ...}}

print(f"[AI서버] CCTV 클라이언트로부터 UDP 수신 대기 중... (Port: {RECIEVER_PORT})")

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

def realtime_anomaly_detection(model_path,  # model_path를 필수로 받도록 변경
                              pose_model_path='yolov8n-pose.pt',
                              sequence_length=15,
                              udp_ip="0.0.0.0",
                              udp_port=5005):
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
    
    video_buffer = deque(maxlen=45)  # 9초 전까지의 프레임 저장 (5fps * 9초)
    pred_buffer = deque(maxlen=7)
    saving = False
    save_countdown = 0
    out = None
    filename = None
    detected_action = None
    last_saved_action = None
    prev_prediction = None
    clip_predictions = []
    pre_buffer_frames = []  # 이상 행위 시작 전 프레임들을 저장
    pre_buffer_size = 15  # 3초 전까지 저장 (5fps * 3초)
    
    # 사람 수 추적을 위한 변수
    max_person_count = 0
    current_clip_max_persons = 0
    
    try:
        while True:
            current_prediction = None

            # UDP로 패킷 수신
            packet_info = receive_frame_udp_packetized(sock)
            if packet_info is None:
                print("No packet received from UDP stream")
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
                        print(f"프레임 {frame_id} 디코딩 실패.")
                        del frame_buffers[frame_id]
                        continue
                    
                    # 딜레이 계산 및 표시
                    delay = time.time() - original_timestamp
                    delay_text = f"Delay: {delay*1000:.2f} ms"
                    
                    # 버그 수정을 위해 probs를 기본값으로 초기화
                    probs = np.array([1.0, 0.0, 0.0, 0.0])

                    # 이상 감지 로직
                    joints, keypoints = extract_joints(frame, pose_model)
                    
                    # 현재 프레임의 사람 수 계산
                    person_count = 0
                    has_person = False
                    
                    # YOLOv8 pose 모델 결과에서 사람 수 추출
                    if hasattr(pose_model, 'results') and pose_model.results:
                        try:
                            # 최신 결과에서 사람 수 가져오기
                            results = pose_model.results[-1]
                            if results and hasattr(results, 'keypoints') and results.keypoints is not None:
                                person_count = len(results.keypoints)
                        except (IndexError, AttributeError) as e:
                            print(f"사람 수 계산 중 오류: {e}")
                    
                    # 프레임에 사람 수 표시
                    cv2.putText(frame, f"Persons: {person_count}", 
                                (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # 클립 저장 중이면 최대 사람 수 업데이트
                    if saving and person_count > current_clip_max_persons:
                        current_clip_max_persons = person_count
                    
                    # 전체 최대 사람 수 업데이트
                    if person_count > max_person_count:
                        max_person_count = person_count
                        cv2.putText(frame, f"Max Persons: {max_person_count}", 
                                    (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    has_person = False
                    if keypoints is not None:
                        # 첫 번째 사람의 키포인트만 처리 (LSTM 모델에 사용)
                        if len(keypoints) > 0:
                            person_keypoints = keypoints[0]
                            for kp_idx in range(len(person_keypoints)):
                                if kp_idx < 17:  # 17개 키포인트만 처리
                                    kp = person_keypoints[kp_idx]
                                    conf_value = float(kp[2])  # 신뢰도를 float로 변환
                                    if conf_value > 0.1:  # confidence > 0.1
                                        has_person = True
                                        x, y = int(kp[0]), int(kp[1])
                                        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                    
                    if has_person:
                        joints_sequence.append(joints)
                        if len(joints_sequence) >= sequence_length:
                            input_tensor = torch.FloatTensor(list(joints_sequence)).unsqueeze(0).to(device)
                            with torch.no_grad():
                                logits = model(input_tensor)
                                probs = F.softmax(logits[:, -1, :], dim=-1).cpu().numpy()[0]
                            
                            # 신뢰도가 0.8 이상일 때만 해당 라벨로 예측, 그 이하는 Normal
                            max_prob = np.max(probs)
                            if max_prob >= 0.8:
                                current_prediction = np.argmax(probs)
                            else:
                                current_prediction = 0  # Normal로 분류
                            
                            frame = draw_predictions(frame, probs, current_prediction, None, delay_text)
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
                    if len(pre_buffer_frames) > pre_buffer_size:
                        pre_buffer_frames.pop(0)  # 가장 오래된 프레임 제거
                    
                    if current_prediction is not None:
                        if prev_prediction is not None and current_prediction != prev_prediction:
                            pred_buffer.clear()
                        pred_buffer.append(current_prediction)
                        prev_prediction = current_prediction
                        frame = draw_predictions(frame, probs, current_prediction, None, delay_text)
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
                        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
                        height, width = frame.shape[:2]
                        out = cv2.VideoWriter(filename, fourcc, 5, (width, height))
                        
                        # 새 클립 시작 시 사람 수 초기화
                        current_clip_max_persons = person_count
                        
                        if out.isOpened():
                            print(f"Started saving clip: {filename}")
                            for pre_frame in pre_buffer_frames:
                                out.write(pre_frame)
                        else:
                            print(f"Failed to open video writer for {filename}")
                            saving = False
                    
                    if saving:
                        if out and out.isOpened():
                            out.write(frame)

                        if current_prediction is not None:
                            clip_predictions.append(current_prediction)
                        save_countdown -= 1

                        if save_countdown == 0:
                            if out and out.isOpened():
                                out.release()
                            saving = False
                            
                            abnormal_preds = [p for p in clip_predictions if p not in (0, None)]
                            if abnormal_preds:
                                major_action = Counter(abnormal_preds).most_common(1)[0][0]
                                action_name = ["Normal", "Theft", "Abandon", "Broken"][major_action]
                                # 파일명에 최대 사람 수 추가
                                new_filename = f"{action_name}_p{current_clip_max_persons}_{dt_str}.mp4"
                                if filename and os.path.exists(filename):
                                    os.rename(filename, new_filename)
                                    print(f"Clip saved: {new_filename} (Max persons: {current_clip_max_persons})")
                            else:
                                if filename and os.path.exists(filename):
                                    os.remove(filename)
                                    print("Clip was mostly Normal, so it was deleted.")
                            
                            last_saved_action = None
                            clip_predictions = []
                            current_clip_max_persons = 0  # 클립 저장 후 사람 수 초기화
                    
                    frame = draw_keypoints(frame, keypoints)
                    cv2.imshow('AI Server Feed', frame)
                    # send_frame_tcp(frame)
                
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
        cv2.destroyAllWindows()
        if out is not None and saving:
            out.release()
        print("UDP connection closed")

if __name__ == "__main__":
    # 프로젝트 루트를 기준으로 모델 파일의 절대 경로 생성
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(project_root, "saved_models/노말변경3개.pth")
    
    # UDP 설정 - cctv_udp_client.py와 호환
    udp_ip = "0.0.0.0"  # 모든 인터페이스에서 수신
    udp_port = 5005     # cctv_udp_client.py와 동일한 포트
    realtime_anomaly_detection(model_path=model_path, udp_ip=udp_ip, udp_port=udp_port) 