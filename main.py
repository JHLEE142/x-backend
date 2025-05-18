## backend/main.py
from fastapi import FastAPI
from app import auth, user, chat, template
from database import create_tables
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # ✅ 개발 환경
        "https://fastapi-backend-p5j9.onrender.com",  # ✅ 자기 자신도 포함
        "https://www.aistudio-comet.world",  # 프론트엔드 도메인
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ✅ 여기에 디버깅용 라우트 추가
@app.get("/debug-db-url")
def debug_db_url():
    return {"DATABASE_URL": os.getenv("DATABASE_URL")}