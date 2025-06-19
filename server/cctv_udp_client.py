# cctv_udp_client.py
import cv2
import socket
import time

UDP_IP = "192.168.0.21"
UDP_PORT = 5005

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
        
        # UDP 패킷 크기 제한 확인
        if len(data) > 65000:
            print("프레임이 너무 큽니다. JPEG 품질을 낮추세요.")
            continue
            
        print(f"[CCTV] 전송 프레임 크기: {len(data)} bytes")
        sock.sendto(data, (UDP_IP, UDP_PORT))
        last_frame_time = current_time

cap.release()
sock.close()