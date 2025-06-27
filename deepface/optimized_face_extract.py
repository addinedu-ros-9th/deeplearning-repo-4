#!/usr/bin/env python3
import os
import cv2
import numpy as np
from tqdm import tqdm
import glob
import tensorflow as tf
from deepface import DeepFace
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# GPU 설정
print("=== GPU 최적화 설정 ===")
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"GPU 설정 완료: {len(gpus)}개")

# 환경변수 설정
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

def process_single_frame(img_path, output_dir):
    """단일 프레임 처리"""
    try:
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        
        # 이미 처리된 파일은 스킵
        if os.path.exists(output_path):
            return f"[스킵] {filename}"
        
        img = cv2.imread(img_path)
        if img is None:
            return f"[실패] {filename}: 로드 실패"

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # opencv detector 사용 (더 빠름)
        result = DeepFace.analyze(
            img_rgb, 
            detector_backend='opencv',  # retinaface보다 빠름
            enforce_detection=False,
            actions=['emotion']  # 최소한의 분석만
        )

        result = result[0] if isinstance(result, list) else result
        region = result['region']
        x, y, w, h = region['x'], region['y'], region['w'], region['h']

        # 유효성 필터링
        img_h, img_w = img.shape[:2]
        face_area = w * h
        img_area = img_w * img_h

        if face_area < 50*50 or face_area > 0.8 * img_area:
            return f"[스킵] {filename}: 얼굴 크기 비정상"

        # 얼굴 크롭 및 저장
        x, y, w, h = max(0, x), max(0, y), min(w, img_w-x), min(h, img_h-y)
        face_crop = img[y:y+h, x:x+w]
        
        if face_crop.size > 0:
            cv2.imwrite(output_path, face_crop)
            return f"[성공] {filename}"
        else:
            return f"[실패] {filename}: 빈 얼굴"
            
    except Exception as e:
        return f"[에러] {filename}: {str(e)}"

def process_batch(frame_batch, output_dir, batch_id):
    """배치 처리"""
    results = []
    for img_path in frame_batch:
        result = process_single_frame(img_path, output_dir)
        results.append(result)
    return results

def main():
    # 경로 설정
    extracted_frames_dir = "/home/ckim/extracted_frames"
    output_dir = "/home/ckim/best_faces"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 프레임 파일 목록
    frame_files = glob.glob(os.path.join(extracted_frames_dir, "*.jpg"))
    total_files = len(frame_files)
    
    print(f"총 {total_files:,}개 프레임 발견")
    
    if total_files == 0:
        print("처리할 파일이 없습니다.")
        return
    
    # 성능 측정
    start_time = time.time()
    
    # 방법 1: 배치 처리 (권장)
    batch_size = 100  # 배치 크기
    batches = [frame_files[i:i+batch_size] for i in range(0, len(frame_files), batch_size)]
    
    print(f"배치 크기: {batch_size}, 총 배치 수: {len(batches)}")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    # 진행률 표시
    with tqdm(total=total_files, desc="얼굴 추출 중") as pbar:
        for i, batch in enumerate(batches):
            batch_results = process_batch(batch, output_dir, i)
            
            for result in batch_results:
                if "[성공]" in result:
                    success_count += 1
                elif "[스킵]" in result:
                    skip_count += 1
                else:
                    error_count += 1
                
                pbar.update(1)
                
                # 주기적으로 상태 출력
                if pbar.n % 1000 == 0:
                    elapsed = time.time() - start_time
                    speed = pbar.n / elapsed
                    remaining = (total_files - pbar.n) / speed if speed > 0 else 0
                    print(f"\n진행률: {pbar.n}/{total_files} ({pbar.n/total_files*100:.1f}%)")
                    print(f"속도: {speed:.1f} files/sec, 남은 시간: {remaining/60:.1f}분")
                    print(f"성공: {success_count}, 스킵: {skip_count}, 에러: {error_count}")
    
    # 최종 결과
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n=== 최종 결과 ===")
    print(f"총 처리 시간: {total_time/60:.1f}분")
    print(f"평균 속도: {total_files/total_time:.1f} files/sec")
    print(f"성공: {success_count:,}개")
    print(f"스킵: {skip_count:,}개") 
    print(f"에러: {error_count:,}개")
    print(f"결과 저장 위치: {output_dir}")

if __name__ == "__main__":
    main() 