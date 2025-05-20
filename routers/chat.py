## backend/app/chat.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from db.models import Chat, User  # 모델 경로 명확히 지정
from jose import jwt
from datetime import datetime
import os

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")

class ChatSavePayload(BaseModel):
    prompt: str
    response: str
    title: str = "Untitled"

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

def get_current_user_id(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = token.replace("Bearer ", "")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return int(payload.get("sub"))

@router.post("/chat/save")
def save_chat(payload: ChatSavePayload, request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)

    estimated_token_usage = len(payload.response.split())  # 단어 수 기반 토큰 추정

    chat = Chat(
        user_id=user_id,
        prompt=payload.prompt,
        response=payload.response,
        title=payload.title,
        token_usage=estimated_token_usage,
    )
    db.add(chat)

    # 사용자 정보 업데이트
    user = db.query(User).get(user_id)
    user.total_tokens_used += estimated_token_usage
    user.requests_processed += 1
    user.last_active = datetime.utcnow()
    user.credit_usage = max(user.credit_usage - 10, 0)  # 코인 차감

    db.commit()
    return {"message": "Chat saved", "tokens_used": estimated_token_usage}


@router.get("/chat/user")
def get_user_chats(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()
    return [
        {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "tokens": chat.token_usage,
        }
        for chat in chats
    ]
