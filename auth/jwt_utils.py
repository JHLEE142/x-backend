# backend/auth/jwt_utils.py
import os
from jose import jwt, JWTError
from typing import Optional, Dict
from datetime import datetime, timedelta

# 비밀키 및 설정
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일 유효

# ✅ JWT 생성 (user 전체 정보 포함 가능)
def create_jwt_token(user: Dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user["id"]),
        "email": user.get("email"),
        "name": user.get("name", user.get("nickname")),
        "plan": user.get("plan"),
        "credit_usage": user.get("credit_usage"),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ✅ JWT 검증
def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ✅ 사용자 ID 추출
def get_user_id_from_token(token: str) -> Optional[str]:
    payload = verify_jwt_token(token)
    if payload:
        return payload.get("sub")
    return None
