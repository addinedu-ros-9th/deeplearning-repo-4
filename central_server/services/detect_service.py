def get_weekly_logs(user_id):
    """일주일치 감지 로그를 반환합니다."""
    # TODO: DB에서 user_id에 해당하는 일주일치 로그 조회
    print(f"DetectService: Getting weekly logs for {user_id}")
    return {"message": "Weekly logs"}

def get_filtered_logs(filters):
    """필터 조건에 맞는 감지 로그를 반환합니다."""
    # TODO: DB에서 필터 조건에 맞는 로그 조회
    print(f"DetectService: Getting filtered logs with {filters}")
    return [{"message": "Filtered logs"}] 