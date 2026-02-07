import streamlit as st
from pathlib import Path
import base64
import uuid
import time
import sqlite3

from menu_config import MENU_TREE

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")

# -------------------------------------------------
# REMOVE STREAMLIT TOP GAP
# -------------------------------------------------
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

# anon id (only if not logged in)
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
    cur.execute("SELECT view_count FROM usage WHERE anon_id = ?", (anon_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def inc_anon(anon_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usage (anon_id, view_count)
        VALUES (?, 1)
        ON CONFLICT(anon_id)
        DO UPDATE SET view_count = view_count + 1
    """, (anon_id,))
    conn.commit()
    conn.close()

def get_user_count(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT view_count FROM user_usage WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def inc_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_usage (user_id, view_count)
        VALUES (?, 1)
        ON CONFLICT(user_id)
        DO UPDATE SET view_count = view_count + 1
    """, (user_id,))
    conn.commit()
    conn.close()

def merge_anon_to_user(anon_id, user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT view_count FROM usage WHERE anon_id = ?", (anon_id,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            INSERT INTO user_usage (user_id, view_count)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET view_count = view_count + ?
        """, (user_id, row[0], row[0]))
        cur.execute("DELETE FROM usage WHERE anon_id = ?", (anon_id,))
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
# MERGE ON LOGIN (ONE TIME)
# -------------------------------------------------
if st.session_state.get("logged_in") and "anon_id" in st.session_state:
    merge_anon_to_user(st.session_state.anon_id, st.session_state.user_id)
    del st.session_state.anon_id

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
CONTENT_DIR = BASE_DIR / "content"

# -------------------------------------------------
# LOGOUT FEEDBACK MESSAGE
# -------------------------------------------------
if st.session_state.get("just_logged_out"):
    st.success("✅ You have been logged out. You are now browsing as a guest.")
    st.info("You can explore up to 5 architectures for free. Login anytime to continue.")
    del st.session_state["just_logged_out"]

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("## 🧠 GenAI Architecture Lab")

# -------------------------------------------------
# SIDEBAR ACCOUNT (EMAIL + LOGOUT)
# -------------------------------------------------
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

# -------------------------------------------------
# TOP MENU
# -------------------------------------------------
if "tab" not in st.session_state:
    st.session_state.tab = "GenAI"

c1, c2, c3, c4, c5, _ = st.columns([1, 1, 1, 1, 1, 5])

with c1:
    if st.button("🏠 Welcome"):
        st.session_state.tab = "Welcome"
with c2:
    if st.button("🧠 GenAI"):
        st.session_state.tab = "GenAI"
with c3:
    if st.button("🛡️ AI Quick Guide"):
        st.session_state.tab = "AI Quick Guide"
with c4:
    if st.button("🛡️ Cloud AI"):
        st.session_state.tab = "Cloud AI"

# ADMIN BUTTON (ONLY FOR YOU)
if st.session_state.get("logged_in"):
    email = get_user_email(st.session_state.user_id)
    if email == "arshuka@gmail.com":
        with c5:
           if st.button("🛠 Admin"):
                st.query_params["user_id"] = st.session_state.user_id
                st.switch_page("pages/Admin.py")

st.divider()

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
ICON_MAP = {
    "GenAI": "🧠",
    "LLM": "🤖",
    "RAG": "📚",
    "AI Quick Guide": "🛡",
    "Welcome": "🏠",
    "Cloud AI": "🛡️",
    "Admin": "🛡️"
}

tab = st.session_state.tab
st.sidebar.header(f"{ICON_MAP.get(tab,'📁')} {tab}")
sections = list(MENU_TREE[tab].keys())
section = st.sidebar.selectbox("Category", sections)
topics = list(MENU_TREE[tab][section].keys())
topic = st.sidebar.radio("Select Topic", topics)

# -------------------------------------------------
# CLICK TRACKING
# -------------------------------------------------
if st.session_state.logged_in:
    current_count = get_user_count(st.session_state.user_id)
else:
    current_count = get_anon_count(st.session_state.anon_id)

if st.session_state.last_topic is None:
    st.session_state.last_topic = topic
elif topic != st.session_state.last_topic:
    if st.session_state.logged_in:
        inc_user(st.session_state.user_id)
    else:
        inc_anon(st.session_state.anon_id)
    st.session_state.last_topic = topic
    current_count += 1

FREE_LIMIT = 5

# -------------------------------------------------
# LOGIN GATE
# -------------------------------------------------
def show_login_modal():
    st.warning("🔒 Free limit reached. Login to continue.")
    st.link_button(
        "Continue with Google",
        "http://localhost:8000/auth/google"
    )

if current_count >= FREE_LIMIT and not st.session_state.logged_in:
    show_login_modal()
    st.stop()

# -------------------------------------------------
# CONTENT RENDERING
# -------------------------------------------------
content = MENU_TREE[tab][section][topic]
col_img, col_text = st.columns([3, 2])

def render_image(image_name: str):
    img_path = IMG_DIR / image_name
    img_bytes = img_path.read_bytes()
    img_base64 = base64.b64encode(img_bytes).decode()
    uid = str(uuid.uuid4())
    st.markdown(
        f"""
        <style>
        .img-{uid} {{
            width:100%;
            border-radius:12px;
            filter:blur(16px);
            animation:unblur-{uid} 1s forwards;
        }}
        @keyframes unblur-{uid} {{
            to {{ filter:blur(0); }}
        }}
        </style>
        <img src="data:image/png;base64,{img_base64}" class="img-{uid}">
        """,
        unsafe_allow_html=True
    )

with col_img:
    st.subheader("Diagram")
    tg, ta = st.tabs(["🖼️ Generate", "🎞️ Animate"])
    with tg:
        if content.get("image"):
            render_image(content["image"])
    with ta:
        if content.get("image_anim"):
            render_image(content["image_anim"])

def type_md(txt, speed=0.004):
    p = st.empty()
    s = ""
    for c in txt:
        s += c
        p.markdown(s)
        time.sleep(speed)

with col_text:
    st.subheader("Details")
    te, tt = st.tabs(["📘 Summary", "⚖️ Trade-offs"])
    with te:
        if content.get("text_md"):
            type_md((CONTENT_DIR / content["text_md"]).read_text())
    with tt:
        if content.get("trade_md"):
            type_md((CONTENT_DIR / content["trade_md"]).read_text())
