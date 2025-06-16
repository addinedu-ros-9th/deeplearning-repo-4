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

user_table = []

try:
    with conn.cursor() as cursor:
        sql = "SELECT * FROM user"
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]  # 컬럼명 추출
        user_table = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print(user_table)
finally:
    conn.close()