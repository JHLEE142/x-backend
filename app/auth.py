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
    hashed_pw = pwd_context.hash(data.password)
    user = models.User(
        email=data.email,
        hashed_password=hashed_pw,
        nickname="NewUser",
        selected_model="GPT-4",
        plan="Pro",
        total_tokens_used=0,
        credit_usage=0,
        requests_processed=0,
        weekly_stat=0.0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created"}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#@router.post("/login")
#def login(data: LoginInput, db: Session = Depends(get_db)):
#    user = db.query(models.User).filter(models.User.email == data.email).first()
#    if not user or not pwd_context.verify(data.password, user.hashed_password):
#        raise HTTPException(status_code=401, detail="Invalid credentials")
#    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm=ALGORITHM)
#    return {"token": token}

@router.post("/login")
def login(login_data: dict, db: Session = Depends(SessionLocal)):
    print("📩 로그인 시도:", login_data["email"])
    user = db.query(User).filter(User.email == login_data["email"]).first()

    if not user:
        print("❌ 사용자 없음")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    print("🔐 비밀번호 검증 시작")
    if not verify_password(login_data["password"], user.hashed_password):
        print("❌ 비밀번호 불일치")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    print("✅ 로그인 성공")
    return {"message": "Login successful", "user_id": user.id}