import streamlit as st
from pathlib import Path
import base64
import uuid
import time
import sqlite3
from dotenv import load_dotenv
import os

from menu_config import MENU_TREE

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()
AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://localhost:8000")

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        .block-container { padding-top: 0.8rem !important; }
        header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DB_PATH = Path("users.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT,
            auth_provider TEXT,
            plan TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            anon_id TEXT PRIMARY KEY,
            view_count INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_usage (
            user_id TEXT PRIMARY KEY,
            view_count INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

init_tables()

# -------------------------------------------------
# AUTH / IDENTITY
# -------------------------------------------------
if "user_id" in st.query_params:
    st.session_state.logged_in = True
    st.session_state.user_id = st.query_params["user_id"]
else:
    st.session_state.logged_in = False

if not st.session_state.get("logged_in"):
    if "anon_id" in st.query_params:
        anon_id = st.query_params["anon_id"]
    else:
        anon_id = str(uuid.uuid4())
        st.query_params["anon_id"] = anon_id
    st.session_state.anon_id = anon_id

if "last_topic" not in st.session_state:
    st.session_state.last_topic = None

# -------------------------------------------------
# USAGE HELPERS
# -------------------------------------------------
def get_anon_count(anon_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT view_count FROM usage WHERE anon_id=?", (anon_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def inc_anon(anon_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usage (anon_id, view_count)
        VALUES (?,1)
        ON CONFLICT(anon_id)
        DO UPDATE SET view_count=view_count+1
    """, (anon_id,))
    conn.commit()
    conn.close()

def get_user_count(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT view_count FROM user_usage WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def inc_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_usage (user_id, view_count)
        VALUES (?,1)
        ON CONFLICT(user_id)
        DO UPDATE SET view_count=view_count+1
    """, (user_id,))
    conn.commit()
    conn.close()

def get_user_email(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# -------------------------------------------------
# MERGE ON LOGIN
# -------------------------------------------------
if st.session_state.get("logged_in") and "anon_id" in st.session_state:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT view_count FROM usage WHERE anon_id=?", (st.session_state.anon_id,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            INSERT INTO user_usage (user_id, view_count)
            VALUES (?,?)
            ON CONFLICT(user_id)
            DO UPDATE SET view_count=view_count+?
        """, (st.session_state.user_id, row[0], row[0]))
        cur.execute("DELETE FROM usage WHERE anon_id=?", (st.session_state.anon_id,))
    conn.commit()
    conn.close()
    del st.session_state.anon_id

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("## 🧠 GenAI Architecture Lab")

# -------------------------------------------------
# MENU
# -------------------------------------------------
if "tab" not in st.session_state:
    st.session_state.tab = "GenAI"

c1, c2, c3, c4, c5, _ = st.columns([1,1,1,1,1,5])
if c1.button("🏠 Welcome"): st.session_state.tab = "Welcome"
if c2.button("🧠 GenAI"): st.session_state.tab = "GenAI"
if c3.button("🛡️ AI Quick Guide"): st.session_state.tab = "AI Quick Guide"
if c4.button("🛡️ Cloud AI"): st.session_state.tab = "Cloud AI"
# ADMIN BUTTON (ONLY FOR YOU)
if st.session_state.get("logged_in"):
    email = get_user_email(st.session_state.user_id)
    if email == "arshuka@gmail.com":
        with c5:
            if st.button("🛠 Admin"):
                st.query_params["user_id"] = st.session_state.user_id
                st.switch_page("pages/Admin.py")

st.divider()

ICON_MAP = {
    "GenAI": "🧠",
    "LLM": "🤖",
    "RAG": "📚",
    "AI Quick Guide": "🛡",
    "Welcome": "🏠",
    "Cloud AI": "🛡️",
    "Admin": "🛠"
}
# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
if st.session_state.get("just_logged_out"):
    st.success("✅ You have been logged out. You are now browsing as a guest.")
    st.info("You can explore up to 5 architectures for free. Login anytime to continue.")
    del st.session_state["just_logged_out"]

# -------------------------------------------------
# SIDEBAR ACCOUNT (EMAIL + LOGOUT)
# -------------------------------------------------
def get_user_email(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

if st.session_state.get("logged_in"):
    st.sidebar.markdown("### 👤 Account")

    email = get_user_email(st.session_state.user_id)
    if email:
        st.sidebar.caption(email)

    if st.sidebar.button("🚪 Logout"):
        st.session_state["just_logged_out"] = True
        st.session_state["tab"] = "Welcome"
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()



tab = st.session_state.tab
st.sidebar.header(tab)

sections = list(MENU_TREE[tab].keys())
section = st.sidebar.selectbox("Category", sections)
topics = list(MENU_TREE[tab][section].keys())
topic = st.sidebar.radio("Topic", topics)

# -------------------------------------------------
# CLICK TRACKING
# -------------------------------------------------
current_count = (
    get_user_count(st.session_state.user_id)
    if st.session_state.logged_in
    else get_anon_count(st.session_state.anon_id)
)

if st.session_state.last_topic != topic:
    if st.session_state.last_topic is not None:
        if st.session_state.logged_in:
            inc_user(st.session_state.user_id)
        else:
            inc_anon(st.session_state.anon_id)
        current_count += 1
    st.session_state.last_topic = topic

FREE_LIMIT = 5

# -------------------------------------------------
# LOGIN GATE
# -------------------------------------------------
if current_count >= FREE_LIMIT and not st.session_state.logged_in:
    st.warning("🔒 Free limit reached. Login to continue.")
    st.link_button(
        "Continue with Google",
        f"{AUTH_BACKEND_URL}/auth/google"
    )
    st.stop()

# -------------------------------------------------
# CONTENT
# -------------------------------------------------
content = MENU_TREE[tab][section][topic]
col_img, col_text = st.columns([3,2])

def render_image(image):
    img = (Path("images") / image).read_bytes()
    b64 = base64.b64encode(img).decode()
    st.markdown(f'<img src="data:image/png;base64,{b64}" width="100%">', unsafe_allow_html=True)

with col_img:
    if content.get("image"):
        render_image(content["image"])

with col_text:
    if content.get("text_md"):
        st.markdown((Path("content") / content["text_md"]).read_text())
