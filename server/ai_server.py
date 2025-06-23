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

def draw_keypoints(frame, keypoints):
    """프레임에 관절점 시각화"""
    if keypoints is not None:
        for kp in keypoints[:17]:
            if len(kp) >= 3 and kp[2] > 0.1: # confidence > 0.1
                x, y = int(kp[0]), int(kp[1])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
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

def receive_frame_udp_single_packet(sock):
    """단일 패킷 방식으로 UDP 프레임 수신 (1920x1080 지원)"""
    try:
        data, addr = sock.recvfrom(150000)  # 120KB + 여유분
        
        if len(data) < 16:
            return None
        
        # 패킷 헤더 파싱: [frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
        header = data[:16]
        frame_id, packet_idx, num_packets, data_size = struct.unpack('!IIII', header)
        
        # 단일 패킷 검증
        if num_packets != 1 or packet_idx != 0:
            print(f"잘못된 패킷 형식: frame_id={frame_id}, packet_idx={packet_idx}, num_packets={num_packets}")
            return None
        
        # 데이터 크기 검증
        if data_size > len(data) - 16:
            print(f"패킷 데이터 크기 불일치: 예상 {data_size}, 실제 {len(data) - 16}")
            return None
            
        packet_data = data[16:16+data_size]
        
        return {
            'frame_id': frame_id,
            'frame_data': packet_data,
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
    
    joints_sequence = deque(maxlen=sequence_length)
    print("Starting real-time anomaly detection from UDP stream at 5fps...")
    print("Press 'q' to quit, 'r' to reset sequence")
    fps = 5
    frame_interval = 1.0 / fps
    last_frame_time = time.time()
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
    
    try:
        while True:
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                continue
            last_frame_time = current_time

            current_prediction = None

            # UDP로 패킷 수신
            packet_info = receive_frame_udp_single_packet(sock)
            if packet_info is None:
                print("No packet received from UDP stream")
                continue
            
            frame_id = packet_info['frame_id']
            frame_data = packet_info['frame_data']
            
            # 단일 패킷이므로 바로 프레임 디코딩
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if frame is None:
                print(f"프레임 {frame_id} 디코딩 실패.")
                continue
            
            # 이상 감지 로직
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
                    
                    # 신뢰도가 0.8 이상일 때만 해당 라벨로 예측, 그 이하는 Normal
                    max_prob = np.max(probs)
                    if max_prob >= 0.8:
                        current_prediction = np.argmax(probs)
                    else:
                        current_prediction = 0  # Normal로 분류
                    
                    frame = draw_predictions(frame, probs, current_prediction, None)
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
                fourcc = cv2.VideoWriter.fourcc(*'mp4v')
                height, width = frame.shape[:2]
                out = cv2.VideoWriter(filename, fourcc, 5, (width, height))
                
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
                        new_filename = f"{action_name}_{dt_str}.mp4"
                        if filename and os.path.exists(filename):
                            os.rename(filename, new_filename)
                            print(f"Clip saved: {new_filename}")
                    else:
                        if filename and os.path.exists(filename):
                            os.remove(filename)
                            print("Clip was mostly Normal, so it was deleted.")
                        
                    last_saved_action = None
                    clip_predictions = []
                send_frame_tcp(frame)
            
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