"""Login Page"""
import streamlit as st
from auth.security import authenticate, login_user

def show():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); }
    .login-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 16px; padding: 2.5rem;
        max-width: 420px; margin: 3rem auto;
        box-shadow: 0 0 40px rgba(48,164,108,0.15);
    }
    .login-title {
        font-size: 1.6rem; font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.3rem;
    }
    .login-sub { color: #8b949e; text-align: center; font-size: 0.85rem; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-title">🎓 JNTUA CEA</div>
            <div class="login-sub">Timetable Management System</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("###")
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 Sign In")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit   = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    result = authenticate(username.strip(), password)

                if result and "error" in result:
                    st.error(f"❌ {result['error']}")
                elif result:
                    login_user(result)
                    st.success(f"✅ Welcome, {result['full_name'] or username}!")
                    st.session_state["page"] = "dashboard"
                    st.rerun()
                else:
                    st.error("❌ Authentication failed")

        st.markdown("---")
        st.markdown("""
        <div style="color:#8b949e; font-size:0.78rem; text-align:center">
        🔒 Secure login · Contact admin for credentials<br>
        Account locks after 5 failed attempts (15 min)
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🧪 Demo Credentials"):
            st.code("""Super Admin:
  Username: superadmin
  Password: Admin@JNTUA2024

HOD CSE:
  Username: hod_cse
  Password: HOD_CSE@2024

HOD ECE:
  Username: hod_ece
  Password: HOD_ECE@2024""")
