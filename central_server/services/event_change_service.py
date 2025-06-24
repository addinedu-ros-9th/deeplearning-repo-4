from central_server.database.db import get_connection

def update_event_type(user_id, store_name, date, new_type):
    """조건에 맞는 event_type을 변경"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # date는 'YYYYMMDD' → 'YYYY-MM-DD'로 변환 필요
        date_str = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        query = """
            UPDATE cctv_data d
            JOIN store s ON d.store_id = s.store_id
            SET d.event_type = %s
            WHERE s.user_id = %s AND s.store_name = %s AND DATE(d.time) = %s
        """
        cursor.execute(query, (new_type, user_id, store_name, date_str))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def update_is_checked(user_id, store_name, date, is_checked=0):
    """조건에 맞는 is_checked 값을 변경"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        date_str = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        query = """
            UPDATE cctv_data d
            JOIN store s ON d.store_id = s.store_id
            SET d.is_checked = %s
            WHERE s.user_id = %s AND s.store_name = %s AND DATE(d.time) = %s
        """
        cursor.execute(query, (is_checked, user_id, store_name, date_str))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close() 