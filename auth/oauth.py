# backend/auth/oauth.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from jose import jwt
import os
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

router = APIRouter()

oauth = OAuth()

# ✅ Google OAuth 등록
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ✅ GitHub OAuth 등록
oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# ✅ 공통 로그인 시작
@router.get("/auth/{provider}/login")
async def oauth_login(request: Request, provider: str):
    redirect_uri = request.url_for("oauth_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

# ✅ 공통 콜백 처리
@router.get("/auth/{provider}/callback")
async def oauth_callback(request: Request, provider: str, db: Session = Depends(get_db)):
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    if provider == "google":
        user_info = await client.parse_id_token(request, token)
        email = user_info.get("email")
        name = user_info.get("name")

    elif provider == "github":
        resp = await client.get("user", token=token)
        user_info = resp.json()
        email = user_info.get("email")
        name = user_info.get("name")

        # GitHub의 경우 이메일이 null일 수 있어 별도 요청
        if not email:
            emails_resp = await client.get("user/emails", token=token)
            emails = emails_resp.json()
            primary_email = next((e["email"] for e in emails if e["primary"] and e["verified"]), None)
            email = primary_email

    else:
        return {"error": "Unsupported provider"}

    if not email:
        return {"error": "Email not found from provider"}

    # ✅ 사용자 DB 저장 또는 조회
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, provider=provider)
        db.add(user)
        db.commit()
        db.refresh(user)

    # ✅ JWT 발급
    encoded_token = jwt.encode(
        {"sub": str(user.id)},
        os.getenv("SECRET_KEY", "mysecret"),
        algorithm="HS256"
    )

    frontend_url = f"https://www.aistudio-comet.world/login?token={encoded_token}"
    return RedirectResponse(url=frontend_url)
