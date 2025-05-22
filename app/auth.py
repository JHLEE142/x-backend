# backend/app/auth.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from db import models
from db.models import User
from passlib.context import CryptContext
from pydantic import BaseModel
from auth.jwt_utils import create_jwt_token
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")

class LoginInput(BaseModel):
    email: str
    password: str

class SignupInput(BaseModel):
    email: str
    password: str
    nickname: str

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(data: SignupInput, db: Session = Depends(get_db)):
    try:
        hashed_pw = pwd_context.hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed_pw,
            nickname=data.nickname,
            selected_model="gpt-3.5",
            plan="basic",
            total_tokens_used=0,
            credit_usage=100,
            requests_processed=0,
            weekly_stat=0.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User created"}
    except Exception as e:
        print("❌ Signup failed", str(e))
        raise HTTPException(status_code=500, detail="Signup failed")

@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token({
        "id": str(user.id),
        "email": user.email,
        "name": user.nickname,
        "plan": user.plan,
        "credit_usage": user.credit_usage
    })

    return {
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.nickname,
            "plan": user.plan,
            "credit_usage": user.credit_usage
        }
    }

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = token.replace("Bearer ", "")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
        "plan": user.plan,
        "credit_usage": user.credit_usage
    }
