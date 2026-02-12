from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import uuid
from supabase import create_client
from datetime import datetime

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("---- DEBUG ----")
print("DEV_MODE:", os.getenv("DEV_MODE"))

def get_streamlit_url():
    dev_mode = os.getenv("DEV_MODE", "").lower()

    if dev_mode == "true":
        return "http://localhost:8501"

    return "https://genai-architecture-lab.streamlit.app"


STREAMLIT_URL = get_streamlit_url()

print("Final Redirect URL:", STREAMLIT_URL)
print("----------------")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="genai-auth-secret")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@app.get("/auth/google")
async def login(request: Request):
    redirect_uri = f"{request.base_url}auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]

    email = user["email"]
    name = user.get("name", "")

    res = supabase.table("users").select("*").eq("email", email).execute()

    now = datetime.utcnow().isoformat()

    # Extract metadata
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if res.data:
        user_id = res.data[0]["id"]

        # Update last login
        supabase.table("users").update({
            "last_login": now
        }).eq("id", user_id).execute()

    else:
        user_id = str(uuid.uuid4())
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "name": name,
            "role": "admin" if email == "arshuka@gmail.com" else "user",
            "created_at": now,
            "last_login": now
        }).execute()

    # ✅ INSERT LOGIN HISTORY (EVERY LOGIN)
    supabase.table("user_history").insert({
        "user_id": user_id,
        "email": email,
        "login_at": now,
        "provider": "google",
        "ip_address": ip_address,
        "user_agent": user_agent
    }).execute()


    return RedirectResponse(f"{STREAMLIT_URL}/?user_id={user_id}")
