from collections import defaultdict
from datetime import datetime
from central_server.database.db import get_connection

def get_weekly_logs(user_id):
    """user_id에 해당하는 가게의 최근 일주일치 감지 로그를 조회하고, event_type으로 그룹화합니다."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. user_id로 store_name 조회
        cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
        store_result = cursor.fetchone()
        
        if not store_result:
            return {} # 해당 사용자와 연결된 가게가 없으면 빈 객체 반환

        store_name = store_result['store_name']
        
        # 2. store_name으로 cctv_data 조회
        logs_by_event = defaultdict(list)
        query = """
            SELECT event_type, time, video_url
            FROM cctv_data
            WHERE store_name = %s AND time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY time DESC
        """
        cursor.execute(query, (store_name,))
        logs = cursor.fetchall()

        for log in logs:
            event_type = log['event_type']
            log_info = {
                "time": log['time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(log['time'], datetime) else str(log['time']),
                "video_url": log['video_url']
            }
            logs_by_event[event_type].append(log_info)

        return dict(logs_by_event)
    finally:
        cursor.close()
        conn.close()


def get_filtered_logs(filters):
    """필터 조건에 맞는 감지 로그를 반환합니다."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
        SELECT s.store_name, d.timestamp, d.event_type, d.person_count, d.is_checked, d.video_url
        FROM detection_logs d
        JOIN store s ON d.store_id = s.store_id
    """
    where_clauses = []
    params = []

    # 필터 조건에 따라 WHERE 절 동적 생성
    if filters.get('store_id'):
        where_clauses.append("d.store_id = %s")
        params.append(filters.get('store_id'))
    if filters.get('event_type'):
        where_clauses.append("d.event_type = %s")
        params.append(filters.get('event_type'))
    if filters.get('start_date'):
        where_clauses.append("d.timestamp >= %s")
        params.append(filters.get('start_date'))
    if filters.get('end_date'):
        where_clauses.append("d.timestamp < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.append(filters.get('end_date'))
    if 'is_checked' in filters:
        where_clauses.append("d.is_checked = %s")
        params.append(filters.get('is_checked'))

    query = base_query
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY d.timestamp DESC"

    try:
        cursor.execute(query, tuple(params))
        logs = cursor.fetchall()
        # datetime 객체를 json으로 변환 가능하게 문자열로 변경
        for log in logs:
            if 'timestamp' in log and hasattr(log['timestamp'], 'strftime'):
                log['timestamp'] = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return logs
    finally:
        cursor.close()
        conn.close() 