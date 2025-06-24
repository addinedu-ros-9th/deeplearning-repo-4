from central_server.database.db import get_connection

def update_event_type(user_id, store_name, timestamp, new_type):
    """조건에 맞는 event_type을 변경"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE cctv_data d
            JOIN store s ON d.store_name = s.store_name
            SET d.event_type = %s
            WHERE s.user_id = %s AND s.store_name = %s AND d.time = %s
        """
        cursor.execute(query, (new_type, user_id, store_name, timestamp))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def update_is_checked(user_id, store_name, timestamp, is_checked=0):
    """조건에 맞는 is_checked 값을 변경"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE cctv_data d
            JOIN store s ON d.store_name = s.store_name
            SET d.is_checked = %s
            WHERE s.user_id = %s AND s.store_name = %s AND d.time = %s
        """
        cursor.execute(query, (is_checked, user_id, store_name, timestamp))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close() 