from collections import defaultdict
from datetime import datetime, timedelta
from central_server.database.db import get_connection

def get_24h_logs(user_id):
    """user_id에 해당하는 가게의 최근 24시간 감지 로그를 조회 리스트로 반환합니다."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. user_id로 store_name 조회
        cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
        store_result = cursor.fetchone()
        
        if not store_result:
            return [] # 해당 사용자와 연결된 가게가 없으면 빈 리스트 반환

        store_name = store_result['store_name']
        
        # 2. store_name으로 cctv_data 조회 (최근 24시간)
        query = """
        SELECT event_type, time, video_url
        FROM cctv_data
        WHERE store_name = %s
        AND time >= DATE_SUB(NOW(), INTERVAL 1 DAY)
        AND time <= NOW()
        ORDER BY time DESC
        """
        cursor.execute(query, (store_name,))
        logs = cursor.fetchall()

        result = []
        for log in logs:
            result.append({
                "time": log['time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(log['time'], datetime) else str(log['time']),
                "event_type": log['event_type'],
                "video_url": log['video_url']
            })
        return result
    finally:
        cursor.close()
        conn.close()