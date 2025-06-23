# from database.db import Base
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship

# class Video(Base):
#     __tablename__ = 'videos'
#     id = Column(Integer, primary_key=True)
#     video_url = Column(String(200), unique=True, nullable=False)
#     event_id = Column(Integer, ForeignKey('events.id'))
    
#     event = relationship("Event")

#     def __repr__(self):
#         return f'<Video {self.video_url}>'

pass 