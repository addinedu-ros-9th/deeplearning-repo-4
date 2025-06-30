from central_server.config import VIDEO_BASE_DIR
from central_server.database.db import get_connection
import os

def get_video_path(video_url):
    """video_url에 해당하는 실제 파일 경로를 반환합니다."""
    video_path = os.path.join(VIDEO_BASE_DIR, video_url)
    if os.path.exists(video_path):
        return video_path
    else:
        return None

def delete_video_file(video_url):
    """비디오 파일을 삭제합니다."""
    try:
        file_path = get_video_path(video_url)
        if not file_path:
            return None

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        delete_query = "DELETE FROM cctv_data WHERE video_url = %s"
        cursor.execute(delete_query, (video_url,))
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()

        file_deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True

        if deleted_count > 0 and file_deleted:
            return file_path
        else:
            return None
    except Exception as e:
        print(f"VideoService: Error deleting video {video_url}: {e}")
        return None

def delete_checked_videos(user_id, video_urls):
    """선택된 여러 영상들을 삭제합니다."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # user_id로 store_name 찾기
        cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
        store_row = cursor.fetchone()
        if not store_row:
            cursor.close()
            conn.close()
            return False
        
        store_name = store_row['store_name']
        deleted_count = 0
        
        for video_url in video_urls:
            # DB에서 삭제 (해당 user의 store_name과 일치하는 경우만)
            delete_query = "DELETE FROM cctv_data WHERE video_url = %s AND store_name = %s"
            cursor.execute(delete_query, (video_url, store_name))
            if cursor.rowcount > 0:
                deleted_count += 1
                
                # 파일 삭제
                file_path = get_video_path(video_url)
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count > 0
    except Exception as e:
        print(f"VideoService: Error deleting checked videos: {e}")
        return False

def update_video_favorite(user_id, video_url, favorite):
    """영상의 즐겨찾기 상태를 업데이트합니다."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # user_id로 store_name 찾기
        cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
        store_row = cursor.fetchone()
        if not store_row:
            cursor.close()
            conn.close()
            return False
        
        store_name = store_row['store_name']
        
        # 즐겨찾기 상태 업데이트 (해당 user의 store_name과 일치하는 경우만)
        update_query = "UPDATE cctv_data SET favorite = %s WHERE video_url = %s AND store_name = %s"
        cursor.execute(update_query, (favorite, video_url, store_name))
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return updated_count > 0
    except Exception as e:
        print(f"VideoService: Error updating video favorite: {e}")
        return False 