import sys
import os
from mysql.connector import pooling

# 이 파일의 위치를 기준으로 프로젝트 루트 폴더(deeplearning-repo-4)의 경로를 계산
# os.path.abspath(__file__) -> /home/ckim/deeplearning-repo-4/central_server/db/mysql_connect.py
# os.path.dirname(...) -> .../central_server/db
# os.path.dirname(...) -> .../central_server
# os.path.dirname(...) -> /home/ckim/deeplearning-repo-4
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from central_server.config import DB_CONFIG

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **DB_CONFIG
)

def get_connection():
    return pool.get_connection()