#!/usr/bin/env python3
import tensorflow as tf
from deepface import DeepFace
import cv2
import numpy as np
import time
import os

print("=== GPU 설정 ===")
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"GPU 발견: {len(gpus)}개")
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
        print(f"GPU 메모리 growth 설정: {gpu}")
else:
    print("GPU 없음")

print("\n=== 환경변수 설정 ===")
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
print("TF_FORCE_GPU_ALLOW_GROWTH=true 설정")

print("\n=== DeepFace 테스트 ===")
# 테스트 이미지 경로
test_frames = [
    "/home/ckim/extracted_frames/Abandon_001.jpg",
    "/home/ckim/extracted_frames/Abandon_002.jpg", 
    "/home/ckim/extracted_frames/Abandon_003.jpg"
]

# 실제 존재하는 프레임 찾기
existing_frames = []
for frame_path in test_frames:
    if os.path.exists(frame_path):
        existing_frames.append(frame_path)

if not existing_frames:
    print("테스트할 프레임 파일이 없습니다.")
    # 임시 테스트 이미지 생성
    test_img = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
    cv2.imwrite("/tmp/test_img.jpg", test_img)
    existing_frames = ["/tmp/test_img.jpg"]

print(f"테스트할 이미지: {len(existing_frames)}개")

for i, img_path in enumerate(existing_frames[:3]):  # 최대 3개만 테스트
    print(f"\n--- 이미지 {i+1}: {os.path.basename(img_path)} ---")
    
    start_time = time.time()
    try:
        img = cv2.imread(img_path)
        if img is None:
            print("이미지 로드 실패")
            continue
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        print("DeepFace 분석 시작...")
        result = DeepFace.analyze(
            img_rgb, 
            detector_backend='retinaface',
            enforce_detection=False
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ 처리 완료! 소요시간: {processing_time:.2f}초")
        
        # 결과 정보
        if isinstance(result, list):
            result = result[0]
        
        if 'region' in result:
            region = result['region']
            print(f"얼굴 위치: x={region['x']}, y={region['y']}, w={region['w']}, h={region['h']}")
        
    except Exception as e:
        print(f"❌ 에러: {e}")

print("\n=== 완료 ===")
print("이제 nvidia-smi로 GPU 사용량을 확인해보세요!") 