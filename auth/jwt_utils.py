# backend/auth/jwt_utils.py

import os
from jose import jwt, JWTError
from typing import Optional
from datetime import datetime, timedelta

# 비밀키 및 설정
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일 유효

# ✅ JWT 생성
def create_jwt_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ✅ JWT 검증 및 디코딩
def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ✅ 사용자 ID 추출 (토큰에서 sub 읽기)
def get_user_id_from_token(token: str) -> Optional[str]:
    payload = verify_jwt_token(token)
    if payload:
        return payload.get("sub")
    return None
