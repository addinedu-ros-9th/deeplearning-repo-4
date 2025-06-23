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

user = ''
user_info = []

def check_user_id(user_id):
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
    
def check_user_pw(user_id, password):
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
    
def set_user(user_id):
    with conn.cursor() as cursor:
        sql = "SELECT user_id FROM user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        print(result)
        global user
        user = str(result)

def set_user_info(user_id):
    # ['user01', 'user01', '최기가', 'user01@email.com', datetime.datetime(2025, 6, 16, 17, 0)]

    with conn.cursor() as cursor:
        sql = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        global user_info
        if result is not None:
            print(list(result))
            user_info = list(result)
        else:
            print("No user found with the given user_id.")
            user_info = []
        
def get_user():
    print(f"사용자 : {user}")
    return user

def get_user_info():
    print(f"유저 정보 : {user_info}")
    return user_info

def reset_user():
    user = ''
    user_info = []