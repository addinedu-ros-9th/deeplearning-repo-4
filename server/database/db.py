from .config import DB_CONFIG
import pymysql

def insert_clip(store_name, cctv_no, time_str, event_type, confidence, person_count, is_checked, video_url):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO cctv_data
                (store_name, cctv_no, time, event_type, confidence, person_count, is_checked, video_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (store_name, cctv_no, time_str, event_type, confidence, person_count, is_checked, video_url))
        conn.commit()
    finally:
        conn.close()
