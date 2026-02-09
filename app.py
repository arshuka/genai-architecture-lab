import streamlit as st
from pathlib import Path
import base64, uuid, time
from supabase import create_client
from menu_config import MENU_TREE

import os
from dotenv import load_dotenv

load_dotenv()


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 0.8rem; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SUPABASE
# -------------------------------------------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_SERVICE_KEY"]
)

# -------------------------------------------------
# AUTH STATE
# -------------------------------------------------
if "user_id" in st.query_params:
    st.session_state.logged_in = True
    st.session_state.user_id = st.query_params["user_id"]
else:
    st.session_state.logged_in = False

if not st.session_state.get("logged_in"):
    if "anon_id" not in st.session_state:
        st.session_state.anon_id = str(uuid.uuid4())

# -------------------------------------------------
# USAGE HELPERS
# -------------------------------------------------
def get_usage(col, key):
    r = supabase.table("usage").select("count").eq(col, key).execute()
    return r.data[0]["count"] if r.data else 0

def inc_usage(col, key):
    supabase.rpc("increment_usage", {"col_name": col, "key_val": key}).execute()

# -------------------------------------------------
# HEADER
# -------------------------------------------------
import os
st.markdown("## 🧠 GenAI Architecture Lab")
st.markdown("## helow Testing")

st.write("Testing")
st.write("OpenAI key loaded:", bool(os.getenv("OPENAI_API_KEY")))
st.markdown("OpenAI key loaded:", bool(os.getenv("OPENAI_API_KEY")))

# -------------------------------------------------
# ACCOUNT
# -------------------------------------------------
if st.session_state.get("logged_in"):
    user = supabase.table("users").select("*").eq("id", st.session_state.user_id).execute().data[0]
    st.sidebar.caption(user["email"])

    if st.sidebar.button("🚪 Logout"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

# -------------------------------------------------
# TOP MENU
# -------------------------------------------------
if "tab" not in st.session_state:
    st.session_state.tab = "GenAI"

c1, c2, c3, c4, c5, _ = st.columns([1,1,1,1,1,4])

if c1.button("🏠 Welcome"): st.session_state.tab = "Welcome"
if c2.button("🧠 GenAI"): st.session_state.tab = "GenAI"
if c3.button("🛡 AI Quick Guide"): st.session_state.tab = "AI Quick Guide"
if c4.button("☁️ Cloud AI"): st.session_state.tab = "Cloud AI"

if st.session_state.get("logged_in") and user["email"] == "arshuka@gmail.com":
    if c5.button("🛠 Admin"):
        st.switch_page("pages/Admin.py")

st.divider()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
tab = st.session_state.tab
st.sidebar.header(tab)
section = st.sidebar.selectbox("Category", MENU_TREE[tab].keys())
topic = st.sidebar.radio("Topic", MENU_TREE[tab][section].keys())

content = MENU_TREE[tab][section][topic]

# -------------------------------------------------
# LIMIT
# -------------------------------------------------
count = get_usage("user_id" if st.session_state.logged_in else "anon_id",
                  st.session_state.user_id if st.session_state.logged_in else st.session_state.anon_id)

AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL")

if count >= 5 and not st.session_state.logged_in:
    st.warning("🔒 Free limit reached here")
    st.link_button(
        "Continue with Google",
        f"{AUTH_BACKEND_URL}/auth/google"
    )
    st.stop()

inc_usage("user_id" if st.session_state.logged_in else "anon_id",
          st.session_state.user_id if st.session_state.logged_in else st.session_state.anon_id)

# -------------------------------------------------
# CONTENT
# -------------------------------------------------
BASE = Path(__file__).parent
IMG = BASE / "images"
TXT = BASE / "content"

col_img, col_txt = st.columns([3,2])

if "animated_once" not in st.session_state:
    st.session_state.animated_once = False

def render_image(image_name, unique_key):
    img_path = IMG / image_name
    img_bytes = img_path.read_bytes()
    img_base64 = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <style>
            .blur-img {{
                width: 100%;
                border-radius: 12px;
                filter: blur(18px);
                animation: unblur 1.1s ease-out forwards;
            }}
            @keyframes unblur {{
                to {{ filter: blur(0); }}
            }}
        </style>

        <img
            key="{unique_key}"
            src="data:image/png;base64,{img_base64}"
            class="blur-img"
        />
        """,
        unsafe_allow_html=True
    )



with col_img:
    st.subheader("Diagram")

    tab_gen, tab_anim = st.tabs(["🖼️ Generate", "🎞️ Animate"])

    # -------- Generate tab
    with tab_gen:
        img_name = content.get("image")
        if img_name:
            img_path = IMG / img_name
            if img_path.exists():
                img_bytes = img_path.read_bytes()
                img_base64 = base64.b64encode(img_bytes).decode()

                html_key = f"{section}_{topic}_gen"

                st.markdown(
                    f"""
                    <style>
                        .blur-img {{
                            width: 100%;
                            border-radius: 12px;
                            filter: blur(18px);
                            animation: unblur 1.1s ease-out forwards;
                        }}
                        @keyframes unblur {{
                            to {{ filter: blur(0); }}
                        }}
                    </style>

                    <img
                        key="{html_key}"
                        src="data:image/png;base64,{img_base64}"
                        class="blur-img"
                    />
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ Image not found: {img_name}")
        else:
            st.info("No diagram available.")

    # -------- Animate tab
    with tab_anim:
        img_name = content.get("image_anim")
        if img_name:
            img_path = IMG / img_name
            if img_path.exists():
                img_bytes = img_path.read_bytes()
                img_base64 = base64.b64encode(img_bytes).decode()

                html_key = f"{section}_{topic}_anim"

                st.markdown(
                    f"""
                    <style>
                        .blur-img {{
                            width: 100%;
                            border-radius: 12px;
                            filter: blur(18px);
                            animation: unblur 1.1s ease-out forwards;
                        }}
                        @keyframes unblur {{
                            to {{ filter: blur(0); }}
                        }}
                    </style>

                    <img
                        key="{html_key}"
                        src="data:image/png;base64,{img_base64}"
                        class="blur-img"
                    />
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ Image not found: {img_name}")
        else:
            st.info("No animated diagram available.")




def type_md(p):
    o = st.empty()
    s=""
    for c in p:
        s+=c; o.markdown(s); time.sleep(0.003)

with col_txt:
    st.subheader("Details")
    s,t = st.tabs(["📘 Summary","⚖️ Trade-offs"])
    with s:
        type_md((TXT/content["text_md"]).read_text())
    with t:

        type_md((TXT/content["trade_md"]).read_text())



