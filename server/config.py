import socket

# 로컬 머신의 IP 주소 가져오기
local_ip = socket.gethostbyname(socket.gethostname())

wonho_pc = "192.168.0.15" # 원호 pc  
chaeyeon_pc = "192.168.0.21" # 채연 pc
beomjin_pc = "192.168.0.75" # 범진 pc
# wonho_pc = local_ip # 원호 pc  
# chaeyeon_pc = local_ip # 채연 pc
# beomjin_pc = local_ip # 범진 pc

AI_IP = chaeyeon_pc # AI 서버 IP
AI_PORT = 5005
MAX_PACKET_SIZE = 60000  # UDP 패킷 크기 제한

# UDP 수신
RECIEVER_IP = "0.0.0.0" # 모든 IP에서 수신
RECIEVER_PORT = 5005

# TCP 송신
CENTRAL_IP = wonho_pc # 중앙 서버 IP
CENTRAL_PORT = 6006

CENTRAL_GUI_IP = beomjin_pc # 중앙 서버 IP
CENTRAL_GUI_PORT = 6007
