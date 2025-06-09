import cv2
import socket
import pickle
import struct
import numpy as np

def main():
    # 웹캠 초기화
    cap = cv2.VideoCapture(0)
    
    # UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('192.168.0.7', 9999)  # 수신자 컴퓨터의 유선 IP 주소
    
    try:
        while True:
            # 웹캠에서 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                break
                
            # 프레임 크기 조정 (선택사항)
            frame = cv2.resize(frame, (640, 480))
            
            # 프레임을 바이트로 직렬화
            data = pickle.dumps(frame)
            
            # 데이터 크기 전송
            message_size = struct.pack("L", len(data))
            sock.sendto(message_size, server_address)
            
            # 실제 데이터 전송
            sock.sendto(data, server_address)
            
            # 화면에 표시 (선택사항)
            cv2.imshow('Sending...', frame)
            
            # 'q'를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        sock.close()

if __name__ == '__main__':
    main() 