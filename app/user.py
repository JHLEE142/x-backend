# backend/app/user.py

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from db.models import User
from jose import jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")

def get_current_user_id(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
def get_user_info(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.nickname,
        "provider": user.provider,
        "created_at": user.created_at,
        "plan": user.plan,
        "credit_usage": user.credit_usage,
        "total_tokens_used": user.total_tokens_used,
        "requests_processed": user.requests_processed,
        "weekly_stat": user.weekly_stat,
        "last_active": user.last_active
    }
