import cv2
import time
import os

# 폴더 및 파일명 매핑
LABELS = {
    '0': ('Broken', 'broken'),
    '1': ('Theft', 'theft'),
    '2': ('Abandon', 'abandon'),
    '3': ('Normal', 'normal'),
}
BASE_PATH = '/home/koo4802/Desktop/'

print("녹화할 클래스를 선택하세요:")
print("0: Broken, 1: Theft, 2: Abandon, 3: Normal")
selected = None
while selected not in LABELS:
    selected = input("클래스 번호 입력: ")
    if selected not in LABELS:
        print("잘못된 입력입니다. 다시 입력하세요.")

folder, prefix = LABELS[selected]
save_dir = os.path.join(BASE_PATH, folder)
os.makedirs(save_dir, exist_ok=True)
# 폴더 내 파일 개수 파악
existing = [f for f in os.listdir(save_dir) if f.startswith(prefix) and f.endswith('.mp4')]
next_idx = 1
if existing:
    nums = [int(f[len(prefix):-4]) for f in existing if f[len(prefix):-4].isdigit()]
    if nums:
        next_idx = max(nums) + 1
filename = f"{prefix}{next_idx}.mp4"
filepath = os.path.join(save_dir, filename)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG 포맷 강제
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"프레임 크기: {width}x{height}")

fps = 5
frame_interval = 1.0 / fps

print(f"녹화 시작: {filepath} (q를 누르면 종료)")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
last_frame_time = time.time()

while True:
    current_time = time.time()
    if current_time - last_frame_time >= frame_interval:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break
        out.write(frame)
        cv2.imshow('Webcam', frame)
        last_frame_time = current_time
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()
cap.release()
cv2.destroyAllWindows()
print(f"녹화가 완료되었습니다: {filepath}")
