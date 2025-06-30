from central_server.database.db import get_connection
from collections import defaultdict
from datetime import datetime

def get_status_data(user_id, date):
    """
    user_id와 date(YYYYMM)로 해당 년도의 1월부터 12월까지 event_type별 count, ratio, 2시간 단위 time_distribution을 집계하여 반환합니다.
    미래 월은 0으로 채워서 반환합니다.
    """
    event_types = ['broken', 'abandon', 'theft', 'light_off']
    # 2시간 단위 구간
    time_slots = [f"{str(h).zfill(2)}-{str(h+2).zfill(2)}" for h in range(0, 24, 2)]
    result = {
        "user_id": user_id,
        "event_types": event_types,
        "monthly_stats": []
    }
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # date: "2025-06"
        year, month = map(int, date.split('-'))
        # 현재 날짜 확인
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # 요청받은 연도의 1월부터 12월까지 모든 월
        months = [f"{year}-{str(m).zfill(2)}" for m in range(1, 13)]

        # user_id로 store_name 찾기
        cursor.execute("SELECT store_name FROM store WHERE user_id = %s", (user_id,))
        store_row = cursor.fetchone()
        if not store_row:
            return result
        store_name = store_row['store_name']

        for ym in months:
            count_dict = {etype: 0 for etype in event_types}
            slot_dict = {slot: [0]*len(event_types) for slot in time_slots}
            
            # 미래 월인지 확인
            ym_year, ym_month = map(int, ym.split('-'))
            is_future = (ym_year > current_year) or (ym_year == current_year and ym_month > current_month)
            
            if not is_future:
                # 과거/현재 월인 경우에만 DB에서 데이터 조회
                query = f"""
                    SELECT event_type, time
                    FROM cctv_data
                    WHERE store_name = %s AND DATE_FORMAT(time, '%Y-%m') = %s
                """
                cursor.execute(query, (store_name, ym))
                rows = cursor.fetchall()
                total = 0
                for row in rows:
                    etype = row['event_type']
                    t = row['time']
                    if etype not in event_types:
                        continue
                    idx = event_types.index(etype)
                    count_dict[etype] += 1
                    total += 1
                    hour = t.hour if hasattr(t, 'hour') else int(str(t)[11:13])
                    slot = f"{str((hour//2)*2).zfill(2)}-{str(((hour//2)*2)+2).zfill(2)}"
                    if slot in slot_dict:
                        slot_dict[slot][idx] += 1
                # 비율 계산
                ratio = [round((count_dict[etype]/total)*100) if total else 0 for etype in event_types]
            else:
                # 미래 월인 경우 모든 값을 0으로 설정
                total = 0
                ratio = [0 for _ in event_types]
            
            # time_distribution dict
            time_distribution = {slot: slot_dict[slot] for slot in time_slots}
            result["monthly_stats"].append({
                "month": ym,
                "count": [count_dict[etype] for etype in event_types],
                "ratio": ratio,
                "time_distribution": time_distribution
            })
        return result
    finally:
        cursor.close()
        conn.close() 