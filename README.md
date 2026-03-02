# 🎓 JNTUA CEA — Timetable Management System v3.0

A **production-ready**, AI-powered timetable generator built specifically for
**JNTUA College of Engineering Anantapur**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Secure Login** | bcrypt-level hashing, rate limiting (5 attempts → 15 min lockout), role-based access |
| **Roles** | Super Admin (full system), HOD (own department only) |
| **Regulations** | R23 for Year 1–3 · R21 for Year 4 (auto-applied) |
| **Subjects DB** | Pre-loaded with official JNTUA CEA R23/R21 subjects for all 6 branches |
| **Faculty DB** | Department-wise, max 3 theory classes/week per faculty |
| **Lab Rules** | 3 consecutive hours + 2 assistant faculty from same department |
| **AI Generation** | Groq LLaMA 3.3 70B — fast, free, conflict-free |
| **3 Views** | Section timetable · Faculty timetable · Room utilization |
| **Exports** | Color-coded PDF · CSV (Excel-ready) · JSON |
| **Future-proof** | Add/edit/remove subjects & faculty any time via UI |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env → paste your Groq API key
```

Get a **free** Groq API key at: https://console.groq.com

### 3. Run
```bash
streamlit run app.py
```

Open: http://localhost:8501

---

## 🔐 Default Login Credentials

> ⚠️ Change passwords immediately after first login!

| Role | Username | Default Password |
|---|---|---|
| Super Admin | `superadmin` | `Admin@JNTUA2024` |
| HOD CSE | `hod_cse` | `HOD_CSE@2024` |
| HOD ECE | `hod_ece` | `HOD_ECE@2024` |
| HOD EEE | `hod_eee` | `HOD_EEE@2024` |
| HOD Civil | `hod_civil` | `HOD_CIVIL@2024` |
| HOD Mech | `hod_mech` | `HOD_MECH@2024` |
| HOD Chemical | `hod_chem` | `HOD_CHEM@2024` |

---

## 📁 Project Structure

```
JNTUA_Timetable/
├── app.py                  ← Entry point (run this)
├── .env                    ← Your API keys (create from .env.example)
├── .env.example            ← Template
├── requirements.txt
├── jntua.db                ← Auto-created SQLite database
│
├── database/
│   ├── db.py               ← Connection, schema, helpers
│   └── seed_data.py        ← Official R23 & R21 subject data
│
├── auth/
│   └── security.py         ← Password hashing, sessions, rate limiting
│
└── pages/
    ├── login.py            ← Login screen
    ├── dashboard.py        ← Home dashboard
    ├── manage_subjects.py  ← Add/Edit/Delete subjects
    ├── manage_faculty.py   ← Add/Edit/Delete faculty
    └── generate.py         ← AI timetable generation + export
```

---

## 📚 Subject Database

### Auto-loaded on first run:
- **R23**: Year 1 Sem 1 & 2 (all branches), Year 2 & 3 Sem 1 (CSE, ECE, EEE, Civil, Mech, Chemical)
- **R21**: Year 4 Sem 1 (all branches) + Sem 2 (project/internship)

### Adding missing subjects:
1. Login as HOD or Super Admin
2. Go to **Manage Subjects**
3. Select Department → Year → Semester
4. Click **Add New Subject**

---

## 👨‍🏫 Faculty Rules

- Each faculty: **max 3 theory classes per week**
- **Lab sessions**: 1 primary + 2 assistants from same department
- Labs: **3 consecutive slots** (never split across lunch)
- Lunch (12:30–1:30): always free

---

## 🗓️ Timetable Rules (JNTUA CEA)

| | |
|---|---|
| Working days | Monday – Friday |
| Saturday | NCC/NSS/Sports/Clubs ONLY |
| Lunch | 12:30–1:30 (always free) |
| Max hrs/section/day | 6 |
| Year 1–3 regulation | R23 |
| Year 4 regulation | R21 |

---

## 🔧 Maintenance Guide

### Adding a new subject year:
- Go to Manage Subjects → select year/sem → Add Subject

### Updating faculty max workload:
- Go to Manage Faculty → click ✏️ → change "Max Theory Classes/Week"

### Resetting a user password:
- Super Admin can reset via the database directly, or add a reset feature
- Or use Change Password in the sidebar

### Backing up data:
```bash
cp jntua.db jntua_backup_$(date +%Y%m%d).db
```

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo, set `app.py` as entry point
4. Add Secrets: `GROQ_API_KEY = "your_key"` and `SECRET_KEY = "your_secret"`
5. Deploy!

---

## 📞 Support

Built for JNTUA CEA Hackathon · Contribute at college GitHub or contact the development team.
