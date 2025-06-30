from collections import defaultdict
from datetime import datetime, timedelta
from central_server.database.db import get_connection

# def get_weekly_logs(user_id):
#     """user_id에 해당하는 가게의 최근 일주일치 감지 로그를 조회하고, event_type으로 그룹화합니다."""
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     try:
#         # 1. user_id로 store_name 조회
#         cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
#         store_result = cursor.fetchone()
        
#         if not store_result:
#             return {} # 해당 사용자와 연결된 가게가 없으면 빈 객체 반환

#         store_name = store_result['store_name']
        
#         # 2. store_name으로 cctv_data 조회
#         logs_by_event = defaultdict(list)
#         query = """
#             SELECT event_type, time, video_url
#             FROM cctv_data
#             WHERE store_name = %s AND time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
#             ORDER BY time DESC
#         """
#         cursor.execute(query, (store_name,))
#         logs = cursor.fetchall()

#         for log in logs:
#             event_type = log['event_type']
#             log_info = {
#                 "time": log['time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(log['time'], datetime) else str(log['time']),
#                 "video_url": log['video_url']
#             }
#             logs_by_event[event_type].append(log_info)

#         return dict(logs_by_event)
#     finally:
#         cursor.close()
#         conn.close()


def get_filtered_logs(filters):
    """필터 조건에 맞는 감지 로그를 반환합니다."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
        SELECT s.store_name, d.time, d.event_type, d.person_count, d.is_checked, d.video_url, d.favorite
        FROM cctv_data d
        JOIN store s ON d.store_name = s.store_name
        WHERE 1=1
    """
    where_clauses = []
    params = []

    # user_id 필터
    if filters.get('user_id'):
        where_clauses.append("s.user_id = %s")
        params.append(filters['user_id'])

    # 날짜/기간 필터
    period = filters.get('period')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    # "None" 문자열, None, null 모두 None으로 처리
    def is_none(val):
        return val is None or val == "None"

    # 둘 다 값이 있으면 에러
    if (not is_none(period)) and (not (is_none(start_date) and is_none(end_date))):
        cursor.close()
        conn.close()
        raise ValueError("period와 start_date/end_date를 동시에 지정할 수 없습니다.")

    # 날짜 범위 우선
    if not is_none(start_date) and not is_none(end_date):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        where_clauses.append("d.time >= %s AND d.time < %s")
        params.extend([start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
    elif not is_none(period):
        today = datetime.now().date()
        if period == "today":
            start = today
            end = today + timedelta(days=1)
        elif period == "week":
            start = today - timedelta(days=6)  # 6일 전부터 (오늘 포함 7일)
            end = today + timedelta(days=1)    # 내일 00:00:00까지
            # start = datetime.now() - timedelta(days=7)
            # end = datetime.now()
            # start = today - timedelta(days=today.weekday())
            # end = start + timedelta(days=7)
        elif period == "month":
            start = today.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year+1, month=1)
            else:
                end = start.replace(month=start.month+1)
        else:
            start = None
            end = None
        if start and end:
            where_clauses.append("d.time >= %s AND d.time < %s")
            params.extend([start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
    # 둘 다 None이면 전체 데이터(혹은 에러) - 필요시 처리

    # event_type (여러 개)
    if filters.get('event_type'):
        event_types = filters['event_type']
        if isinstance(event_types, list) and event_types:
            placeholders = ','.join(['%s'] * len(event_types))
            where_clauses.append(f"d.event_type IN ({placeholders})")
            params.extend(event_types)

    # # person_count (여러 개)
    # if filters.get('person_count'):
    #     person_counts = filters['person_count']
    #     if isinstance(person_counts, list) and person_counts:
    #         placeholders = ','.join(['%s'] * len(person_counts))
    #         where_clauses.append(f"d.person_count IN ({placeholders})")
    #         params.extend(person_counts)

    # is_checked (여러 개)
    if filters.get('is_checked'):
        is_checked = filters['is_checked']
        if isinstance(is_checked, list) and is_checked:
            placeholders = ','.join(['%s'] * len(is_checked))
            where_clauses.append(f"d.is_checked IN ({placeholders})")
            params.extend(is_checked)
    # favorite (여러 개)
    if filters.get('favorite'):
        favorites = filters['favorite']
        if isinstance(favorites, list) and favorites:
            placeholders = ','.join(['%s'] * len(favorites))
            where_clauses.append(f"d.favorite IN ({placeholders})")
            params.extend(favorites)

    # 최종 쿼리 조립
    query = base_query
    if where_clauses:
        query += " AND " + " AND ".join(where_clauses)
    query += " ORDER BY d.time DESC"

    try:
        cursor.execute(query, tuple(params))
        logs = cursor.fetchall()
        # datetime 객체를 문자열로 변환
        for log in logs:
            if 'time' in log and hasattr(log['time'], 'strftime'):
                log['time'] = log['time'].strftime('%Y-%m-%d %H:%M:%S')
        return logs
    finally:
        cursor.close()
        conn.close() 