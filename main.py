# backend/main.py

from fastapi import FastAPI
from app import auth, user, chat, template
from database import create_tables
from fastapi.middleware.cors import CORSMiddleware
from auth.oauth import router as oauth_router
import os

app = FastAPI()  # ✅ 먼저 선언해야 이후 라우터 등록이 유효해짐

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://fastapi-backend-p5j9.onrender.com",
        "https://www.aistudio-comet.world",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 등록 순서
app.include_router(oauth_router, prefix="/auth")
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(chat.router, prefix="/chat")
app.include_router(template.router, prefix="/template")

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
def root():
    return {"message": "FastAPI backend for x-project is running"}

@app.get("/debug-db-url")
def debug_db_url():
    return {"DATABASE_URL": os.getenv("DATABASE_URL")}