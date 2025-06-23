def get_stats_data(user_id, date):
    """요청된 월의 통계 데이터를 생성하여 반환합니다."""
    # TODO: DB에서 해당 사용자와 날짜에 맞는 통계 데이터 집계
    print(f"DashboardService: Getting stats for {user_id} on {date}")
    return {"message": "Stats data"} 