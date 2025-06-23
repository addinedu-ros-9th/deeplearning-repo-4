def verify_user(user_id):
    """사용자 ID를 확인하고 인증합니다."""
    # TODO: DB에서 사용자 정보 확인
    print(f"AuthService: Verifying {user_id}")
    if user_id == "user01":
        return True
    return False 