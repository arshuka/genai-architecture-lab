# NOTE: This is a CLEANED, WORKING reference version focused on:
# 1) Ask AI placement (no overlap)
# 2) Login + 5-question global limit
# 3) No NameError (question / answer_key safe)
# It keeps your existing structure but removes duplicated Ask AI buttons

import streamlit as st
from pathlib import Path
import base64, uuid, time, os
from supabase import create_client
from dotenv import load_dotenv
from menu_config import MENU_TREE
from openai import OpenAI

load_dotenv()


# -------------------------------------------------
# CSS (minimal – stable)
# -------------------------------------------------
st.markdown(
    """
<style>
header {visibility:hidden; height:0;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}


section[data-testid="stMain"] {
    zoom: 0.90;
} 

/* Remove global top padding */
div.block-container {
    padding-top: 0rem !important;
}

/* Remove Streamlit top header space */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Remove space created after hiding header */
section[data-testid="stSidebar"] {
    margin-top: -1rem !important;
}

section[data-testid="stMain"] {
    margin-top: -1rem !important;
}


/* Remove Streamlit global top spacing completely */
.main .block-container {
    padding-top: 0rem !important;
}

/* Remove sidebar internal top gap fully */
section[data-testid="stSidebar"] .block-container {
    padding-top: 0rem !important;
}

/* Remove any margin created by hidden header */
header[data-testid="stHeader"] + div {
    margin-top: 0 !important;
}


/* Prevent horizontal scroll */
html, body {
    overflow-x: hidden;
}

/* Remove extra top space before first column content */
[data-testid="column"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Tighten image positioning */
.blur-img {
    margin-top: 0 !important;
}

/* LinkedIn-style centered canvas */
.block-container {
    padding-top: 0.6rem;
    padding-bottom: 0.6rem;
}

/* Image slow-render animation */
.blur-img {
    width: 95%;
    border-radius: 12px;
}

 
.arch-img {
    display: block;
    margin: 0 auto;
    max-width: 95%;
    height: auto;
    object-fit: contain;
}

.card {
  background: #E0E8E9;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  padding: 18px;
  margin-bottom: 18px;
}

.ask {
  background: #fffff3;
  border-radius: 10px;
  box-shadow: 0 6px 10px rgba(0,0,0,0.08);
  padding: 10px;
  margin-bottom: 10px;
}

/* Force text inputs (textarea + input) to white background */
textarea, 
input[type="text"], 
div[data-baseweb="textarea"] textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 8px !important;
}

/* Improve focus visibility */
textarea:focus {
    border: 1px solid #3b82f6 !important;
    outline: none !important;
}

/* Shadow card for Summary / Trade-offs */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stTabs"]) {
    background: white;
    border-radius: 16px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    padding: 16px;
}

/* Sidebar shadow */
section[data-testid="stSidebar"] {
   box-shadow: 6px 0 28px rgba(0, 0, 0, 0.18);
    background: #f8faf1;
    border-right: 1px solid rgba(0,0,0,0.05);
    width: 340px !important;
}


.sidebar-brand {
    font-size: 19px;
    font-weight: 700;

    background: linear-gradient(135deg, #4b5563, #6b7280);

    color: white;
    padding: 14px 18px;
    border-radius: 18px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.35);

    margin-bottom: 22px;

    display: flex;
    align-items: center;
    gap: 0px;
}

/* Top-right account links */
.top-account {
    text-align: right;
    font-size: 14px;
    margin-top: 6px;
}

.acct-name {
    font-weight: 600;
    color: #1f2937;
    margin-right: 6px;
}

.acct-email {
    color: #6b7280;
    margin-right: 10px;
    font-size: 13px;
}

.acct-link {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
    margin-left: 8px;
}

.acct-link:hover {
    text-decoration: underline;
}

button[kind="secondary"] {
padding: 4px 10px;
font-size: 13px;
}

.top-account-inline {
    white-space: nowrap;
    font-size: 14px;
}

.acct-name {
    font-weight: 600;
    margin-right: 6px;
}

.acct-email {
    color: #6b7280;
    font-size: 13px;
}

</style>
""",
    unsafe_allow_html=True,
)
 
openai_client = OpenAI(
    api_key=os.getenv("AUTO_KEY")
)

if not os.getenv("AUTO_KEY"):
    st.error("KEY not found in environment")



@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=os.getenv("AUTO_KEY"))

@st.cache_data
def load_image_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")

with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            🧠 GenAI Architecture Lab
        </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# SESSION DEFAULTS
# -------------------------------------------------
for k, v in {
    "typed_topics": set(),
    "logged_in": False,
    "prev_context": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

 # bg = "#f0edec" if i % 2 == 0 else "#E0E8E9"
# -------------------------------------------------
# SUPABASE
# -------------------------------------------------
@st.cache_resource
def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"],
        os.getenv("SUPABASE_SERVICE_KEY") or st.secrets["SUPABASE_SERVICE_KEY"],
    )

supabase = get_supabase()


# -------------------------------------------------
# AUTH STATE
# -------------------------------------------------
if "user_id" in st.query_params:
    st.session_state.logged_in = True
    st.session_state.user_id = st.query_params["user_id"]
else:
    st.session_state.logged_in = False
    if "anon_id" not in st.session_state:
        st.session_state.anon_id = str(uuid.uuid4())


AI_COMPONENTS = [
    "LLM Core",
    "Prompt Engineering",
    "RAG (Retrieval Augmented Generation)",
    "Vector Database",
    "Embedding Model",
    "Tool / Function Calling",
    "AI Agent",
    "Multi-Agent Orchestration",
    "Memory (Short / Long-term)",
    "Guardrails & Safety",
    "Observability & Logging",
    "Cost Control & Caching",
    "API Gateway / Access Layer",
    "Human-in-the-Loop (HITL)"
]


# -------------------------------------------------
# ASK‑AI USAGE HELPERS
# -------------------------------------------------

def get_user_email(user_id):
    res = (
        supabase
        .table("users")
        .select("email")
        .eq("id", user_id)
        .single()
        .execute()
    )
    return res.data["email"] if res.data else None


def get_ask_ai_count(user_id):
    res = (
        supabase.table("ask_ai_usage")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    return res.count or 0

def get_usage(col, key):
    r = supabase.table("usage").select("count").eq(col, key).execute()
    return r.data[0]["count"] if r.data else 0

def inc_usage(col, key):
    supabase.rpc("increment_usage", {"col_name": col, "key_val": key}).execute()

def log_ask_ai(user_id, question, page_context):
    user_email = get_user_email(user_id)

    supabase.table("ask_ai_usage").insert({
        "user_id": user_id,
        "email": user_email,
        "question": question,
        "page_context": page_context,
    }).execute()


def enforce_ask_ai_limit(question, page_context):
    AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL")

    if not st.session_state.logged_in:
        st.warning("🔐 Please log in to use Ask AI")
        st.link_button("Continue with Google", f"{AUTH_BACKEND_URL}/auth/google")
        return False

    user_id = st.session_state.user_id
    used = get_ask_ai_count(user_id)

    if used >= 10:
        st.error("🚫 Free limit reached..")
        st.info("Upgrade to continue using Ask AI")
        st.button("💳 Upgrade Plan")
        return False

    log_ask_ai(user_id, question, page_context)
    return True

def ask_openai(question: str, topic: str):
    system_prompt = f"""
        You are a senior GenAI architect.
        Explain clearly, practically, and honestly.
        Avoid fluff. Use bullets when useful.
        Context: {topic}
        """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.4,
        max_tokens=400,
    )

    return response.choices[0].message.content

# -------------------------------------------------
# HEADER
# -------------------------------------------------
#st.markdown("## 🧠 GenAI Architecture Lab")

#st.markdown("""
#<div class="card">
  #<h3>🧠 GenAI Architecture Lab</h3>
#</div>
# """, unsafe_allow_html=True)




# -------------------------------------------------
# TOP MENU + ACCOUNT (SAME ROW)
# -------------------------------------------------
# ==============================


# ==================================================
# FIXED TOP BAR FRAME
# ==================================================

topbar = st.container()

with topbar:

    col_left, col_right = st.columns([6, 2])

    with col_left:

        tabs = {
            "🏠 Welcome": "Welcome",
            "🧠 GenAI": "GenAI",
            "🛡 AI One-Stop": "AI One-Stop",
            "☁️ Cloud AI": "Cloud AI",
            "🛠 AI Tools": "AI Tools",
        }

        reverse_tabs = {v: k for k, v in tabs.items()}

        if "tab" not in st.session_state:
            st.session_state.tab = "GenAI"

        if "menu_selected" not in st.session_state:
            st.session_state.menu_selected = reverse_tabs[st.session_state.tab]

        selected = st.segmented_control(
            "",
            options=list(tabs.keys()),
            key="menu_selected"
        )

        st.session_state.tab = tabs[selected]

    with col_right:

        AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL")

        if st.session_state.get("logged_in"):
            user = supabase.table("users").select("*").eq(
                "id", st.session_state.user_id
            ).execute().data[0]

            st.markdown(f"""
            <div class="top-account">
                <span class="acct-name">{user.get('name','User')}</span>
                <span class="acct-email">({user['email']})</span>
                <a href="?logout=true" class="acct-link" target="_self">Logout</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="top-account">
                    <span class="acct-name">Guest</span>
                    <a href="{AUTH_BACKEND_URL}/auth/google" class="acct-link" target="_top">Login</a>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<hr style='margin:0.5rem 0 0.75rem 0;'>", unsafe_allow_html=True)




#st.divider()
st.markdown("<hr style='margin:0.5rem 0 0.75rem 0;'>", unsafe_allow_html=True)


# -------------------------------------------------
# LIMIT
# -------------------------------------------------
count = get_usage("user_id" if st.session_state.logged_in else "anon_id",
                  st.session_state.user_id if st.session_state.logged_in else st.session_state.anon_id)

AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL")

if count >= 5 and not st.session_state.logged_in:
    st.warning("🔒 Login to continue...")
    st.link_button(
        "Continue with Google",
        f"{AUTH_BACKEND_URL}/auth/google"
    )
    st.stop()

inc_usage("user_id" if st.session_state.logged_in else "anon_id",
          st.session_state.user_id if st.session_state.logged_in else st.session_state.anon_id)



# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------


st.sidebar.header(st.session_state.tab)
section = st.sidebar.selectbox("Category", MENU_TREE[st.session_state.tab].keys())
topic = st.sidebar.radio("Topic", MENU_TREE[st.session_state.tab][section].keys())
content = MENU_TREE[st.session_state.tab][section][topic]

context_key = f"{st.session_state.tab}|{section}|{topic}"


 
# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE = Path(__file__).parent
IMG = BASE / "images"
TXT = BASE / "content"

shared_answer_key = f"a_{section}_{topic}"

# Clear Ask‑AI answers when topic changes
#if st.session_state.prev_context != context_key:
 #   if shared_answer_key in st.session_state:
 #       del st.session_state[shared_answer_key]
 #   st.session_state.prev_context = context_key

def render_ask_ai_block(
    section: str,
    topic: str,
    location: str,   # e.g. "tab" or "bottom"
    shared_answer_key: str
    ):
   
    question_key = f"q_{section}_{topic}_{location}"
    button_key   = f"ask_{section}_{topic}_{location}"

  # Custom styled label
    st.markdown("""
    <style>
    /* Remove top spacing of text area container */
    div[data-testid="stTextArea"] {
        margin-top: -10px !important;
    }

    /* Remove extra spacing from internal block wrapper */
    div[data-testid="stTextArea"] > div {
        margin-top: -14px !important;
    }

    /* Tighten your custom label */
    .ask-label {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)


    st.markdown('<div class="ask-label">Type your question</div>', unsafe_allow_html=True)

    question = st.text_area(
        label="",
        key=question_key,
        placeholder="e.g. When should this architecture be avoided in production?",
        height=120,
    )



    if st.button("Get Expert Insight", key=button_key):
        if not question.strip():
            st.warning("Please enter a question")
            return

        allowed = enforce_ask_ai_limit(question, f"{section}|{topic}")
        if not allowed:
            return

        with st.spinner("🤖 Thinking..."):
            answer = ask_openai(question, topic)

            st.session_state[shared_answer_key] = f"""
            ### 🤖 AI Insight
            **Architecture:** {topic}

            **Your question:**
            {question}

            ---
            {answer}
            """

    if shared_answer_key in st.session_state:
        st.markdown(st.session_state[shared_answer_key])



def render_comments_block(tab, section, topic):

    form_key = f"comment_form_{tab}_{section}_{topic}"

    with st.form(key=form_key, clear_on_submit=True):

        comment = st.text_area(
            "Write a comment",
            placeholder="What worked for you? What should others watch out for?",
            height=100
        )

        submitted = st.form_submit_button("Post comment")

        if submitted:

            if not st.session_state.logged_in:
                st.warning("🔐 Please log in to post comments")
                return

            if not comment.strip():
                st.warning("Comment cannot be empty")
                return

            supabase.table("architecture_comments").insert({
                "user_id": st.session_state.user_id,
                "tab": tab,
                "section": section,
                "topic": topic,
                "comment": comment.strip()
            }).execute()

            #st.success("✅ Comment posted")
            #st.rerun()

            st.markdown("""
                <div style="
                    background:#e8f7ee;
                    border-left:4px solid #2ecc71;
                    padding:10px 14px;
                    border-radius:8px;
                    margin-top:10px;
                    color:#1e7e34;
                    font-weight:500;
                ">
                ✅ Comment posted successfully
                </div>
                """, unsafe_allow_html=True)
            st.rerun()



def render_comment_list(tab, section, topic):
    res = (
        supabase
        .table("architecture_comments")
        .select("comment, created_at, users(name)")
        .eq("tab", tab)
        .eq("section", section)
        .eq("topic", topic)
        .order("created_at", desc=True)
        .execute()
    )

    if not res.data:
        st.info("No comments yet. Be the first to share 👋")
        return

    for i, row in enumerate(res.data):

        bg = "#f0f3e9" if i % 2 == 0 else "#f5eeec"

        st.markdown(f"""
        <div style="
            background:{bg};
            border:1px solid #e6e9ef;
            border-radius:12px;
            padding:14px 16px;
            margin-bottom:10px;
        ">
          <div style="font-weight:600; color:#1f2937;">
            {row['users']['name']}
            <span style="
                font-weight:400;
                color:#6b7280;
                font-size:12px;
            ">
              · {row['created_at'][:19].replace('T',' ')}
            </span>
          </div>

          <div style="
              margin-top:6px;
              color:#374151;
              line-height:1.5;
          ">
            {row['comment']}
          </div>
        </div>
        """, unsafe_allow_html=True)



# -------------------------------------------------
# LAYOUT
# -------------------------------------------------

#col_center, col_right = st.columns([3.8, 2])

col_center, col_right = st.columns([3.8, 2])

# -------------------------------------------------
# IMAGE
# -------------------------------------------------
#if "active_tab" not in st.session_state:
#    st.session_state.active_tab = "Generate"

#image_slot = st.empty()

#tab_gen, tab_anim = st.tabs(["🖼️ Generate", "🎞️ Animate"])

with col_center:

    #tab_gen, tab_anim = st.tabs(["🖼️ Generate", "🎞️ Animate"])
    
    #tab_container = st.container(key=f"arch_container_{section}_{topic}")
    #tab_container = st.container()

    tab_container = st.container(key=f"tabs_for_{topic}")


    #with tab_container:
        # tab_gen, tab_anim = st.tabs(["🖼️ Generate", "🎞️ Animate"])
    tab_a1, tab_a2, tab_a3, tab_lab, tab_ask, tab_comm = st.tabs(
        [
            "🏗 Architecture-1",
            "🏗 Architecture-2",
            "🏗 Architecture-3",
            "🧪 Architecture Lab",
            "🧠 Ask Anything",
            "💬 Comments",
        ]
    )
 
    # -------- Generate --------
    with tab_a1:
        st.markdown(f"""
        <div class="ask">
        <h3>Architecture Model-1 — <span style="color:#2563eb">{topic}</span></h3>
        </div>
        """, unsafe_allow_html=True)


        img_name = content.get("image1")  # or image2 / image3

        if img_name and (IMG / img_name).exists():
                img_path = IMG / img_name
        else:
                img_path = IMG / "comingsoon1.png"   # fallback image

        if img_path.exists():
                img_base64 = load_image_base64(img_path)

                st.markdown(
                    f"""
                    <div style="
                        padding:12px;
                        border-radius:16px;
                        background:white;
                        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                        margin-bottom:16px;
                    ">
                        <img src="data:image/png;base64,{img_base64}"
                            style="
                                width:95%;
                                display:block;
                                margin:0 auto;
                                border-radius:12px;
                            " />
                    </div>
                    """,
                    unsafe_allow_html=True
                )



        render_ask_ai_block(
                section=section,
                topic=topic,
                location="bottom_1",
                shared_answer_key=shared_answer_key
        )

    # -------- Animate --------
    with tab_a2:
        st.markdown(f"""
        <div class="ask">
        <h3>Architecture Model-2 — <span style="color:#2563eb">{topic}</span></h3>
        </div>
        """, unsafe_allow_html=True)

        img_name = content.get("image2")  # or image2 / image3

        if img_name and (IMG / img_name).exists():
                img_path = IMG / img_name
        else:
                img_path = IMG / "comingsoon2.png"   # fallback image

        if img_path.exists():
                img_base64 = load_image_base64(img_path)

                st.markdown(
                    f"""
                    <div style="
                        padding:12px;
                        border-radius:16px;
                        background:white;
                        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                        margin-bottom:16px;
                    ">
                        <img src="data:image/png;base64,{img_base64}"
                            style="
                                width:95%;
                                display:block;
                                margin:0 auto;
                                border-radius:12px;
                            " />
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        render_ask_ai_block(
                section=section,
                topic=topic,
                location="bottom_2",
                shared_answer_key=shared_answer_key
        )

    with tab_a3:
        st.markdown(f"""
        <div class="ask">
        <h3>Architecture Model-3 — <span style="color:#2563eb">{topic}</span></h3>
        </div>
        """, unsafe_allow_html=True)

        img_name = content.get("image3")  # or image2 / image3

        if img_name and (IMG / img_name).exists():
                img_path = IMG / img_name
        else:
                img_path = IMG / "comingsoon3.png"   # fallback image

        if img_path.exists():
                img_base64 = load_image_base64(img_path)

                st.markdown(
                    f"""
                    <div style="
                        padding:12px;
                        border-radius:16px;
                        background:white;
                        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                        margin-bottom:16px;
                    ">
                        <img src="data:image/png;base64,{img_base64}"
                            style="
                                width:95%;
                                display:block;
                                margin:0 auto;
                                border-radius:12px;
                            " />
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        render_ask_ai_block(
                section=section,
                topic=topic,
                location="bottom_3",
                shared_answer_key=shared_answer_key
        )


    with tab_lab:
        st.markdown("### 🧪 Architecture Lab")
        st.caption("Compose your own architecture by selecting building blocks")

        # ------------------------------------
        # Base architecture (radio-selected)
        # ------------------------------------
        base_arch = topic  # sidebar radio value
        image_state_key = f"generated_image_{section}_{base_arch}"
        prompt_state_key = f"generated_prompt_{section}_{base_arch}"

        st.markdown(
            f"""
            <div style="
                background:#eef2ff;
                padding:10px 14px;
                border-radius:10px;
                margin-bottom:14px;
                font-weight:600;
                color:#1e3a8a;
            ">
                Base Architecture: {base_arch}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ------------------------------------
        # Session state init (per topic)
        # ------------------------------------
        state_key = f"arch_lab_components_{section}_{base_arch}"

        if state_key not in st.session_state:
            st.session_state[state_key] = {base_arch: True}

        # ------------------------------------
        # Checkbox grid
        # ------------------------------------
        st.markdown("#### Select Architecture Components")

        all_components = [base_arch] + AI_COMPONENTS
        cols = st.columns(4)

        for i, comp in enumerate(all_components):
            with cols[i % 4]:
                checked = st.checkbox(
                    comp,
                    value=st.session_state[state_key].get(comp, comp == base_arch),
                    key=f"chk_{section}_{base_arch}_{comp}",
                )
                st.session_state[state_key][comp] = checked

        # ------------------------------------
        # Optional details
        # ------------------------------------
        st.markdown("### Optional Details (Scale, Cloud, Domain, Constraints)")

        extra_details = st.text_area(
            "",
            placeholder="e.g., AWS, enterprise scale, internal users, high availability",
            height=120,
        )


        # ------------------------------------
        # Prompt builder
        # ------------------------------------
        def build_arch_prompt(base, selections, extra):
            chosen = [k for k, v in selections.items() if v]

            prompt = "create architectural diagram for "

            if chosen:
                prompt += " + ".join(chosen)
            else:
                prompt += base

            if extra.strip():
                prompt += f". Additional details: {extra.strip()}"

            return prompt

        st.markdown('<div class="ask-label">This is for Upgrade Only</div>', unsafe_allow_html=True)

        # ------------------------------------
        # Generate button (ONLY on click)
        # ------------------------------------
     #   if st.button("Generate Architecture", key=f"gen_btn_{section}_{base_arch}"):

     #       final_prompt = build_arch_prompt(
     #           base_arch,
     #           st.session_state[state_key],
     #           extra_details
     #       )

     #       st.session_state[prompt_state_key] = final_prompt

      #      with st.spinner("🎨 Generating architecture diagram..."):

           #     response = openai_client.images.generate(
            #        model="gpt-image-1",
          #          prompt=final_prompt,
         #           size="1024x1024"
          #      )

            #    image_base64 = response.data[0].b64_json

             #   # Store image permanently (per topic)
          #      st.session_state[image_state_key] = image_base64


        # ------------------------------------
        # ALWAYS SHOW IMAGE IF EXISTS
        # ------------------------------------
        if image_state_key in st.session_state:

            st.markdown("### 🖼 Generated Architecture")

            st.markdown(
                f"""
                <div style="
                    padding:12px;
                    border-radius:16px;
                    background:white;
                    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                    margin-top:12px;
                ">
                    <img src="data:image/png;base64,{st.session_state[image_state_key]}"
                        style="
                            width:95%;
                            display:block;
                            margin:0 auto;
                            border-radius:12px;
                        " />
                </div>
                """,
                unsafe_allow_html=True
            )


    with tab_ask:
        st.markdown(f"""
        <div class="ask">
        <h3>🧠 Ask Anything — <span style="color:#2563eb">{topic}</span></h3>
        <p style="margin-top:-6px; color:#6b7280; font-size:13px;">
            You are asking about the <b>{topic}</b> architecture
        </p>
        </div>
        """, unsafe_allow_html=True)
         
        render_ask_ai_block(
            section=section,
            topic=topic,
            location="tab",
            shared_answer_key=shared_answer_key
    )

        
    with tab_comm:
        st.markdown(f"""
        <div class="ask">
        <h3>💬 Comments — <span style="color:#16a34a">{topic}</span></h3>
        <p style="margin-top:-6px; color:#6b7280; font-size:13px;">
            Discussion specific to the <b>{topic}</b> architecture
        </p>
        </div>
        """, unsafe_allow_html=True)


        render_comments_block(
                tab=st.session_state.tab,
                section=section,
                topic=topic
            )

        render_comment_list(
                tab=st.session_state.tab,
                section=section,
                topic=topic
        )
   
 
def type_md(text, delay=0.002):
    placeholder = st.empty()
    rendered = ""
    for ch in text:
        rendered += ch
        placeholder.markdown(rendered)
        time.sleep(delay)

st.markdown("""
<style>
/* Sticky right column like LinkedIn */
[data-testid="column"]:nth-child(2) {
    position: sticky;
    top: 1rem;
    height: fit-content;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SUMMARY / TRADE‑OFFS
# -------------------------------------------------
from pathlib import Path

with col_right:
    summary_container = st.container()

    with summary_container:
        s, t = st.tabs(["📘 Summary", "⚖️ Trade-offs"])

        # ---------- SUMMARY ----------
        with s:
            summary_path = TXT / content.get("text_md", "")

            if summary_path.exists() and summary_path.stat().st_size > 0:
                summary_text = summary_path.read_text().strip()
                if summary_text:
                    st.markdown(summary_text)

        # ---------- TRADE-OFFS ----------
        with t:
            trade_path = TXT / content.get("trade_md", "")

            if trade_path.exists() and trade_path.stat().st_size > 0:
                trade_text = trade_path.read_text().strip()
                if trade_text:
                    st.markdown(trade_text)

