import cv2
import os
import glob
from tqdm import tqdm

video_files = glob.glob('/home/ckim/Desktop/*/*.mp4')
output_dir = 'extracted_frames'
os.makedirs(output_dir, exist_ok=True)

for video_path in tqdm(video_files, desc='영상별 프레임 추출'):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
cap = cv2.VideoCapture(video_path)
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
        save_path = f"{output_dir}/{video_name}_{frame_count:04d}.jpg"
        cv2.imwrite(save_path, frame)
    frame_count += 1
cap.release()
    print(f"{video_name}: {frame_count}개 프레임 저장 완료")

