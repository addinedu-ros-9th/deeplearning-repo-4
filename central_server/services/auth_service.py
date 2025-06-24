from central_server.database.db import get_connection

def login_user(user_id, password):
    """사용자 ID와 비밀번호를 데이터베이스에서 확인하고 인증합니다."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        id_query = "SELECT user_id FROM user WHERE user_id = %s"
        cursor.execute(id_query, (user_id,))
        user_exists = cursor.fetchone()
        if not user_exists:
            print(f"AuthService: User '{user_id}' does not exist.")
            return {"status": "error", "message": "User does not exist"}, 401
        
        query = "SELECT user_id FROM user WHERE user_id = %s AND password = %s"
        cursor.execute(query, (user_id, password))
        user = cursor.fetchone()
        
        if user:
            print(f"AuthService: User '{user_id}' authenticated successfully.")
            return {"status": "success", "message": "Login successful"}, 200
        else:
            print(f"AuthService: User '{user_id}' authentication failed.")
            return {"status": "error", "message": "Invalid credentials"}, 402

    except Exception as e:
        print(f"AuthService: Database error - {e}")
        return {"status": "error", "message": "Server error"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 