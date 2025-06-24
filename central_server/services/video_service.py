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