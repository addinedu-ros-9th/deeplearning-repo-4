from datetime import datetime, timedelta

def get_kst_now():
    """한국 표준시(KST) 기준 현재 시간을 반환합니다."""
    return datetime.utcnow() + timedelta(hours=9)

def format_to_string(dt_object):
    """datetime 객체를 'YYYY-MM-DD HH:MM:SS' 형태의 문자열로 변환합니다."""
    return dt_object.strftime('%Y-%m-%d %H:%M:%S') 