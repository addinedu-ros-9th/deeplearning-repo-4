from central_server.database.db import get_connection


def get_user_private_info(user_id):
    """user_id로 특정 사용자의 이름, 이메일, 지점명을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # users 테이블과 store 테이블을 JOIN하여 사용자 정보와 매장명을 함께 조회
        query = """
            SELECT u.name, u.email, s.store_name
            FROM users u
            JOIN store s ON u.user_id = s.user_id
            WHERE u.user_id = %s
        """
        cursor.execute(query, (user_id,))
        user_info = cursor.fetchone()
        return user_info
    finally:
        cursor.close()
        conn.close()