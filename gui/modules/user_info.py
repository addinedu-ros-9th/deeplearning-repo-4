import pymysql

# MySQL 연결 정보
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='0000',
    db='GigachadDb',
    port=3306,
    charset='utf8'
)

user_info = []

def check_user_exixts(user_id):
    """
    주어진 user_id가 user에 존재하는지 확인합니다.
    :param user_id: 확인할 사용자 ID
    :return: 존재하면 True, 아니면 False
    """
    with conn.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] > 0
    
def check_user_password(user_id, password):
    """
    주어진 user_id와 password가 일치하는지 확인합니다.
    :param user_id: 사용자 ID
    :param password: 비밀번호
    :return: 일치하면 True, 아니면 False
    """
    with conn.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM user WHERE user_id = %s AND password = %s"
        cursor.execute(sql, (user_id, password))
        result = cursor.fetchone()
        return result[0] > 0
    
def get_user_info(user_id):
    """
    주어진 user_id에 대한 사용자 정보를 반환합니다.
    :param user_id: 사용자 ID
    :return: 사용자 정보 리스트 [user_id, email] 또는 None
    """
    with conn.cursor() as cursor:
        sql = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        print(list(result))
        if result:
            return list(result)
        else:
            return None
        

def set_user_info(id, pw):
    global user_info 
    user_info= [id, pw]
    return user_info