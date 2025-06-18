# ai_server.py
import socket
import threading
import cv2
import numpy as np

# UDP 수신
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

# TCP 송신
CENTRAL_IP = "192.168.0.21"
CENTRAL_PORT = 6006
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))

while True:
    data, addr = udp_sock.recvfrom(65536)
    print(f"[AI서버] UDP로 수신: {len(data)} bytes from {addr}")
    tcp_sock.sendall(data)
    print(f"[AI서버] TCP로 전송: {len(data)} bytes")
    if not data:
        break
    # JPEG 바이너리를 numpy array로 변환 후 디코딩
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is not None:
        cv2.imshow("Received Frame", frame)
    if cv2.waitKey(1) == 27:
        break
tcp_sock.close()
cv2.destroyAllWindows()