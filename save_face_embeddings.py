import cv2
import numpy as np
import os
import pickle
from typing import List, Dict
import logging
from ultralytics import YOLO
from deepface import DeepFace

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceFeatureExtractorYOLO:
    """
    YOLO로 얼굴을 감지하고 DeepFace로 특징(임베딩)을 추출하는 클래스 (YOLOv8n-face.pt 전용)
    """
    
    def __init__(self, yolo_model_path: str = "yolov8n-face.pt", deepface_model_name: str = "ArcFace"):
        self.yolo_model = YOLO(yolo_model_path)
        self.deepface_model_name = deepface_model_name
        self.deepface_model = DeepFace.build_model(deepface_model_name)
    
    def extract_face_features_from_video(self, video_path: str, frame_interval: int = 1, save_faces_dir: str = "faces"):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {video_path}")
        frame_count = 0
        features = []
        os.makedirs(save_faces_dir, exist_ok=True)  # 폴더 생성
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                results = self.yolo_model(frame)
                for result in results:
                    boxes = result.boxes
                    if boxes is not None and len(boxes) > 0:
                        for i, box in enumerate(boxes):
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            face_roi = frame[y1:y2, x1:x2]
                            h, w = face_roi.shape[:2]
                            # 너무 작은 얼굴은 건너뜀
                            if h < 60 or w < 60:
                                continue
                            # 얼굴을 224x224로 리사이즈
                            face_resized = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                            # 얼굴 이미지 저장
                            face_filename = os.path.join(save_faces_dir, f"frame{frame_count}_face{i}.jpg")
                            cv2.imwrite(face_filename, face_resized)
                            try:
                                embedding_result = DeepFace.represent(
                                    face_resized,
                                    model_name=self.deepface_model_name,
                                    enforce_detection=False
                                )
                                if embedding_result and isinstance(embedding_result, list):
                                    embedding = embedding_result[0]["embedding"]
                                    features.append({
                                        'frame': frame_count,
                                        'box': [x1, y1, x2, y2],
                                        'embedding': embedding
                                    })
                            except Exception as e:
                                logger.warning(f"DeepFace 임베딩 추출 실패: {e}")
            frame_count += 1
        cap.release()
        print(f"총 {len(features)}개의 얼굴 특징(임베딩)이 추출되었습니다.")
        return features
    
    def save_embeddings(self, features, filepath):
        """
        추출된 임베딩을 파일로 저장
        """
        with open(filepath, 'wb') as f:
            pickle.dump(features, f)
        print(f"임베딩이 {filepath}에 저장되었습니다.")

def main():
    extractor = FaceFeatureExtractorYOLO(yolo_model_path="yolov8n-face.pt", deepface_model_name="ArcFace")
    
    # 영상에서 얼굴 임베딩 추출 및 저장
    video_path = "/home/koo4802/Desktop/Abandon/abandon12.mp4"
    features = extractor.extract_face_features_from_video(video_path, frame_interval=1)
    extractor.save_embeddings(features, "abandon12_embeddings.pkl")

if __name__ == "__main__":
    main() 