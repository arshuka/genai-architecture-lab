import streamlit as st
import sqlite3
from pathlib import Path

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Admin Dashboard", layout="wide")

ADMIN_EMAIL = "arshuka@gmail.com"
DB_PATH = Path("users.db")

# -------------------------------------------------
# DB HELPERS
# -------------------------------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def fetch_table(table_name):
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
    cols = [desc[0] for desc in cur.description]
    conn.close()
    return cols, rows

# -------------------------------------------------
# AUTH CHECK
# -------------------------------------------------
user_id = st.query_params.get("user_id") or st.session_state.get("user_id")

if not user_id:
    st.error("❌ Not logged in")
    st.stop()


conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT email FROM users WHERE id = ?", (user_id,))
row = cur.fetchone()
conn.close()

if not row:
    st.error("❌ User not found")
    st.stop()

email = row[0]

if email != ADMIN_EMAIL:
    st.error("⛔ You are not authorized to view Admin Dashboard")
    st.stop()

# -------------------------------------------------
# ADMIN UI
# -------------------------------------------------
st.title("🛠 Admin Dashboard")
st.caption(f"Logged in as: {email}")

st.divider()

# -------------------------------------------------
# USERS TABLE
# -------------------------------------------------
st.subheader("👤 Users")
cols, rows = fetch_table("users")
st.dataframe(rows, use_container_width=True)

# -------------------------------------------------
# ANONYMOUS USAGE
# -------------------------------------------------
st.subheader("👻 Anonymous Usage")
cols, rows = fetch_table("usage")
st.dataframe(rows, use_container_width=True)

# -------------------------------------------------
# USER USAGE
# -------------------------------------------------
st.subheader("📊 User Usage")
cols, rows = fetch_table("user_usage")
st.dataframe(rows, use_container_width=True)

st.divider()

st.info("🔒 Admin access restricted to authorized account only.")
