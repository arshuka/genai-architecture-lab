from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import uuid
import sqlite3

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")
AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://localhost:8000")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise RuntimeError("Missing Google OAuth environment variables")

# -------------------------------------------------
# APP
# -------------------------------------------------
app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="genai-architecture-lab-secret"
)

# -------------------------------------------------
# OAUTH SETUP
# -------------------------------------------------
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
def get_conn():
    return sqlite3.connect("users.db", check_same_thread=False)

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = f"{AUTH_BACKEND_URL}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]

    email = user["email"]
    user_id = str(uuid.uuid4())

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (id, email, auth_provider) VALUES (?, ?, 'google')",
        (user_id, email)
    )
    conn.commit()
    conn.close()

    return RedirectResponse(f"{STREAMLIT_URL}/?user_id={user_id}")
