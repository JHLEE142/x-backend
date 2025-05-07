## backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
from passlib.context import CryptContext
from jose import jwt
import os

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
def signup(email: str, password: str, db: Session = Depends(get_db)):
    hashed_pw = pwd_context.hash(password)
    user = models.User(
        email=email,
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

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token}