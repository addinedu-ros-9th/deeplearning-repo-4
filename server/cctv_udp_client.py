# cctv_udp_client.py
import cv2
import socket

UDP_IP = "192.168.0.21"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # 프레임을 JPEG로 인코딩
    frame = cv2.resize(frame, (320, 240)) 
    result, imgencode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    data = imgencode.tobytes()
    # UDP 패킷 크기 제한 확인
    if len(data) > 65000:
        print("프레임이 너무 큽니다. 크기를 줄이세요.")
        continue
    print(f"[CCTV] 전송 프레임 크기: {len(data)} bytes")
    sock.sendto(data, (UDP_IP, UDP_PORT))
cap.release()
sock.close()