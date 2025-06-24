DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "0000",
    "database": "GigachadDb",
    "port": 3306
}

import os
VIDEO_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../server/received_clips/')
)