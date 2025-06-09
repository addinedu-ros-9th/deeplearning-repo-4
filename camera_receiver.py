import cv2
import socket
import pickle
import struct
import numpy as np

def main():
    # UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 9999)  # 모든 인터페이스에서 수신
    sock.bind(server_address)
    
    print("Waiting for video stream...")
    
    try:
        while True:
            # 데이터 크기 수신
            data, addr = sock.recvfrom(struct.calcsize("L"))
            message_size = struct.unpack("L", data)[0]
            
            # 실제 데이터 수신
            data = b''
            while len(data) < message_size:
                packet, addr = sock.recvfrom(message_size - len(data))
                if not packet:
                    break
                data += packet
            
            # 데이터를 프레임으로 변환
            frame = pickle.loads(data)
            
            # 화면에 표시
            cv2.imshow('Receiving...', frame)
            
            # 'q'를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cv2.destroyAllWindows()
        sock.close()

if __name__ == '__main__':
    main() 