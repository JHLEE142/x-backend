## backend/main.py
from fastapi import FastAPI
from app import auth, user, chat, template
from database import create_tables

app = FastAPI()

# 라우터 등록
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