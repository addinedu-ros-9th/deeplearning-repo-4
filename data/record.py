import cv2
import time

# 기본 카메라 접근 방식 사용
cap = cv2.VideoCapture(3)  # video3에 해당하는 인덱스

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# 프레임 크기 확인
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"프레임 크기: {width}x{height}")

# MP4 인코더 설정 (H.264 코덱 사용)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 5.0, (width, height))

# FPS 설정 (5 FPS)
fps = 5
frame_interval = 1.0 / fps
last_frame_time = time.time()

print("녹화를 시작합니다. 'q'를 누르면 종료됩니다.")

while True:
    # 현재 시간
    current_time = time.time()
    
    # 프레임 간격 확인
    if current_time - last_frame_time >= frame_interval:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break
            
        # 프레임 저장
        out.write(frame)
            
        # 프레임 표시
        cv2.imshow('Webcam', frame)
        last_frame_time = current_time
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()
print("녹화가 완료되었습니다. output.mp4 파일을 확인하세요.")
