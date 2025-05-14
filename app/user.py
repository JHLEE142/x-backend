## backend/app/user.py
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
import os

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"

# DB 연결 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT 토큰으로 사용자 조회
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token error: {str(e)}")

# 로그인된 사용자 정보 반환
@router.get("/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "selected_model": current_user.selected_model,
        "plan": current_user.plan,
        "total_tokens_used": current_user.total_tokens_used,
        "credit_usage": current_user.credit_usage,
        "last_active": current_user.last_active,
        "requests_processed": current_user.requests_processed,
        "weekly_stat": current_user.weekly_stat,
    }
