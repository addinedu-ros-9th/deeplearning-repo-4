# ai_server.py
import socket
import threading
import cv2
import numpy as np
import time

# UDP 수신
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

# TCP 송신
CENTRAL_IP = "192.168.0.15"
CENTRAL_PORT = 6006
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))

# FPS 제어를 위한 설정
fps = 5
frame_interval = 1.0 / fps
last_frame_time = time.time()

print(f"[AI서버] 1920x1080 해상도, {fps}fps로 수신 대기 중...")

while True:
    data, addr = udp_sock.recvfrom(65536)
    current_time = time.time()
    
    # FPS 제어: 지정된 간격으로만 프레임 처리
    if current_time - last_frame_time >= frame_interval:
        print(f"[AI서버] UDP로 수신: {len(data)} bytes from {addr}")
        tcp_sock.sendall(data)
        print(f"[AI서버] TCP로 전송: {len(data)} bytes")
        
        if not data:
            break
            
        # JPEG 바이너리를 numpy array로 변환 후 디코딩
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is not None:
            # 1920x1080 해상도에 맞는 윈도우 크기로 조정
            cv2.namedWindow("Received Frame", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Received Frame", 1280, 720)  # 화면에 맞게 크기 조정
            cv2.imshow("Received Frame", frame)
            last_frame_time = current_time
    
    if cv2.waitKey(1) == 27:
        break

tcp_sock.close()
cv2.destroyAllWindows()