# ai_server.py
import socket
import threading
import cv2
import numpy as np
import time
import struct

# UDP 수신
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

# TCP 송신
CENTRAL_IP = "192.168.0.15"
CENTRAL_PORT = 6006
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((CENTRAL_IP, CENTRAL_PORT))

# FPS 제어를 위한 설정
fps = 5
frame_interval = 1.0 / fps
last_frame_time = time.time()

# 프레임 재조립을 위한 버퍼
frame_buffers = {}  # {frame_id: {packet_idx: data, ...}}

print(f"[AI서버] 1920x1080 해상도, {fps}fps로 수신 대기 중...")

def reassemble_frame(frame_id, packets_info):
    """패킷들을 재조립하여 완전한 프레임 생성"""
    num_packets = packets_info['num_packets']
    packets = packets_info['packets']
    
    # 모든 패킷이 수신되었는지 확인
    if len(packets) != num_packets:
        return None
    
    # 패킷들을 순서대로 결합
    frame_data = b''
    for i in range(num_packets):
        if i in packets:
            frame_data += packets[i]
        else:
            return None  # 패킷 누락
    
    return frame_data

while True:
    data, addr = udp_sock.recvfrom(65536)
    current_time = time.time()
    
    # 패킷 헤더 파싱 (16바이트)
    if len(data) < 16:
        continue
    
    header = data[:16]
    frame_id, packet_idx, num_packets, data_size = struct.unpack('!IIII', header)
    packet_data = data[16:16+data_size]
    
    print(f"[AI서버] 프레임 {frame_id}, 패킷 {packet_idx+1}/{num_packets}, 크기: {len(packet_data)} bytes")
    
    # 프레임 버퍼에 패킷 저장
    if frame_id not in frame_buffers:
        frame_buffers[frame_id] = {'num_packets': num_packets, 'packets': {}}
    
    frame_buffers[frame_id]['packets'][packet_idx] = packet_data
    
    # 프레임이 완성되었는지 확인
    if len(frame_buffers[frame_id]['packets']) == num_packets:
        # FPS 제어: 지정된 간격으로만 프레임 처리
        if current_time - last_frame_time >= frame_interval:
            # 프레임 재조립
            complete_frame_data = reassemble_frame(frame_id, frame_buffers[frame_id])
            
            if complete_frame_data:
                print(f"[AI서버] 프레임 {frame_id} 완성, 크기: {len(complete_frame_data)} bytes")
                tcp_sock.sendall(complete_frame_data)
                print(f"[AI서버] TCP로 전송: {len(complete_frame_data)} bytes")
                
                # JPEG 바이너리를 numpy array로 변환 후 디코딩
                nparr = np.frombuffer(complete_frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # 1920x1080 해상도에 맞는 윈도우 크기로 조정
                    cv2.namedWindow("Received Frame", cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Received Frame", 1280, 720)  # 화면에 맞게 크기 조정
                    cv2.imshow("Received Frame", frame)
                    last_frame_time = current_time
            
            # 완성된 프레임 버퍼 삭제
            del frame_buffers[frame_id]
    
    # 오래된 프레임 버퍼 정리 (메모리 누수 방지)
    current_frame_id = frame_id
    old_frames = [fid for fid in frame_buffers.keys() if fid < current_frame_id - 10]
    for old_frame in old_frames:
        del frame_buffers[old_frame]
    
    if cv2.waitKey(1) == 27:
        break

tcp_sock.close()
cv2.destroyAllWindows()