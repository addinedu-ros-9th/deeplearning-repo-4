# central_server.py
import socket
import threading

# AI 서버로부터 수신
AI_PORT = 6006
# GUI와 통신
GUI_PORT = 7007

def handle_ai(ai_conn, gui_conn):
    while True:
        data = ai_conn.recv(65536)
        if not data:
            break
        print(f"[Central] AI서버에서 수신: {len(data)} bytes")
        # GUI로 데이터 전달
        gui_conn.sendall(data)
        print(f"[Central] GUI로 전송: {len(data)} bytes")

def handle_gui(gui_conn, ai_conn):
    while True:
        data = gui_conn.recv(65536)
        if not data:
            break
        # 필요시 AI 서버로 데이터 전달
        ai_conn.sendall(data)

# AI 서버 연결 대기
ai_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ai_sock.bind(('0.0.0.0', AI_PORT))
ai_sock.listen(1)
ai_conn, _ = ai_sock.accept()

# GUI 연결 대기
gui_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gui_sock.bind(('0.0.0.0', GUI_PORT))
gui_sock.listen(1)
gui_conn, _ = gui_sock.accept()

# 스레드로 양방향 통신
threading.Thread(target=handle_ai, args=(ai_conn, gui_conn)).start()
threading.Thread(target=handle_gui, args=(gui_conn, ai_conn)).start()