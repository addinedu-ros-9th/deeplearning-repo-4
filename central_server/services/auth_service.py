from central_server.database.db import get_connection

def login_user(user_id, password):
    """사용자 ID와 비밀번호를 데이터베이스에서 확인하고 인증합니다."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. 아이디 존재 여부 확인
        query_id = "SELECT user_id, password FROM users WHERE user_id = %s"
        cursor.execute(query_id, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"AuthService: User '{user_id}' not found.")
            return {"status": "error", "message": "Invalid user_id"}, 401
        
        # 2. 비밀번호 일치 여부 확인
        if user['password'] != password:
            print(f"AuthService: User '{user_id}' password mismatch.")
            return {"status": "error", "message": "Invalid password"}, 402

        print(f"AuthService: User '{user_id}' authenticated successfully.")
        return {"status": "success", "message": "Login successful"}, 200

    except Exception as e:
        print(f"AuthService: Database error - {e}")
        return {"status": "error", "message": "Server error"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 