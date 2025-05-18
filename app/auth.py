## backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
from passlib.context import CryptContext
from jose import jwt
import os
from pydantic import BaseModel

class LoginInput(BaseModel):
    email: str
    password: str

class SignupInput(BaseModel):
    email: str
    password: str
    nickname: str

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
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
        user = models.User(
            email=data.email,
            hashed_password=hashed_pw,
            nickname=data.nickname,
            selected_model="",
            plan="",
            total_tokens_used=0,
            credit_usage=0,
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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    print("🔐 Login attempt:", data.email)

    try:
        user = db.query(models.User).filter(models.User.email == data.email).first()

        if not user:
            print("❌ User not found:", data.email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not pwd_context.verify(data.password, user.hashed_password):
            print("❌ Incorrect password for:", data.email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm=ALGORITHM)
        print("✅ Login successful:", user.email)
        return {"token": token}

    except Exception as e:
        print("🚨 Exception during login:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
