import sys
import os
from mysql.connector import pooling

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