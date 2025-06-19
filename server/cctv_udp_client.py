# cctv_udp_client.py
import cv2
import socket
import time
import struct
import numpy as np

UDP_IP = "192.168.0.21" # 채연 pc
# UDP_IP = "192.168.0.15" # 원호 pc 
UDP_PORT = 5005
MAX_PACKET_SIZE = 60000  # UDP 패킷 크기 제한

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

# record.py와 동일한 카메라 설정
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG 포맷 강제
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"프레임 크기: {width}x{height}")

# record.py와 동일한 FPS 설정
fps = 5
frame_interval = 1.0 / fps
last_frame_time = time.time()
frame_id = 0

def send_frame_in_packets(frame_data, frame_id):
    """프레임을 여러 패킷으로 분할하여 전송"""
    total_size = len(frame_data)
    num_packets = (total_size + MAX_PACKET_SIZE - 1) // MAX_PACKET_SIZE
    
    for packet_idx in range(num_packets):
        start_idx = packet_idx * MAX_PACKET_SIZE
        end_idx = min(start_idx + MAX_PACKET_SIZE, total_size)
        packet_data = frame_data[start_idx:end_idx]
        
        # 패킷 헤더: [frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
        header = struct.pack('!IIII', frame_id, packet_idx, num_packets, len(packet_data))
        packet = header + packet_data
        
        sock.sendto(packet, (UDP_IP, UDP_PORT))
        print(f"[CCTV] 프레임 {frame_id}, 패킷 {packet_idx+1}/{num_packets}, 크기: {len(packet_data)} bytes")

def recv_full(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_ai(ai_conn, gui_conn):
    print("[Central] AI 서버 핸들러 시작")
    while True:
        # 1. 프레임 길이(4바이트) 먼저 받기
        length_bytes = recv_full(ai_conn, 4)
        if not length_bytes:
            print("[Central] AI 서버 연결 종료")
            break
        frame_len = struct.unpack('!I', length_bytes)[0]

        # 2. 프레임 데이터 받기
        frame_bytes = recv_full(ai_conn, frame_len)
        if not frame_bytes:
            print("[Central] 프레임 데이터 수신 실패")
            break

        print(f"[Central] AI서버에서 수신: {frame_len} bytes")

        # 프레임 디코딩 테스트
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            print("[Central] 프레임 디코딩 실패")
            continue

        # GUI로도 같은 방식으로 전송
        gui_conn.sendall(struct.pack('!I', frame_len) + frame_bytes)
        print(f"[Central] GUI로 전송: {frame_len} bytes")

while True:
    current_time = time.time()
    if current_time - last_frame_time >= frame_interval:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break
        
        # 프레임을 JPEG로 인코딩 (원본 해상도 유지)
        result, imgencode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        data = imgencode.tobytes()
        
        # 프레임을 여러 패킷으로 분할하여 전송
        send_frame_in_packets(data, frame_id)
        frame_id += 1
        last_frame_time = current_time

cap.release()
sock.close()