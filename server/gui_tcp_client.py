# gui_client.py
import socket
import pickle
import cv2
import numpy as np

# CENTRAL_IP = "192.168.0.15"
CENTRAL_IP = "192.168.0.21"
CENTRAL_PORT = 7007

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((CENTRAL_IP, CENTRAL_PORT))

while True:
    data = sock.recv(65536)
    if not data:
        break
    print(f"[GUI] Central 서버에서 수신: {len(data)} bytes")
    # JPEG 바이너리를 numpy array로 변환 후 디코딩
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is not None:
        cv2.imshow("Received Frame", frame)
    if cv2.waitKey(1) == 27:
        break
sock.close()
cv2.destroyAllWindows()