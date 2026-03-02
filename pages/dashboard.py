"""Dashboard — Home page after login"""
import streamlit as st
from database.db import fetchone, fetchall
from auth.security import current_role, current_dept_id
def show():
    role    = current_role()
    dept_id = current_dept_id()

    st.markdown("## 🏠 Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.get('full_name', 'User')}** · Role: `{role.upper()}`")
    st.markdown("---")

    if role == "superadmin":
        # System-wide stats
        total_faculty   = fetchone("SELECT COUNT(*) as c FROM faculty WHERE is_active=1")
        total_subjects  = fetchone("SELECT COUNT(*) as c FROM subjects WHERE is_active=1")
        total_depts     = fetchone("SELECT COUNT(*) as c FROM departments")
        total_users     = fetchone("SELECT COUNT(*) as c FROM users WHERE is_active=1")

        c1,c2,c3,c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "Departments",  total_depts["c"],   "#00d4ff"),
            (c2, "Active Faculty", total_faculty["c"],"#00ff88"),
            (c3, "Active Subjects",total_subjects["c"],"#e3b341"),
            (c4, "System Users",   total_users["c"],  "#f85149"),
        ]:
            col.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;
            border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:700;color:{color}">{val}</div>
            <div style="color:#8b949e;font-size:0.82rem">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("### 📊 Department-wise Summary")
        dept_stats = fetchall("""
            SELECT d.code, d.name,
            COUNT(DISTINCT CASE WHEN f.is_active=1 THEN f.id END) as faculty_count,
            COUNT(DISTINCT CASE WHEN s.is_active=1 THEN s.id END) as subject_count
            FROM departments d
            LEFT JOIN faculty f ON f.dept_id=d.id
            LEFT JOIN subjects s ON s.dept_id=d.id
            GROUP BY d.id ORDER BY d.code
        """)

        import pandas as pd
        if dept_stats:
            df = pd.DataFrame(dept_stats)
            df.columns = ["Code","Department","Active Faculty","Active Subjects"]
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### 👥 Recent Login Activity")
        recent = fetchall("""
            SELECT u.full_name, u.username, u.role, u.last_login
            FROM users u WHERE u.last_login IS NOT NULL
            ORDER BY u.last_login DESC LIMIT 10
        """)
        if recent:
            df2 = pd.DataFrame(recent)
            df2.columns = ["Name","Username","Role","Last Login"]
            st.dataframe(df2, use_container_width=True, hide_index=True)

    else:
        # HOD view — show their department info
        dept = fetchone("SELECT * FROM departments WHERE id=?", (dept_id,))
        if dept:
            st.markdown(f"### 🏛️ {dept['name']} ({dept['code']})")

            fc = fetchone("SELECT COUNT(*) as c FROM faculty WHERE dept_id=? AND is_active=1", (dept_id,))
            sc = fetchone("SELECT COUNT(*) as c FROM subjects WHERE dept_id=? AND is_active=1", (dept_id,))

            c1, c2 = st.columns(2)
            c1.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;
            border-radius:10px;padding:1.5rem;text-align:center">
            <div style="font-size:2.5rem;font-weight:700;color:#00ff88">{fc["c"]}</div>
            <div style="color:#8b949e">Active Faculty</div></div>""", unsafe_allow_html=True)
            c2.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;
            border-radius:10px;padding:1.5rem;text-align:center">
            <div style="font-size:2.5rem;font-weight:700;color:#00d4ff">{sc["c"]}</div>
            <div style="color:#8b949e">Active Subjects</div></div>""", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("### 📋 Quick Subject Overview")
            for yr in [1,2,3,4]:
                reg = "R21" if yr == 4 else "R23"
                subjs = fetchall("""
                    SELECT code, name, year, semester, type, hours_week
                    FROM subjects WHERE dept_id=? AND year=? AND is_active=1
                    ORDER BY semester, type, name
                """, (dept_id, yr))
                if subjs:
                    import pandas as pd
                    df = pd.DataFrame(subjs)
                    with st.expander(f"Year {yr} — {reg} ({len(subjs)} subjects)"):
                        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("📚 Manage Subjects", use_container_width=True):
            st.session_state["page"] = "subjects"
            st.rerun()
    with qc2:
        if st.button("👨‍🏫 Manage Faculty", use_container_width=True):
            st.session_state["page"] = "faculty"
            st.rerun()
    with qc3:
        if st.button("🗓️ Generate Timetable", use_container_width=True):
            st.session_state["page"] = "generate"
            st.rerun()
