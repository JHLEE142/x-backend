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
@@router.get("/auth/callback/{provider}", response_class=HTMLResponse)
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
         email = profile.get("email", f'{profile["login"]}@github.com')
         name = profile["login"]
         uid = str(profile["id"])

     # ✅ 기존 유저 확인 또는 신규 생성
     user = db.query(models.User).filter(models.User.email == email).first()
     if not user:
         user = models.User(
             email=email,
             hashed_password="social-login",  # 소셜 로그인은 패스워드 없음
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

     # ✅ 클라이언트에 token + user 전달
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
