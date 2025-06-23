from database.db import get_connection

def verify_user(user_id):
    """사용자 ID를 데이터베이스에서 확인하고 인증"""
    
    db_conn = None
    cursor = None
    try:
        db_conn = get_connection()
        cursor = db_conn.cursor()
        
        # users 테이블에서 user_id가 존재하는지 확인
        query = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user:
            print(f"AuthService: User '{user_id}' found in DB.")
            return True
        else:
            print(f"AuthService: User '{user_id}' not found in DB.")
            return False

    except Exception as e:
        print(f"AuthService: Database error - {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close() 