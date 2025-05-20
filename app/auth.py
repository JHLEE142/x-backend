# backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
from passlib.context import CryptContext
from pydantic import BaseModel
from auth.jwt_utils import create_jwt_token

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
        user = models.User(
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
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ JWT 발급
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
