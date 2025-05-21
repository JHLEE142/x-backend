# backend/auth/oauth.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from jose import jwt
import os
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.jwt_utils import create_jwt_token

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

# ✅ 로그인 시작: Google/GitHub 공통
@router.get("/auth/{provider}/login")
async def oauth_login(request: Request, provider: str):
    redirect_uri = request.url_for("oauth_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

# ✅ 콜백 처리
@router.get("/auth/callback/{provider}", name="oauth_callback", response_class=HTMLResponse)
async def auth_callback(request: Request, provider: str, db: Session = Depends(get_db)):
    oauth_client = oauth.create_client(provider)
    token = await oauth_client.authorize_access_token(request)

    if provider == "google":
        userinfo = await oauth_client.parse_id_token(request, token)
        email = userinfo["email"]
        name = userinfo["name"]
        uid = userinfo["sub"]
    else:
        resp = await oauth_client.get("user", token=token)
        profile = resp.json()
        email = profile.get("email") or f'{profile["login"]}@github.com'
        name = profile["login"]
        uid = str(profile["id"])

    # ✅ 유저 존재 여부 확인
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password="social-login",
            nickname=name,
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

    # ✅ JWT 발급
    jwt_token = create_jwt_token({
        "id": str(user.id),
        "email": user.email,
        "name": user.nickname,
        "plan": user.plan,
        "credit_usage": user.credit_usage
    })

    # ✅ 프론트로 전달 (팝업 → 부모 창 postMessage)
    return f"""
    <script>
      window.opener.postMessage({{
        token: "{jwt_token}",
        user: {{
          id: "{user.id}",
          name: "{user.nickname}",
          email: "{user.email}",
          plan: "{user.plan}",
          credit_usage: {user.credit_usage}
        }}
      }}, "*");
      window.close();
    </script>
    """
