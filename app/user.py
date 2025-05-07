## backend/app/user.py
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
import os

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = db.query(models.User).get(user_id)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
def read_users_me(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "selected_model": user.selected_model,
        "plan": user.plan,
        "total_tokens_used": user.total_tokens_used,
        "credit_usage": user.credit_usage,
        "last_active": user.last_active,
        "requests_processed": user.requests_processed,
        "weekly_stat": user.weekly_stat
    }

