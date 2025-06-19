# central_server.py
import socket
import threading
import cv2
import numpy as np

# AI 서버로부터 수신
AI_PORT = 6006
# GUI와 통신
GUI_PORT = 7007

def handle_ai(ai_conn, gui_conn):
    print("[Central] AI 서버 핸들러 시작")
    while True:
        try:
            # 프레임 데이터 수신
            data = ai_conn.recv(65536)
            if not data:
                print("[Central] AI 서버 연결 종료")
                break
            
            frame_size = len(data)
            print(f"[Central] AI서버에서 수신: {frame_size} bytes")
            
            try:
                # 프레임 디코딩 테스트 (데이터 무결성 확인)
                nparr = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is None:
                    print("[Central] 프레임 디코딩 실패")
                    continue
                
                # GUI로 데이터 전달
                gui_conn.sendall(data)
                print(f"[Central] GUI로 전송: {frame_size} bytes")
            except Exception as e:
                print(f"[Central] 프레임 처리 중 오류: {e}")
                
        except Exception as e:
            print(f"[Central] 수신 중 오류: {e}")
            break
    
    print("[Central] AI 서버 핸들러 종료")

def handle_gui(gui_conn, ai_conn):
    print("[Central] GUI 핸들러 시작")
    while True:
        try:
            data = gui_conn.recv(65536)
            if not data:
                print("[Central] GUI 연결 종료")
                break
            # 필요시 AI 서버로 데이터 전달
            ai_conn.sendall(data)
        except Exception as e:
            print(f"[Central] GUI 통신 중 오류: {e}")
            break
    print("[Central] GUI 핸들러 종료")

print("[Central] 중앙서버 시작...")

# AI 서버 연결 대기
ai_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ai_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ai_sock.bind(('0.0.0.0', AI_PORT))
ai_sock.listen(1)
print(f"[Central] AI 서버 연결 대기 중... (Port: {AI_PORT})")
ai_conn, ai_addr = ai_sock.accept()
print(f"[Central] AI 서버 연결됨: {ai_addr}")

# GUI 연결 대기
gui_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gui_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
gui_sock.bind(('0.0.0.0', GUI_PORT))
gui_sock.listen(1)
print(f"[Central] GUI 연결 대기 중... (Port: {GUI_PORT})")
gui_conn, gui_addr = gui_sock.accept()
print(f"[Central] GUI 연결됨: {gui_addr}")

# 스레드로 양방향 통신
ai_thread = threading.Thread(target=handle_ai, args=(ai_conn, gui_conn))
gui_thread = threading.Thread(target=handle_gui, args=(gui_conn, ai_conn))

ai_thread.start()
gui_thread.start()

print("[Central] 양방향 통신 시작...")

try:
    ai_thread.join()
    gui_thread.join()
except KeyboardInterrupt:
    print("\n[Central] 서버 종료 중...")
finally:
    ai_conn.close()
    gui_conn.close()
    ai_sock.close()
    gui_sock.close()