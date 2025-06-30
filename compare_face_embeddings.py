import cv2
import numpy as np
import os
import pickle
from typing import List, Dict
import logging
from ultralytics import YOLO
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity

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
    
    def extract_face_features_from_video(self, video_path: str, frame_interval: int = 1):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {video_path}")
        frame_count = 0
        features = []
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
    
    def compare_faces(self, embedding1, embedding2, threshold=0.6):
        """
        두 얼굴 임베딩을 비교하여 같은 사람인지 판단
        """
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        is_same_person = similarity > threshold
        return is_same_person, similarity
    
    def find_matching_faces(self, target_embedding, face_features, threshold=0.6):
        """
        타겟 임베딩과 일치하는 얼굴들을 찾기
        """
        matches = []
        for feature in face_features:
            is_match, similarity = self.compare_faces(target_embedding, feature['embedding'], threshold)
            if is_match:
                matches.append({
                    'frame': feature['frame'],
                    'box': feature['box'],
                    'similarity': similarity
                })
        return matches
    
    def load_embeddings(self, filepath):
        """
        저장된 임베딩을 파일에서 로드
        """
        with open(filepath, 'rb') as f:
            features = pickle.load(f)
        print(f"{filepath}에서 {len(features)}개의 임베딩을 로드했습니다.")
        return features

def main():
    extractor = FaceFeatureExtractorYOLO(yolo_model_path="yolov8n-face.pt", deepface_model_name="ArcFace")
    
    # 1. 저장된 임베딩 로드
    try:
        saved_features = extractor.load_embeddings("broken4_embeddings.pkl")
    except FileNotFoundError:
        print("저장된 임베딩 파일이 없습니다. 먼저 save_face_embeddings.py를 실행하여 영상에서 임베딩을 추출하고 저장하세요.")
        return
    
    # 2. 비교할 영상에서 얼굴 임베딩 추출
    video_path = "/home/koo4802/Desktop/Broken/broken19.mp4"
    features = extractor.extract_face_features_from_video(video_path, frame_interval=1)
    
    # 3. 저장된 임베딩과 새로운 영상 비교
    if saved_features and features:
        target_embedding = saved_features[0]['embedding']  # 저장된 첫 번째 얼굴
        matches = extractor.find_matching_faces(target_embedding, features, threshold=0.8)
        
        print(f"\n=== 얼굴 비교 결과 ===")
        print(f"저장된 얼굴과 일치하는 얼굴: {len(matches)}개")
        for match in matches:
            print(f"프레임 {match['frame']}: 유사도 {match['similarity']:.3f}")

if __name__ == "__main__":
    main() 