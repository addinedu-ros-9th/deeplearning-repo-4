# central_server.py
import socket
import threading
import cv2
import numpy as np
import struct
import os
import json

# AI 서버로부터 수신
AI_PORT = 6006

def recv_full(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_ai(ai_conn):
    print("[Central] AI 서버 핸들러 시작")
    while True:
        try:
            # 패킷 헤더 수신 (28바이트 - metadata_size 추가)
            header_bytes = recv_full(ai_conn, 28)
            if not header_bytes:
                break
            
            # 헤더 파싱: [timestamp(8bytes), frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes), metadata_size(4bytes)]
            timestamp, frame_id, packet_idx, num_packets, data_size, metadata_size = struct.unpack('!dIIIII', header_bytes)
            
            # 패킷 데이터 수신
            packet_data = recv_full(ai_conn, data_size)
            if not packet_data:
                break

            print(f"[Central] AI서버에서 수신: 프레임 {frame_id}, 패킷 {packet_idx+1}/{num_packets}, 크기: {data_size} bytes")
            
            try:
                # 데이터가 클립인지 프레임인지 확인 (크기로 판단)
                if data_size > 1000000:  # 1MB 이상이면 클립으로 간주
                    # 메타데이터와 비디오 데이터 분리
                    metadata_json = packet_data[:metadata_size]
                    video_data = packet_data[metadata_size:]
                    
                    # 메타데이터 파싱
                    metadata = json.loads(metadata_json.decode('utf-8'))
                    action_name = metadata['action_name']
                    person_count = metadata['person_count']
                    timestamp_str = metadata['timestamp']
                    
                    # 클립 저장 디렉토리 생성
                    clips_dir = "received_clips"
                    if not os.path.exists(clips_dir):
                        os.makedirs(clips_dir)
                    
                    # 의미있는 파일명으로 저장
                    clip_filename = os.path.join(clips_dir, f"{action_name}_p{person_count}_{timestamp_str}.mp4")
                    with open(clip_filename, 'wb') as f:
                        f.write(video_data)
                    print(f"[Central] 클립 저장됨: {clip_filename}")
                else:
                    print(f"[Central] 프레임 데이터 수신 (저장하지 않음): {data_size} bytes")
                    
            except Exception as e:
                print(f"[Central] 데이터 처리 중 오류: {e}")
                
        except Exception as e:
            print(f"[Central] 수신 중 오류: {e}")
            break
    
    print("[Central] AI 서버 핸들러 종료")

print("[Central] 중앙서버 시작...")

# AI 서버 연결 대기
ai_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ai_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ai_sock.bind(('0.0.0.0', AI_PORT))
ai_sock.listen(1)
print(f"[Central] AI 서버 연결 대기 중... (Port: {AI_PORT})")
ai_conn, ai_addr = ai_sock.accept()
print(f"[Central] AI 서버 연결됨: {ai_addr}")

# AI 서버 핸들러 시작
ai_thread = threading.Thread(target=handle_ai, args=(ai_conn,))
ai_thread.start()

print("[Central] 클립 수신 대기 중...")

try:
    ai_thread.join()
except KeyboardInterrupt:
    print("\n[Central] 서버 종료 중...")
finally:
    ai_conn.close()
    ai_sock.close()
    print("[Central] 서버 종료됨")