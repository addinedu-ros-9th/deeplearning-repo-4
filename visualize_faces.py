import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from ultralytics import YOLO
import pickle
import insightface
from sklearn.metrics.pairwise import cosine_similarity

class FaceVisualizer:
    """
    얼굴 이미지를 시각화하여 데이터 품질을 확인하는 클래스
    """
    
    def __init__(self, yolo_model_path: str = "yolov8n-face.pt"):
        self.yolo_model = YOLO(yolo_model_path)
    
    def extract_and_visualize_faces_from_video(self, video_path: str, frame_interval: int = 1, max_faces: int = 20):
        """
        영상에서 얼굴을 추출하고 시각화
        """
        if not os.path.exists(video_path):
            print(f"영상 파일을 찾을 수 없습니다: {video_path}")
            return
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"영상을 열 수 없습니다: {video_path}")
            return
        
        frame_count = 0
        extracted_faces = []
        
        print("얼굴 추출 중...")
        
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
                            
                            # 원본 얼굴과 리사이즈된 얼굴 저장
                            face_128 = cv2.resize(face_roi, (128, 128), interpolation=cv2.INTER_CUBIC)
                            face_224 = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                            
                            extracted_faces.append({
                                'frame': frame_count,
                                'original': face_roi,
                                'resized_128': face_128,
                                'resized_224': face_224,
                                'size': (h, w),
                                'box': [x1, y1, x2, y2]
                            })
                            
                            if len(extracted_faces) >= max_faces:
                                break
                
                if len(extracted_faces) >= max_faces:
                    break
            
            frame_count += 1
        
        cap.release()
        print(f"총 {len(extracted_faces)}개의 얼굴을 추출했습니다.")
        
        # 시각화
        self.visualize_faces(extracted_faces, video_path)
        
        return extracted_faces
    
    def visualize_faces(self, faces, video_path):
        """
        추출된 얼굴들을 시각화
        """
        if not faces:
            print("시각화할 얼굴이 없습니다.")
            return
        
        # 서브플롯 설정
        n_faces = min(len(faces), 12)  # 최대 12개만 표시
        cols = 4
        rows = (n_faces + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(16, 4*rows))
        if rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, face_data in enumerate(faces[:n_faces]):
            row = i // cols
            col = i % cols
            
            # 224x224 크기로 시각화
            face_img = cv2.cvtColor(face_data['resized_224'], cv2.COLOR_BGR2RGB)
            
            axes[row, col].imshow(face_img)
            axes[row, col].set_title(f"Frame {face_data['frame']}\nSize: {face_data['size']}")
            axes[row, col].axis('off')
        
        # 빈 서브플롯 숨기기
        for i in range(n_faces, rows * cols):
            row = i // cols
            col = i % cols
            axes[row, col].axis('off')
        
        plt.suptitle(f'Extracted Faces from {os.path.basename(video_path)}', fontsize=16)
        plt.tight_layout()
        plt.show()
        
        # 통계 정보 출력
        self.print_face_statistics(faces)
    
    def print_face_statistics(self, faces):
        """
        얼굴 통계 정보 출력
        """
        if not faces:
            return
        
        sizes = [face['size'] for face in faces]
        heights = [h for h, w in sizes]
        widths = [w for h, w in sizes]
        
        print("\n=== 얼굴 통계 ===")
        print(f"총 얼굴 수: {len(faces)}")
        print(f"평균 높이: {np.mean(heights):.1f}px")
        print(f"평균 너비: {np.mean(widths):.1f}px")
        print(f"최소 높이: {min(heights)}px")
        print(f"최대 높이: {max(heights)}px")
        print(f"최소 너비: {min(widths)}px")
        print(f"최대 너비: {max(widths)}px")
        
        # 크기별 분포
        small_faces = len([h for h in heights if h < 80])
        medium_faces = len([h for h in heights if 80 <= h < 120])
        large_faces = len([h for h in heights if h >= 120])
        
        print(f"\n크기별 분포:")
        print(f"작은 얼굴 (<80px): {small_faces}개 ({small_faces/len(faces)*100:.1f}%)")
        print(f"중간 얼굴 (80-120px): {medium_faces}개 ({medium_faces/len(faces)*100:.1f}%)")
        print(f"큰 얼굴 (≥120px): {large_faces}개 ({large_faces/len(faces)*100:.1f}%)")
    
    def visualize_saved_embeddings(self, embedding_file: str):
        """
        저장된 임베딩 파일에서 얼굴 정보 시각화
        """
        if not os.path.exists(embedding_file):
            print(f"임베딩 파일을 찾을 수 없습니다: {embedding_file}")
            return
        
        try:
            with open(embedding_file, 'rb') as f:
                saved_features = pickle.load(f)
            
            print(f"저장된 임베딩 파일: {embedding_file}")
            print(f"총 얼굴 수: {len(saved_features)}")
            
            # 프레임별 분포
            frames = [feature['frame'] for feature in saved_features]
            print(f"프레임 범위: {min(frames)} ~ {max(frames)}")
            
            # 박스 크기 분석
            boxes = [feature['box'] for feature in saved_features]
            sizes = [(box[3]-box[1], box[2]-box[0]) for box in boxes]  # (height, width)
            
            heights = [h for h, w in sizes]
            widths = [w for h, w in sizes]
            
            print(f"평균 얼굴 크기: {np.mean(heights):.1f} x {np.mean(widths):.1f}")
            print(f"최소 얼굴 크기: {min(heights)} x {min(widths)}")
            print(f"최대 얼굴 크기: {max(heights)} x {max(widths)}")
            
        except Exception as e:
            print(f"임베딩 파일 로드 오류: {e}")

    def compare_videos(self, video1_path: str, video2_path: str, max_faces_per_video: int = 10, use_frontal_only: bool = True):
        """
        두 영상에서 얼굴을 추출하고 평균 유사도를 계산
        """
        print(f"\n=== 영상 비교: {os.path.basename(video1_path)} vs {os.path.basename(video2_path)} ===")
        
        # 첫 번째 영상에서 얼굴 추출
        print(f"\n1. {os.path.basename(video1_path)}에서 얼굴 추출 중...")
        faces1 = self.extract_faces_from_video(video1_path, max_faces=max_faces_per_video)
        
        # 두 번째 영상에서 얼굴 추출
        print(f"\n2. {os.path.basename(video2_path)}에서 얼굴 추출 중...")
        faces2 = self.extract_faces_from_video(video2_path, max_faces=max_faces_per_video)
        
        if not faces1 or not faces2:
            print("얼굴을 추출할 수 없습니다.")
            return None
        
        # 가장 정면에 가까운 얼굴만 선택
        if use_frontal_only:
            print(f"\n3. 가장 정면에 가까운 얼굴 선택 중...")
            faces1 = self.get_most_frontal_faces(faces1, num_faces=1)
            faces2 = self.get_most_frontal_faces(faces2, num_faces=1)
        
        print(f"\n4. 얼굴 임베딩 추출 중...")
        
        # InsightFace 모델 준비
        app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        recognition_model = app.models['recognition']
        
        def get_embedding_from_array(face_img):
            face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            face_img_resized = cv2.resize(face_img_rgb, (112, 112))
            embedding = recognition_model.get_feat(face_img_resized).flatten()
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        
        # 모든 얼굴의 임베딩 추출
        embeddings1 = []
        embeddings2 = []
        
        for face in faces1:
            embedding = get_embedding_from_array(face['resized_224'])
            if embedding is not None:
                embeddings1.append(embedding)
        
        for face in faces2:
            embedding = get_embedding_from_array(face['resized_224'])
            if embedding is not None:
                embeddings2.append(embedding)
        
        if not embeddings1 or not embeddings2:
            print("임베딩 추출에 실패했습니다.")
            return None
        
        print(f"영상1 얼굴 수: {len(embeddings1)}")
        print(f"영상2 얼굴 수: {len(embeddings2)}")
        
        # 모든 얼굴 쌍의 유사도 계산
        similarities = []
        print(f"\n5. {len(embeddings1)} x {len(embeddings2)} = {len(embeddings1) * len(embeddings2)}개 쌍 비교 중...")
        
        for i, emb1 in enumerate(embeddings1):
            for j, emb2 in enumerate(embeddings2):
                similarity = np.dot(emb1, emb2)
                similarities.append(similarity)
                print(f"  얼굴 {i+1}-{j+1}: {similarity:.3f}")
        
        # 평균 유사도 계산
        avg_similarity = np.mean(similarities)
        max_similarity = np.max(similarities)
        min_similarity = np.min(similarities)
        
        print(f"\n=== 결과 ===")
        print(f"평균 유사도: {avg_similarity:.3f}")
        print(f"최대 유사도: {max_similarity:.3f}")
        print(f"최소 유사도: {min_similarity:.3f}")
        
        # 결과 해석
        if avg_similarity >= 0.6:
            result = "같은 사람들 (매우 높은 확률)"
        elif avg_similarity >= 0.4:
            result = "같은 사람들일 가능성이 높음"
        elif avg_similarity >= 0.3:
            result = "경계선 (추가 검증 필요)"
        else:
            result = "다른 사람들 (매우 높은 확률)"
        
        print(f"결론: {result}")
        
        return {
            'avg_similarity': avg_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'similarities': similarities
        }
    
    def extract_faces_from_video(self, video_path: str, max_faces: int = 10):
        """
        영상에서 얼굴만 추출 (시각화 없이)
        """
        if not os.path.exists(video_path):
            print(f"영상 파일을 찾을 수 없습니다: {video_path}")
            return []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"영상을 열 수 없습니다: {video_path}")
            return []
        
        frame_count = 0
        extracted_faces = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % 5 == 0:  # 5프레임마다 처리
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
                            
                            # 224x224로 리사이즈
                            face_224 = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                            
                            # 얼굴의 정면도 계산 (박스의 가로세로 비율로 대략 추정)
                            aspect_ratio = w / h
                            # 정면 얼굴은 보통 0.8~1.2 비율
                            frontal_score = 1.0 - abs(aspect_ratio - 1.0)
                            
                            extracted_faces.append({
                                'frame': frame_count,
                                'resized_224': face_224,
                                'size': (h, w),
                                'box': [x1, y1, x2, y2],
                                'frontal_score': frontal_score
                            })
                            
                            if len(extracted_faces) >= max_faces:
                                break
                
                if len(extracted_faces) >= max_faces:
                    break
            
            frame_count += 1
        
        cap.release()
        print(f"총 {len(extracted_faces)}개의 얼굴을 추출했습니다.")
        
        return extracted_faces
    
    def get_most_frontal_faces(self, faces, num_faces=1):
        """
        가장 정면에 가까운 얼굴들을 선택
        """
        if not faces:
            return []
        
        # 정면도 점수로 정렬
        sorted_faces = sorted(faces, key=lambda x: x['frontal_score'], reverse=True)
        
        # 상위 num_faces개 선택
        selected_faces = sorted_faces[:num_faces]
        
        print(f"가장 정면에 가까운 얼굴 {len(selected_faces)}개 선택:")
        for i, face in enumerate(selected_faces):
            print(f"  얼굴 {i+1}: 정면도 점수 {face['frontal_score']:.3f}, 크기 {face['size']}")
        
        return selected_faces

def main():
    visualizer = FaceVisualizer()
    
    # 영상끼리 비교
    print("=== 영상 비교 ===")
    video1_path = "/home/koo4802/Desktop/Broken/broken19.mp4"
    video2_path = "/home/koo4802/Desktop/Normal/normal109.mp4"  # 다른 영상 경로로 변경하세요
    
    if os.path.exists(video2_path):
        result = visualizer.compare_videos(video1_path, video2_path, max_faces_per_video=5)
        if result:
            print(f"\n영상 비교 완료!")
    else:
        print(f"비교할 영상이 없습니다: {video2_path}")
        print("다른 영상 경로로 video2_path를 변경해주세요.")

if __name__ == "__main__":
    main() 