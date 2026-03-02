"""
Timetable Generation Page
- PUBLIC ACCESS — no login required
- API key loaded silently from backend (.env) — never shown to user
- Rooms loaded from admin-managed room_assignments table
- Falls back to auto-assignment if admin has not set rooms yet
"""
import streamlit as st
import json, re, io
import pandas as pd
from groq import Groq
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from database.db import fetchall, fetchone, execute
import os

GROQ_KEY      = os.environ.get("GROQ_API_KEY", "")
TIME_SLOTS    = ["9:30-10:30","10:30-11:30","11:30-12:30","12:30-1:30","1:30-2:30","2:30-3:30","3:30-4:30"]
DAYS          = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
BRANCHES_Y1   = ["CSE","CSE-SS","CSE-AIML","ECE","ECE-SS","CIVIL","MECH","EEE","CHEMICAL"]
BRANCHES_Y234 = ["CSE","ECE","CIVIL","MECH","EEE","CHEMICAL"]
BRANCH_TO_DEPT = {
    "CSE":"CSE","CSE-SS":"CSE","CSE-AIML":"CSE",
    "ECE":"ECE","ECE-SS":"ECE","EEE":"EEE",
    "CIVIL":"CIVIL","MECH":"MECH","CHEMICAL":"CHEMICAL"
}


def get_subjects_for(branch, year, semester):
    dept_code  = BRANCH_TO_DEPT.get(branch, branch)
    regulation = "R21" if year == 4 else "R23"
    dept = fetchone("SELECT id FROM departments WHERE code=?", (dept_code,))
    if not dept:
        return []
    return fetchall("""
        SELECT s.*, d.code as dept_code FROM subjects s
        JOIN departments d ON s.dept_id=d.id
        WHERE s.dept_id=? AND s.year=? AND s.semester=? AND s.regulation=? AND s.is_active=1
        ORDER BY s.type, s.name
    """, (dept["id"], year, semester, regulation))


def get_faculty_for_dept(dept_code):
    dept = fetchone("SELECT id FROM departments WHERE code=?", (dept_code,))
    if not dept:
        return []
    return fetchall("""
        SELECT * FROM faculty WHERE dept_id=? AND is_active=1
        ORDER BY designation, name
    """, (dept["id"],))


def get_room_map(year, semester, branches):
    db_rooms  = fetchall(
        "SELECT * FROM room_assignments WHERE year=? AND semester=?",
        (year, semester)
    )
    db_map       = {r["branch"]: r for r in db_rooms}
    room_map     = {}
    fallback_used = []
    for i, branch in enumerate(branches):
        if branch in db_map:
            room_map[branch] = {
                "classroom": db_map[branch]["classroom"],
                "lab":       db_map[branch]["lab_room"],
                "source":    "admin",
            }
        else:
            room_map[branch] = {
                "classroom": f"R{101 + i}",
                "lab":       f"LAB{1 + i}",
                "source":    "fallback",
            }
            fallback_used.append(branch)
    return room_map, fallback_used


def enforce_rooms(result, room_map):
    for branch, branch_tt in result.get("timetable", {}).items():
        assigned  = room_map.get(branch, {})
        classroom = assigned.get("classroom", "R101")
        lab_room  = assigned.get("lab", "LAB1")
        for day, slots in branch_tt.items():
            for slot, cell in slots.items():
                if isinstance(cell, dict):
                    if cell.get("type") == "theory":
                        cell["room"] = classroom
                    elif cell.get("type") == "lab":
                        cell["room"] = lab_room
    result["room_assignments"] = {
        b: {"classroom": v["classroom"], "lab": v["lab"]}
        for b, v in room_map.items()
    }
    return result


def build_prompt(year, semester, branches, room_map, subjects_map, faculty_map):
    regulation = "R21" if year == 4 else "R23"
    room_str   = "\n".join(
        f"  {b}: classroom={v['classroom']}, lab={v['lab']}"
        for b, v in room_map.items()
    )
    ex_branch = branches[0]
    ex_class  = room_map[ex_branch]["classroom"]
    ex_lab    = room_map[ex_branch]["lab"]

    subjects_json = {
        b: [{"name": s["name"], "code": s["code"], "type": s["type"], "hours": s["hours_week"]}
            for s in subjects_map.get(b, [])]
        for b in branches
    }
    faculty_json = {
        dept: [{"name": f["name"], "designation": f["designation"],
                "max_theory": f["max_theory_hrs"], "emp_id": f["emp_id"]}
               for f in fac_list]
        for dept, fac_list in faculty_map.items()
    }

    branches_str = ", ".join(branches)
    subj_str     = json.dumps(subjects_json, indent=2)
    fac_str_json = json.dumps(faculty_json, indent=2)
    reg_num      = regulation[1:]

    prompt = (
        "You are an expert timetable scheduler for JNTUA College of Engineering Anantapur.\n\n"
        f"Generate a COMPLETE conflict-free weekly timetable for Year {year}, Semester {semester} ({regulation} Regulation).\n\n"
        "=== JNTUA CEA RULES ===\n"
        "Working Days: Monday-Friday (classes) + Saturday (activities only)\n"
        "Saturday: NCC/NSS/Sports/Clubs ONLY - NO theory or lab classes\n"
        "Time Slots:\n"
        "  9:30-10:30 | 10:30-11:30 | 11:30-12:30\n"
        "  12:30-1:30 -> LUNCH (always free)\n"
        "  1:30-2:30  | 2:30-3:30   | 3:30-4:30\n\n"
        "=== FIXED ROOM ASSIGNMENTS - NEVER CHANGE THESE ===\n"
        "Each branch has ONE permanent classroom (all theory) and ONE lab room (all labs).\n"
        "Students stay in their room all week - only faculty moves.\n"
        f"{room_str}\n\n"
        "=== LAB RULES ===\n"
        "- Labs = 3 CONSECUTIVE slots ONLY (9:30-12:30 OR 1:30-4:30)\n"
        "- NEVER split a lab across lunch\n"
        "- Primary faculty + 2 ADDITIONAL from SAME department for every lab slot\n"
        "- All 3 faculty names in every lab slot\n\n"
        "=== FACULTY RULES ===\n"
        "- MAX 3 theory classes per faculty per week\n"
        "- No faculty clash (same time, two sections)\n"
        "- Faculty must match subject department\n\n"
        "=== HARD CONSTRAINTS ===\n"
        "1. No faculty clash\n"
        "2. No room clash\n"
        "3. No section clash\n"
        "4. Labs = 3 consecutive only\n"
        "5. Lunch 12:30-1:30 always free\n"
        "6. Saturday = activities only\n"
        "7. Max 6 teaching hours per section per day\n"
        "8. Each branch classroom is FIXED all week\n"
        "9. Each branch lab room is FIXED all week\n\n"
        f"=== BRANCHES & SUBJECTS (R{reg_num}) ===\n"
        f"{subj_str}\n\n"
        "=== AVAILABLE FACULTY BY DEPARTMENT ===\n"
        f"{fac_str_json}\n\n"
        "=== OUTPUT - Return ONLY valid JSON, no markdown, no explanation ===\n"
        "{\n"
        f'  "year": {year}, "semester": {semester}, "regulation": "{regulation}",\n'
        '  "timetable": {\n'
        f'    "{ex_branch}": {{\n'
        '      "Monday": {\n'
        f'        "9:30-10:30":  {{"subject":"Name","code":"CODE","faculty":["Dr. X"],"room":"{ex_class}","type":"theory"}},\n'
        f'        "10:30-11:30": {{"subject":"Name","code":"CODE","faculty":["Dr. X"],"room":"{ex_class}","type":"theory"}},\n'
        f'        "11:30-12:30": {{"subject":"Name","code":"CODE","faculty":["Dr. X"],"room":"{ex_class}","type":"theory"}},\n'
        '        "12:30-1:30":  {"subject":"LUNCH","code":"","faculty":[],"room":"","type":"lunch"},\n'
        f'        "1:30-2:30":   {{"subject":"Lab","code":"CODE","faculty":["Dr. P","Dr. A1","Dr. A2"],"room":"{ex_lab}","type":"lab"}},\n'
        f'        "2:30-3:30":   {{"subject":"Lab","code":"CODE","faculty":["Dr. P","Dr. A1","Dr. A2"],"room":"{ex_lab}","type":"lab"}},\n'
        f'        "3:30-4:30":   {{"subject":"Lab","code":"CODE","faculty":["Dr. P","Dr. A1","Dr. A2"],"room":"{ex_lab}","type":"lab"}}\n'
        "      },\n"
        '      "Tuesday":{}, "Wednesday":{}, "Thursday":{}, "Friday":{},\n'
        '      "Saturday": {\n'
        '        "9:30-10:30":{"subject":"NCC/NSS","code":"","faculty":["Activity Incharge"],"room":"Grounds","type":"activity"},\n'
        '        "10:30-11:30":{"subject":"Sports","code":"","faculty":["Activity Incharge"],"room":"Grounds","type":"activity"},\n'
        '        "11:30-12:30":{"subject":"Club Activity","code":"","faculty":["Activity Incharge"],"room":"Seminar Hall","type":"activity"},\n'
        '        "12:30-1:30":{"subject":"LUNCH","code":"","faculty":[],"room":"","type":"lunch"},\n'
        '        "1:30-2:30":{"subject":"NSS/NCC","code":"","faculty":["Activity Incharge"],"room":"Grounds","type":"activity"},\n'
        '        "2:30-3:30":{"subject":"FREE","code":"","faculty":[],"room":"","type":"free"},\n'
        '        "3:30-4:30":{"subject":"FREE","code":"","faculty":[],"room":"","type":"free"}\n'
        "      }\n"
        "    }\n"
        "  },\n"
        '  "faculty_timetable": {\n'
        f'    "Dr. X": {{"Monday":["9:30-10:30: {ex_branch} - Subject - {ex_class}"],"Tuesday":[],"Wednesday":[],"Thursday":[],"Friday":[],"Saturday":[]}}\n'
        "  },\n"
        '  "room_timetable": {\n'
        f'    "{ex_class}": {{"Monday":["9:30-10:30: {ex_branch} - Subject - Dr. X"],"Tuesday":[]}}\n'
        "  },\n"
        '  "conflicts": [], "warnings": [],\n'
        '  "stats": {"theory_hrs_per_branch":{},"lab_hrs_per_branch":{},"faculty_load":{}}\n'
        "}\n\n"
        f"Generate for ALL branches: {branches_str}\n"
        "STRICT: Every theory slot MUST use the assigned classroom. Every lab slot MUST use the assigned lab.\n"
        "RETURN ONLY THE JSON."
    )
    return prompt


def render_tt(tt, branch):
    bt   = tt.get(branch, {})
    html = '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.76rem"><tr>'
    html += '<th style="background:linear-gradient(135deg,#1a3a5c,#1e5f3f);color:white;padding:8px;border:1px solid #30363d;min-width:80px">Time</th>'
    for d in DAYS:
        html += f'<th style="background:linear-gradient(135deg,#1a3a5c,#1e5f3f);color:white;padding:8px;border:1px solid #30363d">{d}</th>'
    html += '</tr>'
    bg = {"theory":"#0d2818","lab":"#2d1515","lunch":"#272115","activity":"#0d2626","free":"#0d1117"}
    fg = {"theory":"#56d364","lab":"#f85149","lunch":"#e3b341","activity":"#39d0d8","free":"#30363d"}
    for slot in TIME_SLOTS:
        html += f'<tr><td style="background:#161b22;color:#58a6ff;padding:6px;font-weight:600;border:1px solid #30363d;white-space:nowrap;font-size:0.72rem">{slot}</td>'
        for day in DAYS:
            cell = bt.get(day, {}).get(slot, {})
            typ  = cell.get("type","free")
            subj = cell.get("subject","FREE")
            facs = cell.get("faculty",[])
            room = cell.get("room","")
            code = cell.get("code","")
            cbg  = bg.get(typ, bg["free"])
            cfg  = fg.get(typ, fg["free"])
            if typ == "lunch":
                html += f'<td style="background:{cbg};color:{cfg};padding:6px;border:1px solid #30363d;text-align:center;font-weight:600">🍽️ LUNCH</td>'
            elif typ in ("theory","lab"):
                fac_str  = "<br>".join(f"<small style='font-size:0.65rem'>{f}</small>" for f in facs[:3])
                icon     = "📖" if typ=="theory" else "🔬"
                code_str = f"<br><small style='color:#8b949e;font-size:0.65rem'>{code}</small>" if code else ""
                html += f'<td style="background:{cbg};color:{cfg};padding:5px;border:1px solid #30363d;text-align:center">{icon} <b style="font-size:0.73rem">{subj}</b>{code_str}<br>{fac_str}<br><small style="color:#8b949e;font-size:0.65rem">🏛️ {room}</small></td>'
            elif typ == "activity":
                html += f'<td style="background:{cbg};color:{cfg};padding:5px;border:1px solid #30363d;text-align:center"><b style="font-size:0.73rem">{subj}</b><br><small style="font-size:0.65rem">🎯 {room}</small></td>'
            else:
                html += f'<td style="background:{cbg};color:{cfg};padding:5px;border:1px solid #30363d;text-align:center">—</td>'
        html += '</tr>'
    html += '</table></div>'
    return html


def generate_pdf(result):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            leftMargin=0.35*inch, rightMargin=0.35*inch,
                            topMargin=0.35*inch, bottomMargin=0.35*inch)
    styles = getSampleStyleSheet()
    ts = ParagraphStyle('T', parent=styles['Title'],    fontSize=14, textColor=colors.HexColor('#00d4ff'), alignment=TA_CENTER)
    ss = ParagraphStyle('S', parent=styles['Normal'],   fontSize=7,  textColor=colors.HexColor('#666666'), alignment=TA_CENTER)
    hs = ParagraphStyle('H', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1e5f3f'), alignment=TA_LEFT)
    story = [
        Paragraph("JNTUA CEA — Timetable Management System", ts),
        Paragraph(f"Year {result.get('year')} · Semester {result.get('semester')} · {result.get('regulation')} Regulation", ss),
        Spacer(1, 0.12*inch)
    ]
    hdr = colors.HexColor('#1a3a5c')
    color_map = {
        "theory":   colors.HexColor('#e8f5e9'),
        "lab":      colors.HexColor('#fce4e4'),
        "lunch":    colors.HexColor('#fff8e1'),
        "activity": colors.HexColor('#e3f2fd'),
        "free":     colors.HexColor('#fafafa'),
    }
    for branch, branch_tt in result.get("timetable",{}).items():
        story.append(Paragraph(f"Branch: {branch}", hs))
        data = [["Time"] + DAYS]
        for slot in TIME_SLOTS:
            row = [slot]
            for day in DAYS:
                cell = branch_tt.get(day,{}).get(slot,{})
                typ  = cell.get("type","free")
                subj = cell.get("subject","FREE")
                facs = cell.get("faculty",[])
                room = cell.get("room","")
                if typ == "lunch":      row.append("LUNCH")
                elif typ == "free":     row.append("—")
                elif typ == "activity": row.append(f"{subj}\n{room}")
                else:                   row.append(f"{subj}\n{chr(10).join(facs[:3])}\n{room}")
            data.append(row)
        t    = Table(data, colWidths=[0.8*inch]+[0.88*inch]*6)
        cmds = [
            ('BACKGROUND',(0,0),(-1,0),hdr),('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),6.5),
            ('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,1),(-1,-1),5.5),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0),(-1,-1),0.4,colors.grey),('ROWHEIGHT',(0,0),(-1,-1),38),
            ('BACKGROUND',(0,1),(0,-1),colors.HexColor('#e8eaf6')),
            ('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
        ]
        for ri, slot in enumerate(TIME_SLOTS,1):
            for ci, day in enumerate(DAYS,1):
                typ = branch_tt.get(day,{}).get(slot,{}).get("type","free")
                cmds.append(('BACKGROUND',(ci,ri),(ci,ri),color_map.get(typ,color_map["free"])))
        t.setStyle(TableStyle(cmds))
        story += [t, Spacer(1,0.08*inch), PageBreak()]
    doc.build(story)
    buf.seek(0)
    return buf


def show():
    st.markdown("## 🗓️ Generate Timetable")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        year = st.selectbox("Academic Year", [1,2,3,4])
    with c2:
        semester = st.selectbox("Semester", [1,2])
    with c3:
        branches_list     = BRANCHES_Y1 if year == 1 else BRANCHES_Y234
        selected_branches = st.multiselect("Branches", branches_list, default=branches_list[:3])
    with c4:
        regulation = "R21" if year == 4 else "R23"
        st.metric("Regulation", regulation)

    if not selected_branches:
        st.warning("Please select at least one branch.")
        return

    # Load rooms from DB
    room_map, fallback_used = get_room_map(year, semester, selected_branches)

    with st.expander("🏛️ Room Assignments (set by Admin)"):
        if fallback_used:
            st.warning(
                "⚠️ **" + ", ".join(fallback_used) + "** have no admin-assigned rooms — "
                "using auto-fallback. Ask admin to set rooms in **Manage Rooms**."
            )
        rows_html = ""
        for b in selected_branches:
            r      = room_map[b]
            source = "🏛️ Admin" if r["source"] == "admin" else "⚙️ Auto"
            rows_html += (
                "<tr>"
                f"<td style='padding:6px 10px;color:#e2e8f0;font-weight:600'>{b}</td>"
                f"<td style='padding:6px 10px;color:#a5b4fc'>{r['classroom']}</td>"
                f"<td style='padding:6px 10px;color:#6ee7b7'>{r['lab']}</td>"
                f"<td style='padding:6px 10px;color:#475569;font-size:0.75rem'>{source}</td>"
                "</tr>"
            )
        table_html = (
            '<table style="width:100%;border-collapse:collapse;font-size:0.83rem;background:#0d1321">' +
            '<tr style="background:#1a1f4e">' +
            '<th style="padding:8px 10px;color:#a5b4fc;text-align:left">Branch</th>' +
            '<th style="padding:8px 10px;color:#a5b4fc;text-align:left">Classroom</th>' +
            '<th style="padding:8px 10px;color:#a5b4fc;text-align:left">Lab Room</th>' +
            '<th style="padding:8px 10px;color:#a5b4fc;text-align:left">Source</th>' +
            '</tr>' + rows_html + '</table>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

    # Subjects & Faculty
    subjects_map      = {}
    faculty_map       = {}
    dept_codes_needed = set()
    for b in selected_branches:
        subjects_map[b] = get_subjects_for(b, year, semester)
        dept_codes_needed.add(BRANCH_TO_DEPT.get(b, b))
    for dc in dept_codes_needed:
        faculty_map[dc] = get_faculty_for_dept(dc)

    with st.expander("📚 Subjects & Faculty Preview"):
        for b in selected_branches:
            subjs  = subjects_map[b]
            dc     = BRANCH_TO_DEPT.get(b, b)
            fac    = faculty_map.get(dc, [])
            theory = [s for s in subjs if s["type"]=="theory"]
            lab    = [s for s in subjs if s["type"]=="lab"]
            st.markdown(f"**{b}** — {len(theory)} theory · {len(lab)} labs · {len(fac)} faculty")
            if not subjs:
                st.warning(f"No subjects for {b} Y{year} S{semester} ({regulation}). Add in Manage Subjects.")
            ec1, ec2 = st.columns(2)
            with ec1:
                for s in theory:
                    st.markdown(f"📖 `{s['code']}` {s['name']} ({s['hours_week']}h)")
            with ec2:
                for s in lab:
                    st.markdown(f"🔬 `{s['code']}` {s['name']} ({s['hours_week']}h)")
            st.markdown("---")

    missing = [b for b in selected_branches if not subjects_map.get(b)]
    if missing:
        st.error(f"No subjects for: {', '.join(missing)}. Add in Manage Subjects first.")
        return

    # API key — backend only
    if not GROQ_KEY:
        st.error("Groq API key not configured. Ask admin to add GROQ_API_KEY to the .env file.")
        return

    _, mc, _ = st.columns([1,2,1])
    with mc:
        gen = st.button("🚀 Generate AI Timetable", use_container_width=True)

    if gen:
        prog = st.progress(0)
        stat = st.empty()
        try:
            stat.text("🔑 Verifying API connection...")
            prog.progress(10)
            client = Groq(api_key=GROQ_KEY)
            prompt = build_prompt(year, semester, selected_branches,
                                  room_map, subjects_map, faculty_map)

            stat.text("📡 Sending to Groq LLaMA 3.3 70B...")
            prog.progress(25)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":prompt}],
                max_tokens=8192,
                temperature=0.2,
            )
            prog.progress(75)
            stat.text("🔄 Parsing timetable...")

            raw = response.choices[0].message.content
            raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
            raw = re.sub(r'\s*```$', '', raw.strip())
            m   = re.search(r'\{.*\}', raw, re.DOTALL)
            result = json.loads(m.group() if m else raw)

            result = enforce_rooms(result, room_map)

            prog.progress(90)
            stat.text("💾 Saving to database...")

            st.session_state["tt_result"]   = result
            st.session_state["tt_year"]     = year
            st.session_state["tt_semester"] = semester
            st.session_state["tt_branches"] = selected_branches

            execute("DELETE FROM timetable_slots WHERE year=? AND semester=?", (year, semester))
            for branch, branch_tt in result.get("timetable",{}).items():
                for day, day_slots in branch_tt.items():
                    for slot, cell in day_slots.items():
                        execute("""INSERT INTO timetable_slots
                                   (branch,year,semester,regulation,day,time_slot,room,slot_type)
                                   VALUES(?,?,?,?,?,?,?,?)""",
                                (branch,year,semester,regulation,day,slot,
                                 cell.get("room",""),cell.get("type","free")))

            prog.progress(100)
            prog.empty(); stat.empty()
            st.success("✅ Timetable generated and saved!")

        except json.JSONDecodeError:
            prog.empty(); stat.empty()
            st.error("❌ AI returned invalid JSON. Please try again.")
        except Exception as e:
            prog.empty(); stat.empty()
            err = str(e)
            if "401" in err or "invalid_api_key" in err.lower():
                st.error("❌ Invalid Groq API key. Ask admin to update the .env file.")
            elif "rate" in err.lower():
                st.error("❌ Rate limit hit. Please wait a moment and try again.")
            else:
                st.error(f"❌ Error: {e}")

    if "tt_result" not in st.session_state:
        return

    result   = st.session_state["tt_result"]
    branches = st.session_state["tt_branches"]
    yr       = st.session_state["tt_year"]
    sem      = st.session_state["tt_semester"]

    timetable  = result.get("timetable", {})
    faculty_tt = result.get("faculty_timetable", {})
    room_tt    = result.get("room_timetable", {})
    conflicts  = result.get("conflicts", [])

    if not conflicts:
        st.markdown(
            '<div style="background:#0d2818;border:1px solid #56d364;border-radius:8px;' +
            f'padding:0.8rem 1rem;margin:0.5rem 0">✅ <b>Zero Conflicts!</b> — ' +
            f'{len(timetable)} sections · Year {yr} Sem {sem}</div>',
            unsafe_allow_html=True)
    else:
        for c in conflicts:
            st.warning(c)

    st.markdown("")
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Section","👨\u200d🏫 Faculty","🏢 Room","📥 Export"])

    with tab1:
        if timetable:
            btabs = st.tabs(list(timetable.keys()))
            for i, (b, _) in enumerate(timetable.items()):
                with btabs[i]:
                    st.markdown(render_tt(timetable, b), unsafe_allow_html=True)
                    st.markdown("📖 Theory &nbsp;&nbsp; 🔬 Lab (3hrs+2 assistants) &nbsp;&nbsp; 🍽️ Lunch &nbsp;&nbsp; 🎯 Activity")

    with tab2:
        if faculty_tt:
            th_style = 'style="background:linear-gradient(135deg,#1a3a5c,#1e5f3f);color:white;padding:8px;border:1px solid #30363d"'
            hdrs = "".join(f"<th {th_style}>{d}</th>" for d in DAYS)
            rows = ""
            for fac, sched in faculty_tt.items():
                total = sum(len(v) for v in sched.values())
                rows += f'<tr><td style="color:#58a6ff;padding:6px;font-weight:600;border:1px solid #30363d">{fac}</td>'
                for day in DAYS:
                    slots   = sched.get(day, [])
                    content = "<br>".join(f"<small>{s}</small>" for s in slots) if slots else "—"
                    rbg = "#0d2818" if slots else "#0d1117"
                    rfg = "#56d364" if slots else "#30363d"
                    rows += f'<td style="background:{rbg};color:{rfg};padding:5px;border:1px solid #30363d">{content}</td>'
                rows += f'<td style="color:#e3b341;padding:6px;text-align:center;font-weight:700;border:1px solid #30363d">{total}</td></tr>'
            st.markdown(
                '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.76rem">' +
                f'<tr><th {th_style}>Faculty</th>{hdrs}<th {th_style}>Total</th></tr>' +
                rows + '</table></div>',
                unsafe_allow_html=True)

    with tab3:
        if room_tt:
            th_style = 'style="background:linear-gradient(135deg,#1a3a5c,#1e5f3f);color:white;padding:8px;border:1px solid #30363d"'
            hdrs = "".join(f"<th {th_style}>{d}</th>" for d in DAYS)
            rows = ""
            for room, sched in room_tt.items():
                total = sum(len(v) for v in sched.values())
                rows += f'<tr><td style="color:#58a6ff;padding:6px;font-weight:600;border:1px solid #30363d">{room}</td>'
                for day in DAYS:
                    slots   = sched.get(day, [])
                    content = "<br>".join(f"<small>{s}</small>" for s in slots) if slots else "—"
                    rbg = "#2d1515" if slots else "#0d1117"
                    rfg = "#f85149" if slots else "#30363d"
                    rows += f'<td style="background:{rbg};color:{rfg};padding:5px;border:1px solid #30363d">{content}</td>'
                rows += f'<td style="color:#e3b341;padding:6px;text-align:center;font-weight:700;border:1px solid #30363d">{total}</td></tr>'
            st.markdown(
                '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.76rem">' +
                f'<tr><th {th_style}>Room</th>{hdrs}<th {th_style}>Sessions</th></tr>' +
                rows + '</table></div>',
                unsafe_allow_html=True)

    with tab4:
        st.markdown("### 📥 Export Options")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            st.markdown("**📄 PDF Report**")
            if st.button("Generate PDF", use_container_width=True):
                with st.spinner("Building PDF..."):
                    try:
                        pdf_buf = generate_pdf(result)
                        st.download_button("⬇️ Download PDF", data=pdf_buf,
                            file_name=f"JNTUA_Y{yr}_S{sem}.pdf",
                            mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"PDF error: {e}")
        with ec2:
            st.markdown("**📦 JSON**")
            st.download_button("⬇️ Download JSON",
                data=json.dumps(result, indent=2),
                file_name=f"JNTUA_Y{yr}_S{sem}.json",
                mime="application/json", use_container_width=True)
        with ec3:
            st.markdown("**📊 CSV**")
            csv_rows = []
            for b, btt in timetable.items():
                for day, dslots in btt.items():
                    for slot, cell in dslots.items():
                        facs = cell.get("faculty", [])
                        csv_rows.append({
                            "Branch": b, "Day": day, "Time": slot,
                            "Subject": cell.get("subject",""), "Code": cell.get("code",""),
                            "Primary Faculty": facs[0] if facs else "",
                            "Lab Asst 1": facs[1] if len(facs)>1 else "",
                            "Lab Asst 2": facs[2] if len(facs)>2 else "",
                            "Room": cell.get("room",""), "Type": cell.get("type",""),
                        })
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                st.download_button("⬇️ Download CSV",
                    data=df.to_csv(index=False),
                    file_name=f"JNTUA_Y{yr}_S{sem}.csv",
                    mime="text/csv", use_container_width=True)