## backend/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
     __tablename__ = "users"

     id = Column(Integer, primary_key=True, index=True)
     email = Column(String, unique=True, index=True)
     hashed_password = Column(String)
     plan = Column(String, nullable=True, default="")

     # 🔽 추가 필드들
     nickname = Column(String, default="NewUser")
     selected_model = Column(String, nullable=True, default="")
     total_tokens_used = Column(Integer, default=0)
     credit_usage = Column(Integer, default=0)
     requests_processed = Column(Integer, default=0)
     weekly_stat = Column(Float, default=0.0)

     chats = relationship("Chat", back_populates="owner")
     templates = relationship("Template", back_populates="owner")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="chats")

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    content = Column(Text)

    owner = relationship("User", back_populates="templates")