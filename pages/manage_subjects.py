"""Manage Subjects Page — Add / Edit / Delete / Toggle"""
import streamlit as st
from database.db import fetchall, fetchone, execute
from auth.security import require_login, current_role, current_dept_id

REGULATIONS = {"R23": [1,2,3], "R21": [4]}

def get_regulation(year):
    return "R21" if year == 4 else "R23"

def show():
    require_login()
    role    = current_role()
    dept_id = current_dept_id()

    st.markdown("## 📚 Manage Subjects")
    st.markdown("Add, edit, or deactivate subjects per department, year, and semester.")
    st.markdown("---")

    # ── FILTERS ──────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        if role == "superadmin":
            depts = fetchall("SELECT id, code, name FROM departments ORDER BY code")
            dept_options = {d["code"]: d["id"] for d in depts}
            sel_dept_code = st.selectbox("Department", list(dept_options.keys()))
            filter_dept_id = dept_options[sel_dept_code]
        else:
            dept = fetchone("SELECT id, code, name FROM departments WHERE id=?", (dept_id,))
            st.info(f"Department: **{dept['name']}**")
            filter_dept_id = dept_id
            sel_dept_code = dept["code"]

    with f2:
        year = st.selectbox("Year", [1, 2, 3, 4])
    with f3:
        sem  = st.selectbox("Semester", [1, 2])
    with f4:
        regulation = get_regulation(year)
        st.info(f"Regulation: **{regulation}**")

    # ── CURRENT SUBJECTS TABLE ────────────────────────────────
    subjects = fetchall("""
        SELECT s.*, d.code as dept_code
        FROM subjects s JOIN departments d ON s.dept_id=d.id
        WHERE s.dept_id=? AND s.year=? AND s.semester=? AND s.regulation=?
        ORDER BY s.type, s.name
    """, (filter_dept_id, year, sem, regulation))

    st.markdown(f"### 📋 {sel_dept_code} · Year {year} · Sem {sem} · {regulation}")
    st.caption(f"Total: {len(subjects)} subjects")

    if subjects:
        for subj in subjects:
            status_color = "#56d364" if subj["is_active"] else "#f85149"
            status_text  = "Active" if subj["is_active"] else "Inactive"
            type_icon    = "📖" if subj["type"] == "theory" else "🔬"

            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([1.5, 3, 1, 1, 1, 1.5])
                with c1:
                    st.code(subj["code"])
                with c2:
                    st.markdown(f"{type_icon} **{subj['name']}**")
                with c3:
                    st.markdown(f"**{subj['hours_week']}** hrs/wk")
                with c4:
                    st.markdown(f"**{subj['credits']}** credits")
                with c5:
                    st.markdown(f"<span style='color:{status_color};font-weight:600'>{status_text}</span>",
                                unsafe_allow_html=True)
                with c6:
                    cols = st.columns(2)
                    with cols[0]:
                        if st.button("✏️", key=f"edit_{subj['id']}", help="Edit"):
                            st.session_state["edit_subject"] = subj
                    with cols[1]:
                        tog_label = "🔴" if subj["is_active"] else "🟢"
                        tog_help  = "Deactivate" if subj["is_active"] else "Activate"
                        if st.button(tog_label, key=f"tog_{subj['id']}", help=tog_help):
                            new_status = 0 if subj["is_active"] else 1
                            execute("UPDATE subjects SET is_active=? WHERE id=?",
                                    (new_status, subj["id"]))
                            st.success(f"Subject {'activated' if new_status else 'deactivated'}!")
                            st.rerun()
                st.divider()
    else:
        st.info("No subjects found for this filter. Add one below!")

    # ── EDIT FORM ─────────────────────────────────────────────
    if "edit_subject" in st.session_state:
        subj = st.session_state["edit_subject"]
        st.markdown("### ✏️ Edit Subject")
        with st.form("edit_form"):
            ec1, ec2 = st.columns(2)
            with ec1:
                new_name  = st.text_input("Subject Name", value=subj["name"])
                new_code  = st.text_input("Subject Code", value=subj["code"])
                new_type  = st.selectbox("Type", ["theory","lab"],
                                          index=0 if subj["type"]=="theory" else 1)
            with ec2:
                new_hrs   = st.number_input("Hours/Week", min_value=1, max_value=6,
                                             value=int(subj["hours_week"]))
                new_cred  = st.number_input("Credits", min_value=0.0, max_value=6.0,
                                             value=float(subj["credits"]), step=0.5)
                new_active = st.checkbox("Active", value=bool(subj["is_active"]))

            sc1, sc2 = st.columns(2)
            with sc1:
                save = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with sc2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if save:
            execute("""UPDATE subjects SET name=?,code=?,type=?,hours_week=?,credits=?,is_active=?
                       WHERE id=?""",
                    (new_name, new_code, new_type, new_hrs, new_cred,
                     1 if new_active else 0, subj["id"]))
            st.success("✅ Subject updated!")
            del st.session_state["edit_subject"]
            st.rerun()
        if cancel:
            del st.session_state["edit_subject"]
            st.rerun()

    # ── ADD NEW SUBJECT ───────────────────────────────────────
    st.markdown("---")
    st.markdown("### ➕ Add New Subject")

    with st.form("add_subject_form", clear_on_submit=True):
        a1, a2 = st.columns(2)
        with a1:
            new_code  = st.text_input("Subject Code*", placeholder="e.g. 23A05301")
            new_name  = st.text_input("Subject Name*", placeholder="e.g. Discrete Mathematics")
            new_type  = st.selectbox("Type*", ["theory", "lab"])
        with a2:
            new_hrs   = st.number_input("Hours/Week*", min_value=1, max_value=6, value=3)
            new_cred  = st.number_input("Credits*", min_value=0.0, max_value=6.0,
                                         value=3.0, step=0.5)

        submitted = st.form_submit_button("➕ Add Subject", use_container_width=True)

    if submitted:
        if not new_code or not new_name:
            st.error("Subject Code and Name are required!")
        else:
            try:
                execute("""INSERT INTO subjects
                           (code,name,dept_id,year,semester,regulation,type,hours_week,credits)
                           VALUES(?,?,?,?,?,?,?,?,?)""",
                        (new_code.strip(), new_name.strip(), filter_dept_id,
                         year, sem, regulation, new_type, new_hrs, new_cred))
                st.success(f"✅ Subject '{new_name}' added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e} (Code may already exist)")
