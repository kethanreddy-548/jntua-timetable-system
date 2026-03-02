import streamlit as st
import os

st.set_page_config(
    page_title="JNTUA CEA — Timetable System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()
load_env()

from database.db import init_db
from database.seed_data import seed_all
if "db_ready" not in st.session_state:
    init_db()
    seed_all()
    st.session_state["db_ready"] = True

from auth.security import is_logged_in, logout_user, current_role
from pages import login, dashboard, manage_subjects, manage_faculty, generate, manage_rooms

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0a0f1e !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #0a0f1e 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
.stButton > button {
    background: transparent !important; color: #94a3b8 !important;
    border: 1px solid rgba(99,102,241,0.15) !important; border-radius: 10px !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 0.5rem 0.8rem !important; transition: all 0.2s ease !important;
    text-align: left !important; width: 100% !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.5) !important;
    color: #a5b4fc !important; transform: translateX(2px) !important;
}
.stButton > button:active { background: rgba(99,102,241,0.2) !important; }
.stTextInput > label, .stSelectbox > label,
.stNumberInput > label, .stMultiSelect > label,
.stSlider > label { color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; }
.stTextInput > div > div > input {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important; color: #e2e8f0 !important; font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
div[data-baseweb="select"] > div {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #131929 !important; border-radius: 12px !important;
    padding: 5px !important; gap: 4px !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important; font-weight: 600 !important;
    font-size: 0.83rem !important; border-radius: 8px !important; padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important; box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
}
.streamlit-expanderHeader {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 8px !important; color: #94a3b8 !important; font-size: 0.83rem !important;
}
.streamlit-expanderContent {
    background: #0d1321 !important; border: 1px solid rgba(99,102,241,0.15) !important;
    border-top: none !important; border-radius: 0 0 8px 8px !important;
}
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
[data-testid="stDataFrameResizable"] {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 10px !important;
}
.stSuccess, .stError, .stWarning, .stInfo { border-radius: 10px !important; font-size: 0.85rem !important; }
[data-testid="metric-container"] {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important; padding: 1rem !important;
}
hr { border-color: rgba(99,102,241,0.15) !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0f1e; }
::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #4f46e5; }
.stNumberInput > div > div > input {
    background: #131929 !important; border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
.stCheckbox > label { color: #94a3b8 !important; font-size: 0.85rem !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed) !important; border-radius: 4px !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 0.55rem 1.2rem !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important; transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important; transform: translateY(-1px) !important;
}
.main .block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
span[data-baseweb="tag"] {
    background: rgba(99,102,241,0.2) !important; border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 6px !important; color: #a5b4fc !important;
}
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1.5rem 1rem 1rem;border-bottom:1px solid rgba(99,102,241,0.15);margin-bottom:0.5rem">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                <div style="font-size:1.6rem">🎓</div>
                <div>
                    <div style="font-size:1rem;font-weight:800;color:#e2e8f0;letter-spacing:-0.3px">JNTUA CEA</div>
                    <div style="font-size:0.68rem;color:#4f46e5;font-weight:600;letter-spacing:1px;text-transform:uppercase">Timetable System</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── PUBLIC NAV ────────────────────────────────────────
        st.markdown("""<div style="padding:0.6rem 0.8rem 0.3rem;font-size:0.68rem;
        font-weight:700;color:#475569;letter-spacing:1.2px;text-transform:uppercase">
        Navigation</div>""", unsafe_allow_html=True)

        for icon, label, key in [
            ("🏠", "Dashboard",          "dashboard"),
            ("🗓️", "Generate Timetable", "generate"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        # ── ADMIN NAV ─────────────────────────────────────────
        st.markdown("""<div style="padding:0.8rem 0.8rem 0.3rem;font-size:0.68rem;
        font-weight:700;color:#475569;letter-spacing:1.2px;text-transform:uppercase;
        margin-top:0.4rem">Admin Panel</div>""", unsafe_allow_html=True)

        for icon, label, key in [
            ("📚",  "Manage Subjects", "subjects"),
            ("👨‍🏫", "Manage Faculty",  "faculty"),
            ("🏛️",  "Manage Rooms",    "rooms"),
        ]:
            if st.button(f"{icon}  {label}  🔒", key=f"nav_{key}", use_container_width=True):
                if not is_logged_in():
                    st.session_state["redirect_after"] = key
                    st.session_state["page"] = "login"
                else:
                    st.session_state["page"] = key
                st.rerun()

        st.divider()

        # ── AUTH ──────────────────────────────────────────────
        if is_logged_in():
            role        = current_role()
            full_name   = st.session_state.get("full_name", "")
            badge_color = "#6366f1" if role == "superadmin" else "#059669"
            badge_label = "Super Admin" if role == "superadmin" else "HOD"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(124,58,237,0.08));
            border:1px solid rgba(99,102,241,0.2);border-radius:10px;padding:0.8rem;margin-bottom:0.8rem">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:32px;height:32px;background:linear-gradient(135deg,#4f46e5,#7c3aed);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.85rem">👤</div>
                    <div>
                        <div style="color:#e2e8f0;font-weight:600;font-size:0.82rem">{full_name}</div>
                        <div style="color:{badge_color};font-size:0.68rem;font-weight:600">{badge_label}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔒 Change Password"):
                with st.form("pwd_form", clear_on_submit=True):
                    old_pwd = st.text_input("Current Password", type="password")
                    new_pwd = st.text_input("New Password", type="password")
                    cnf_pwd = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Update", use_container_width=True):
                        from auth.security import change_password
                        if new_pwd != cnf_pwd:
                            st.error("Passwords don't match!")
                        else:
                            res = change_password(st.session_state["user_id"], old_pwd, new_pwd)
                            st.error(res["error"]) if "error" in res else st.success("✅ Updated!")

            if st.button("🚪  Sign Out", use_container_width=True, key="logout_btn"):
                logout_user()
                st.session_state["page"] = "dashboard"
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;padding:0.5rem 0;color:#475569;font-size:0.78rem">
            Admin access required to manage data
            </div>""", unsafe_allow_html=True)
            if st.button("🔑  Admin Login", use_container_width=True, key="sidebar_login"):
                st.session_state["page"] = "login"
                st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;
        color:#1e293b;font-size:0.68rem">R23 (Y1–Y3) · R21 (Y4) · v3.0</div>
        """, unsafe_allow_html=True)


# ── RENDER SIDEBAR ────────────────────────────────────────────
render_sidebar()

# ── ROUTER ────────────────────────────────────────────────────
page = st.session_state.get("page", "dashboard")

# Protected pages — require login
if page in ("subjects", "faculty", "rooms") and not is_logged_in():
    st.session_state["redirect_after"] = page
    page = "login"

if page == "login":
    login.show()
    if is_logged_in() and "redirect_after" in st.session_state:
        st.session_state["page"] = st.session_state.pop("redirect_after")
        st.rerun()
elif page == "dashboard":
    dashboard.show()
elif page == "generate":
    generate.show()
elif page == "subjects":
    manage_subjects.show()
elif page == "faculty":
    manage_faculty.show()
elif page == "rooms":
    manage_rooms.show()
else:
    dashboard.show()