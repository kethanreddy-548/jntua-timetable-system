"""Manage Faculty Page — Department-wise with workload limits"""
import streamlit as st
from database.db import fetchall, fetchone, execute
from auth.security import require_login, current_role, current_dept_id

def show():
    require_login()
    role    = current_role()
    dept_id = current_dept_id()

    st.markdown("## 👨‍🏫 Manage Faculty")
    st.markdown("Add, edit, or deactivate faculty members. Each faculty has **max 3 theory classes** per week.")
    st.markdown("---")

    # Department selection
    if role == "superadmin":
        depts = fetchall("SELECT id, code, name FROM departments ORDER BY code")
        dept_map = {f"{d['code']} — {d['name']}": d["id"] for d in depts}
        sel = st.selectbox("Select Department", list(dept_map.keys()))
        filter_dept_id = dept_map[sel]
        dept_info = fetchone("SELECT * FROM departments WHERE id=?", (filter_dept_id,))
    else:
        dept_info = fetchone("SELECT * FROM departments WHERE id=?", (dept_id,))
        filter_dept_id = dept_id
        st.info(f"Department: **{dept_info['name']}**")

    if not dept_info:
        st.error("Department not found")
        return

    # Faculty list
    faculty = fetchall("""
        SELECT f.*, d.code as dept_code, d.name as dept_name
        FROM faculty f JOIN departments d ON f.dept_id=d.id
        WHERE f.dept_id=?
        ORDER BY f.is_active DESC, f.designation, f.name
    """, (filter_dept_id,))

    # Stats
    active_count   = sum(1 for f in faculty if f["is_active"])
    inactive_count = len(faculty) - active_count

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;
        padding:1rem;text-align:center"><div style="font-size:1.8rem;font-weight:700;color:#00ff88">
        {len(faculty)}</div><div style="color:#8b949e;font-size:0.8rem">Total Faculty</div></div>""",
        unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;
        padding:1rem;text-align:center"><div style="font-size:1.8rem;font-weight:700;color:#56d364">
        {active_count}</div><div style="color:#8b949e;font-size:0.8rem">Active</div></div>""",
        unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;
        padding:1rem;text-align:center"><div style="font-size:1.8rem;font-weight:700;color:#f85149">
        {inactive_count}</div><div style="color:#8b949e;font-size:0.8rem">Inactive</div></div>""",
        unsafe_allow_html=True)

    st.markdown(f"### 👥 Faculty — {dept_info['code']}")

    if faculty:
        # Header
        hc = st.columns([0.8, 2.5, 1.5, 1, 1, 1, 1.2])
        for col, label in zip(hc, ["Emp ID", "Name", "Designation", "Theory Hrs", "Lab Hrs", "Status", "Actions"]):
            col.markdown(f"**{label}**")
        st.divider()

        for fac in faculty:
            status_color = "#56d364" if fac["is_active"] else "#6e7681"
            cols = st.columns([0.8, 2.5, 1.5, 1, 1, 1, 1.2])
            with cols[0]: st.code(fac["emp_id"])
            with cols[1]: st.markdown(f"**{fac['name']}**")
            with cols[2]: st.caption(fac["designation"] or "—")
            with cols[3]: st.markdown(f"**{fac['max_theory_hrs']}**/week")
            with cols[4]: st.markdown(f"**{fac['max_lab_hrs']}**/week")
            with cols[5]: st.markdown(f"<span style='color:{status_color};font-weight:600'>{'Active' if fac['is_active'] else 'Inactive'}</span>", unsafe_allow_html=True)
            with cols[6]:
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("✏️", key=f"fe_{fac['id']}", help="Edit"):
                        st.session_state["edit_faculty"] = fac
                with bc2:
                    lbl  = "🔴" if fac["is_active"] else "🟢"
                    help = "Deactivate" if fac["is_active"] else "Activate"
                    if st.button(lbl, key=f"ft_{fac['id']}", help=help):
                        execute("UPDATE faculty SET is_active=? WHERE id=?",
                                (0 if fac["is_active"] else 1, fac["id"]))
                        st.rerun()
            st.divider()
    else:
        st.info("No faculty found. Add faculty below.")

    # ── EDIT FORM ─────────────────────────────────────────────
    if "edit_faculty" in st.session_state:
        fac = st.session_state["edit_faculty"]
        st.markdown(f"### ✏️ Edit: {fac['name']}")
        with st.form("edit_fac_form"):
            ec1, ec2 = st.columns(2)
            with ec1:
                new_name  = st.text_input("Full Name", value=fac["name"])
                new_empid = st.text_input("Employee ID", value=fac["emp_id"])
                new_desig = st.selectbox("Designation",
                    ["Professor", "Associate Professor", "Assistant Professor", "Guest Faculty"],
                    index=["Professor","Associate Professor","Assistant Professor","Guest Faculty"].index(
                        fac["designation"]) if fac["designation"] in
                        ["Professor","Associate Professor","Assistant Professor","Guest Faculty"] else 2)
            with ec2:
                new_email = st.text_input("Email", value=fac["email"] or "")
                new_theory = st.number_input("Max Theory Classes/Week", min_value=1, max_value=6,
                                              value=int(fac["max_theory_hrs"]))
                new_lab   = st.number_input("Max Lab Hours/Week", min_value=3, max_value=12,
                                             value=int(fac["max_lab_hrs"]))
                new_active = st.checkbox("Active", value=bool(fac["is_active"]))

            fc1, fc2 = st.columns(2)
            with fc1:
                save   = st.form_submit_button("💾 Save", use_container_width=True)
            with fc2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if save:
            execute("""UPDATE faculty SET name=?,emp_id=?,designation=?,email=?,
                       max_theory_hrs=?,max_lab_hrs=?,is_active=? WHERE id=?""",
                    (new_name, new_empid, new_desig, new_email,
                     new_theory, new_lab, 1 if new_active else 0, fac["id"]))
            st.success("✅ Faculty updated!")
            del st.session_state["edit_faculty"]
            st.rerun()
        if cancel:
            del st.session_state["edit_faculty"]
            st.rerun()

    # ── ADD NEW FACULTY ───────────────────────────────────────
    st.markdown("---")
    st.markdown("### ➕ Add New Faculty")

    with st.form("add_fac_form", clear_on_submit=True):
        af1, af2 = st.columns(2)
        with af1:
            a_name  = st.text_input("Full Name*", placeholder="Dr. / Prof. Full Name")
            a_empid = st.text_input("Employee ID*", placeholder="e.g. CSE007")
            a_desig = st.selectbox("Designation*",
                ["Professor","Associate Professor","Assistant Professor","Guest Faculty"])
        with af2:
            a_email  = st.text_input("Email", placeholder="name@jntuacea.ac.in")
            a_theory = st.number_input("Max Theory Classes/Week", min_value=1, max_value=6, value=3)
            a_lab    = st.number_input("Max Lab Hours/Week", min_value=3, max_value=12, value=6)

        submitted = st.form_submit_button("➕ Add Faculty", use_container_width=True)

    if submitted:
        if not a_name or not a_empid:
            st.error("Name and Employee ID are required!")
        else:
            try:
                execute("""INSERT INTO faculty(emp_id,name,designation,dept_id,email,max_theory_hrs,max_lab_hrs)
                           VALUES(?,?,?,?,?,?,?)""",
                        (a_empid.strip(), a_name.strip(), a_desig,
                         filter_dept_id, a_email.strip(), a_theory, a_lab))
                st.success(f"✅ Faculty '{a_name}' added to {dept_info['code']}!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e} (Employee ID may already exist)")
