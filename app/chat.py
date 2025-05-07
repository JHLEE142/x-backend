## backend/app/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/save")
def save_chat(user_id: int, content: str, db: Session = Depends(get_db)):
    chat = models.Chat(user_id=user_id, content=content, timestamp=datetime.utcnow())
    db.add(chat)

    # 사용자 실시간 정보 업데이트
    user = db.query(models.User).get(user_id)
    estimated_token_usage = len(content.split())  # 단순 추정 (단어 수 기반)
    user.total_tokens_used += estimated_token_usage
    user.requests_processed += 1
    user.last_active = datetime.utcnow()
    user.credit_usage = min(int(user.total_tokens_used / 1000), 100)  # 예시: 1000 토큰당 1% 차감

    db.commit()
    return {"message": "Chat saved", "tokens_used": estimated_token_usage}

@router.get("/history")
def get_history(user_id: int, db: Session = Depends(get_db)):
    chats = db.query(models.Chat).filter(models.Chat.user_id == user_id).all()
    return chats