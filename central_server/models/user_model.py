# from database.db import Base  # db.py에 Base = declarative_base()가 있다고 가정
# from sqlalchemy import Column, Integer, String

# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(String(50), unique=True, nullable=False)
#     name = Column(String(50))
#     email = Column(String(120), unique=True)
#     store_name = Column(String(100))

#     def __repr__(self):
#         return f'<User {self.name}>'

# 주석 처리된 예시입니다. ORM에 맞게 활성화하여 사용하세요.
pass 