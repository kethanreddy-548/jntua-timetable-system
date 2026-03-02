"""
Manage Rooms — Admin Only
Assign classroom + lab room per branch per year per semester.
These rooms are used by the timetable generator.
"""
import streamlit as st
from database.db import fetchall, fetchone, execute
from auth.security import is_logged_in, current_role

BRANCHES_Y1   = ["CSE","CSE-SS","CSE-AIML","ECE","ECE-SS","CIVIL","MECH","EEE","CHEMICAL"]
BRANCHES_Y234 = ["CSE","ECE","CIVIL","MECH","EEE","CHEMICAL"]

def get_branches(year):
    return BRANCHES_Y1 if year == 1 else BRANCHES_Y234

def load_rooms(year, semester):
    rows = fetchall(
        "SELECT * FROM room_assignments WHERE year=? AND semester=? ORDER BY branch",
        (year, semester)
    )
    return {r["branch"]: r for r in rows}

def save_room(year, semester, branch, classroom, lab_room):
    existing = fetchone(
        "SELECT id FROM room_assignments WHERE year=? AND semester=? AND branch=?",
        (year, semester, branch)
    )
    if existing:
        execute("""UPDATE room_assignments
                   SET classroom=?, lab_room=?, updated_at=datetime('now')
                   WHERE year=? AND semester=? AND branch=?""",
                (classroom, lab_room, year, semester, branch))
    else:
        execute("""INSERT INTO room_assignments (year, semester, branch, classroom, lab_room)
                   VALUES (?,?,?,?,?)""",
                (year, semester, branch, classroom, lab_room))

def delete_room(year, semester, branch):
    execute("DELETE FROM room_assignments WHERE year=? AND semester=? AND branch=?",
            (year, semester, branch))


def show():
    # ── AUTH GUARD ────────────────────────────────────────────
    if not is_logged_in():
        st.warning("🔒 Please login to manage room assignments.")
        return

    st.markdown("## 🏛️ Manage Room Assignments")
    st.markdown("Assign a **permanent classroom** and **lab room** to each branch per year & semester. These rooms are automatically used during timetable generation.")
    st.markdown("---")

    # ── FILTERS ───────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Academic Year", [1, 2, 3, 4], key="rm_year")
    with col2:
        semester = st.selectbox("Semester", [1, 2], key="rm_sem")

    regulation = "R21" if year == 4 else "R23"
    branches   = get_branches(year)

    st.markdown(f"""
    <div style="background:#131929;border:1px solid rgba(99,102,241,0.2);border-radius:10px;
    padding:0.7rem 1rem;margin-bottom:1rem;font-size:0.85rem;color:#94a3b8">
    📋 Year {year} · Semester {semester} · <b style="color:#a5b4fc">{regulation} Regulation</b>
    · {len(branches)} branches
    </div>
    """, unsafe_allow_html=True)

    # ── LOAD EXISTING ─────────────────────────────────────────
    current_rooms = load_rooms(year, semester)

    # ── BULK DEFAULTS ─────────────────────────────────────────
    with st.expander("⚡ Auto-fill Defaults for All Branches"):
        st.markdown("Quickly generate room names. You can edit individually after.")
        d1, d2, d3 = st.columns(3)
        with d1:
            prefix_class = st.text_input("Classroom Prefix", value="R", key="rm_prefix_c")
            start_class  = st.number_input("Start Number", value=101, step=1, key="rm_start_c")
        with d2:
            prefix_lab  = st.text_input("Lab Prefix", value="LAB", key="rm_prefix_l")
            start_lab   = st.number_input("Start Number ", value=1, step=1, key="rm_start_l")
        with d3:
            st.markdown("")
            st.markdown("")
            if st.button("🔄 Apply Defaults to All", use_container_width=True):
                for i, b in enumerate(branches):
                    save_room(year, semester, b,
                              f"{prefix_class}{int(start_class)+i}",
                              f"{prefix_lab}{int(start_lab)+i}")
                st.success(f"✅ Defaults applied to all {len(branches)} branches!")
                st.rerun()

    st.markdown("### 📝 Branch Room Assignments")
    st.markdown("<small style='color:#475569'>Edit each branch individually and click Save.</small>",
                unsafe_allow_html=True)
    st.markdown("")

    # ── PER-BRANCH EDIT GRID ──────────────────────────────────
    # Show 2 branches per row
    for row_start in range(0, len(branches), 2):
        row_branches = branches[row_start:row_start+2]
        cols = st.columns(2)

        for col_idx, branch in enumerate(row_branches):
            existing = current_rooms.get(branch, {})
            default_class = existing.get("classroom", f"R{101 + branches.index(branch)}")
            default_lab   = existing.get("lab_room",  f"LAB{1 + branches.index(branch)}")
            has_assignment = bool(existing)

            with cols[col_idx]:
                # Card header
                status_color = "#059669" if has_assignment else "#dc2626"
                status_label = "✅ Assigned" if has_assignment else "⚠️ Not Set"
                st.markdown(f"""
                <div style="background:#131929;border:1px solid rgba(99,102,241,0.2);
                border-radius:12px;padding:1rem;margin-bottom:0.5rem">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                        <div style="font-weight:700;color:#e2e8f0;font-size:0.95rem">🏫 {branch}</div>
                        <div style="font-size:0.72rem;color:{status_color};font-weight:600">{status_label}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.form(f"room_form_{year}_{semester}_{branch}", clear_on_submit=False):
                    classroom = st.text_input(
                        "🏛️ Classroom",
                        value=default_class,
                        placeholder="e.g. R101, CS-101, Block-A Room 5",
                        key=f"class_{year}_{semester}_{branch}"
                    )
                    lab_room = st.text_input(
                        "🔬 Lab Room",
                        value=default_lab,
                        placeholder="e.g. LAB1, CS-Lab-2, Network Lab",
                        key=f"lab_{year}_{semester}_{branch}"
                    )

                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if not classroom.strip() or not lab_room.strip():
                                st.error("Both fields required!")
                            else:
                                save_room(year, semester, branch,
                                          classroom.strip(), lab_room.strip())
                                st.success("✅ Saved!")
                                st.rerun()
                    with bc2:
                        if has_assignment:
                            if st.form_submit_button("🗑️ Clear", use_container_width=True):
                                delete_room(year, semester, branch)
                                st.warning(f"Cleared {branch}")
                                st.rerun()

    st.markdown("---")

    # ── SUMMARY TABLE ─────────────────────────────────────────
    st.markdown("### 📊 Current Assignments Summary")

    if current_rooms:
        assigned   = [b for b in branches if b in current_rooms]
        unassigned = [b for b in branches if b not in current_rooms]

        # Stats
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Total Branches", len(branches))
        with s2:
            st.metric("✅ Assigned", len(assigned))
        with s3:
            st.metric("⚠️ Not Set", len(unassigned))

        if unassigned:
            st.warning(f"⚠️ These branches have no room assigned yet: **{', '.join(unassigned)}**. "
                       f"Timetable generation will use auto-assigned fallback rooms for them.")

        # Table
        rows_html = ""
        for b in branches:
            r = current_rooms.get(b)
            if r:
                rows_html += f"""
                <tr>
                    <td style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#e2e8f0;font-weight:600">{b}</td>
                    <td style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#a5b4fc">🏛️ {r['classroom']}</td>
                    <td style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#6ee7b7">🔬 {r['lab_room']}</td>
                    <td style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#475569;font-size:0.78rem">{r.get('updated_at','—')[:16]}</td>
                </tr>"""
            else:
                rows_html += f"""
                <tr>
                    <td style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#e2e8f0;font-weight:600">{b}</td>
                    <td colspan="3" style="padding:8px 12px;border:1px solid rgba(99,102,241,0.15);color:#dc2626;font-style:italic">Not assigned — fallback will be used</td>
                </tr>"""

        st.markdown(f"""
        <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;background:#0d1321;border-radius:10px;overflow:hidden">
            <thead>
                <tr style="background:linear-gradient(135deg,#1a1f4e,#1a3a2c)">
                    <th style="padding:10px 12px;border:1px solid rgba(99,102,241,0.2);color:#a5b4fc;text-align:left">Branch</th>
                    <th style="padding:10px 12px;border:1px solid rgba(99,102,241,0.2);color:#a5b4fc;text-align:left">Classroom</th>
                    <th style="padding:10px 12px;border:1px solid rgba(99,102,241,0.2);color:#a5b4fc;text-align:left">Lab Room</th>
                    <th style="padding:10px 12px;border:1px solid rgba(99,102,241,0.2);color:#a5b4fc;text-align:left">Last Updated</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No rooms assigned yet for this year and semester. Use the forms above or apply defaults.")

    st.markdown("---")
    st.markdown("""
    <div style="color:#475569;font-size:0.78rem">
    💡 <b>How rooms work:</b> Once assigned here, the timetable generator automatically places
    every theory class in the classroom and every lab session in the lab room for that branch.
    These rooms stay constant throughout the entire timetable — students never move classrooms.
    </div>
    """, unsafe_allow_html=True)