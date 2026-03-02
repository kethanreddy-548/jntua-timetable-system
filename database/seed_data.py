"""
Seed Data — JNTUA CEA Official Subjects
R23 Regulation: 1st, 2nd, 3rd Year
R21 Regulation: 4th Year
Source: jntuacea.ac.in/academics_syllabus.php
"""
from database.db import get_conn, fetchone, execute

DEPARTMENTS = [
    ("CSE",      "Computer Science & Engineering"),
    ("ECE",      "Electronics & Communication Engineering"),
    ("EEE",      "Electrical & Electronics Engineering"),
    ("CIVIL",    "Civil Engineering"),
    ("MECH",     "Mechanical Engineering"),
    ("CHEMICAL", "Chemical Engineering"),
    ("MATH",     "Mathematics"),
    ("PHYSICS",  "Physics"),
    ("CHEMISTRY","Chemistry"),
    ("ENGLISH",  "Humanities & Sciences"),
]

# ── R23 SUBJECTS (1st, 2nd, 3rd Year) ────────────────────────
# Format: (code, name, dept_code, year, semester, type, hours_week, credits)
R23_SUBJECTS = [

    # ═══ 1ST YEAR SEM 1 ══════════════════════════════════════
    ("23A15101", "Linear Algebra and Calculus",               "MATH",     1, 1, "theory", 3, 3.0),
    ("23A15201", "Applied Physics",                           "PHYSICS",  1, 1, "theory", 3, 3.0),
    ("23A15501", "Communicative English",                     "ENGLISH",  1, 1, "theory", 3, 3.0),
    ("23A05101", "Problem Solving & C Programming",           "CSE",      1, 1, "theory", 3, 3.0),
    ("23A10301", "Engineering Drawing",                       "MECH",     1, 1, "theory", 2, 2.0),
    ("23A10302", "Engineering Graphics Lab",                  "MECH",     1, 1, "lab",    3, 1.5),
    ("23A15202", "Applied Physics Lab",                       "PHYSICS",  1, 1, "lab",    3, 1.5),
    ("23A15502", "Communicative English Lab",                 "ENGLISH",  1, 1, "lab",    3, 1.5),
    ("23A05102", "C Programming Lab",                         "CSE",      1, 1, "lab",    3, 1.5),

    # ═══ 1ST YEAR SEM 2 ══════════════════════════════════════
    ("23A15102", "Differential Equations & Vector Calculus",  "MATH",     1, 2, "theory", 3, 3.0),
    ("23A15301", "Applied Chemistry",                         "CHEMISTRY",1, 2, "theory", 3, 3.0),
    ("23A10201", "Fundamentals of Electrical Engineering",    "EEE",      1, 2, "theory", 3, 3.0),
    ("23A10401", "Electronic Devices & Circuits",             "ECE",      1, 2, "theory", 3, 3.0),
    ("23A10508", "IT Workshop",                               "CSE",      1, 2, "lab",    3, 1.5),
    ("23A15304", "Chemistry Lab",                             "CHEMISTRY",1, 2, "lab",    3, 1.5),
    ("23A10202", "Electrical Engineering Lab",                "EEE",      1, 2, "lab",    3, 1.5),
    ("23A10303", "Engineering Workshop",                      "MECH",     1, 2, "lab",    3, 1.5),
    ("23A10803", "Environmental Science",                     "MATH",     1, 2, "theory", 3, 0.0),

    # ═══ 2ND YEAR CSE SEM 3 ══════════════════════════════════
    ("23A05301", "Discrete Mathematics & Graph Theory",       "CSE",      2, 1, "theory", 3, 3.0),
    ("23A04301", "Computer Organization & Architecture",      "CSE",      2, 1, "theory", 3, 3.0),
    ("23A05302", "Object Oriented Programming (Java)",        "CSE",      2, 1, "theory", 3, 3.0),
    ("23A05303", "Database Management Systems",               "CSE",      2, 1, "theory", 3, 3.0),
    ("23A39101", "Managerial Economics & Financial Analysis", "ENGLISH",  2, 1, "theory", 3, 3.0),
    ("23A05351", "OOP Lab (Java)",                            "CSE",      2, 1, "lab",    3, 1.5),
    ("23A05352", "DBMS Lab",                                  "CSE",      2, 1, "lab",    3, 1.5),
    ("23A05353", "Python Programming Lab",                    "CSE",      2, 1, "lab",    3, 2.0),

    # ═══ 2ND YEAR CSE SEM 4 ══════════════════════════════════
    ("23A35102", "Complex Variables & Transform Techniques",  "MATH",     2, 2, "theory", 3, 3.0),
    ("23A05401", "Operating Systems",                         "CSE",      2, 2, "theory", 3, 3.0),
    ("23A05402", "Software Engineering",                      "CSE",      2, 2, "theory", 3, 3.0),
    ("23A05403", "Computer Networks",                         "CSE",      2, 2, "theory", 3, 3.0),
    ("23A05404", "Design & Analysis of Algorithms",           "CSE",      2, 2, "theory", 3, 3.0),
    ("23A05451", "Operating Systems Lab",                     "CSE",      2, 2, "lab",    3, 1.5),
    ("23A05452", "Computer Networks Lab",                     "CSE",      2, 2, "lab",    3, 1.5),
    ("23A05453", "Algorithms Lab",                            "CSE",      2, 2, "lab",    3, 1.5),

    # ═══ 3RD YEAR CSE SEM 5 ══════════════════════════════════
    ("23A05501", "Machine Learning",                          "CSE",      3, 1, "theory", 3, 3.0),
    ("23A05502", "Compiler Design",                           "CSE",      3, 1, "theory", 3, 3.0),
    ("23A05503", "Information Security",                      "CSE",      3, 1, "theory", 3, 3.0),
    ("23A05504", "Cloud Computing",                           "CSE",      3, 1, "theory", 3, 3.0),
    ("23A05PE1", "Professional Elective I",                   "CSE",      3, 1, "theory", 3, 3.0),
    ("23A05551", "Machine Learning Lab",                      "CSE",      3, 1, "lab",    3, 1.5),
    ("23A05552", "Cloud Computing Lab",                       "CSE",      3, 1, "lab",    3, 1.5),
    ("23A05553", "Security Lab",                              "CSE",      3, 1, "lab",    3, 1.5),

    # ═══ 3RD YEAR CSE SEM 6 ══════════════════════════════════
    ("23A05601", "Deep Learning",                             "CSE",      3, 2, "theory", 3, 3.0),
    ("23A05602", "Big Data Analytics",                        "CSE",      3, 2, "theory", 3, 3.0),
    ("23A05603", "Internet of Things",                        "CSE",      3, 2, "theory", 3, 3.0),
    ("23A05604", "Full Stack Development",                    "CSE",      3, 2, "theory", 3, 3.0),
    ("23A05PE2", "Professional Elective II",                  "CSE",      3, 2, "theory", 3, 3.0),
    ("23A05651", "Deep Learning Lab",                         "CSE",      3, 2, "lab",    3, 1.5),
    ("23A05652", "Big Data Lab",                              "CSE",      3, 2, "lab",    3, 1.5),
    ("23A05653", "IoT Lab",                                   "CSE",      3, 2, "lab",    3, 1.5),

    # ═══ 2ND YEAR ECE ════════════════════════════════════════
    ("23A04351", "Electronic Circuit Analysis Lab",           "ECE",      2, 1, "lab",    3, 1.5),
    ("23A04352", "Signals & Systems Lab",                     "ECE",      2, 1, "lab",    3, 1.5),
    ("23A04353", "Digital Logic Design Lab",                  "ECE",      2, 1, "lab",    3, 1.5),
    ("23A04401", "Analog Electronics",                        "ECE",      2, 1, "theory", 3, 3.0),
    ("23A04402", "Signals & Systems",                         "ECE",      2, 1, "theory", 3, 3.0),
    ("23A04403", "Digital Logic Design",                      "ECE",      2, 1, "theory", 3, 3.0),
    ("23A04404", "Electromagnetic Theory",                    "ECE",      2, 1, "theory", 3, 3.0),

    # ═══ 2ND YEAR EEE ════════════════════════════════════════
    ("23A30201", "Electrical Circuit Analysis",               "EEE",      2, 1, "theory", 3, 3.0),
    ("23A30202", "DC Machines & Transformers",                "EEE",      2, 1, "theory", 3, 3.0),
    ("23A30404", "Digital Logic Design",                      "EEE",      2, 1, "theory", 3, 3.0),
    ("23A30203", "Electrical Circuit Analysis Lab",           "EEE",      2, 1, "lab",    3, 1.5),
    ("23A30204", "DC Machines & Transformers Lab",            "EEE",      2, 1, "lab",    3, 1.5),
    ("23A30205", "Python Programming Lab",                    "EEE",      2, 1, "lab",    3, 2.0),

    # ═══ 2ND YEAR CIVIL ══════════════════════════════════════
    ("23A01301", "Structural Analysis - I",                   "CIVIL",    2, 1, "theory", 3, 3.0),
    ("23A01302", "Building Materials & Construction",         "CIVIL",    2, 1, "theory", 3, 3.0),
    ("23A01303", "Fluid Mechanics",                           "CIVIL",    2, 1, "theory", 3, 3.0),
    ("23A01351", "Surveying Lab",                             "CIVIL",    2, 1, "lab",    3, 1.5),
    ("23A01352", "Fluid Mechanics Lab",                       "CIVIL",    2, 1, "lab",    3, 1.5),
    ("23A01353", "CAD Lab",                                   "CIVIL",    2, 1, "lab",    3, 2.0),

    # ═══ 2ND YEAR MECH ═══════════════════════════════════════
    ("23A03301", "Thermodynamics",                            "MECH",     2, 1, "theory", 3, 3.0),
    ("23A03302", "Strength of Materials",                     "MECH",     2, 1, "theory", 3, 3.0),
    ("23A03303", "Manufacturing Technology I",                "MECH",     2, 1, "theory", 3, 3.0),
    ("23A03351", "Thermodynamics Lab",                        "MECH",     2, 1, "lab",    3, 1.5),
    ("23A03352", "Manufacturing Technology Lab",              "MECH",     2, 1, "lab",    3, 1.5),
    ("23A03353", "Python Programming Lab",                    "MECH",     2, 1, "lab",    3, 2.0),

    # ═══ 2ND YEAR CHEMICAL ═══════════════════════════════════
    ("23A06301", "Chemical Engineering Thermodynamics",       "CHEMICAL", 2, 1, "theory", 3, 3.0),
    ("23A06302", "Fluid Mechanics & Mechanical Operations",   "CHEMICAL", 2, 1, "theory", 3, 3.0),
    ("23A06303", "Process Equipment Design I",                "CHEMICAL", 2, 1, "theory", 3, 3.0),
    ("23A06351", "Fluid Mechanics Lab",                       "CHEMICAL", 2, 1, "lab",    3, 1.5),
    ("23A06352", "Chemical Process Lab",                      "CHEMICAL", 2, 1, "lab",    3, 1.5),
    ("23A06353", "Python Programming Lab",                    "CHEMICAL", 2, 1, "lab",    3, 2.0),

    # ═══ 3RD YEAR ECE SEM 5 ══════════════════════════════════
    ("23A04501", "Analog Communications",                     "ECE",      3, 1, "theory", 3, 3.0),
    ("23A04502", "Microprocessors & Microcontrollers",        "ECE",      3, 1, "theory", 3, 3.0),
    ("23A04503", "VLSI Design",                               "ECE",      3, 1, "theory", 3, 3.0),
    ("23A04504", "Control Systems",                           "ECE",      3, 1, "theory", 3, 3.0),
    ("23A04PE1", "Professional Elective I",                   "ECE",      3, 1, "theory", 3, 3.0),
    ("23A04551", "Analog Communications Lab",                 "ECE",      3, 1, "lab",    3, 1.5),
    ("23A04552", "Microprocessors Lab",                       "ECE",      3, 1, "lab",    3, 1.5),
    ("23A04553", "VLSI Lab",                                  "ECE",      3, 1, "lab",    3, 1.5),

    # ═══ 3RD YEAR EEE SEM 5 ══════════════════════════════════
    ("23A50201", "Power System Architecture",                 "EEE",      3, 1, "theory", 3, 3.0),
    ("23A50202", "Control Systems",                           "EEE",      3, 1, "theory", 3, 3.0),
    ("23A50203", "Digital Computer Platforms",                "EEE",      3, 1, "theory", 3, 3.0),
    ("23A50204", "Embedded Systems",                          "EEE",      3, 1, "theory", 3, 3.0),
    ("23A50PE1", "Professional Elective I",                   "EEE",      3, 1, "theory", 3, 3.0),
    ("23A50206", "Control Systems Lab",                       "EEE",      3, 1, "lab",    3, 1.5),
    ("23A50207", "Digital Computer Platforms Lab",            "EEE",      3, 1, "lab",    3, 1.5),

    # ═══ 3RD YEAR CIVIL SEM 5 ════════════════════════════════
    ("23A01501", "Structural Analysis II",                    "CIVIL",    3, 1, "theory", 3, 3.0),
    ("23A01502", "Geotechnical Engineering",                  "CIVIL",    3, 1, "theory", 3, 3.0),
    ("23A01503", "Transportation Engineering",                "CIVIL",    3, 1, "theory", 3, 3.0),
    ("23A01504", "Environmental Engineering",                 "CIVIL",    3, 1, "theory", 3, 3.0),
    ("23A01PE1", "Professional Elective I",                   "CIVIL",    3, 1, "theory", 3, 3.0),
    ("23A01551", "Geotechnical Engineering Lab",              "CIVIL",    3, 1, "lab",    3, 1.5),
    ("23A01552", "Environmental Engineering Lab",             "CIVIL",    3, 1, "lab",    3, 1.5),

    # ═══ 3RD YEAR MECH SEM 5 ══════════════════════════════════
    ("23A03501", "Heat Transfer",                             "MECH",     3, 1, "theory", 3, 3.0),
    ("23A03502", "Machine Design I",                          "MECH",     3, 1, "theory", 3, 3.0),
    ("23A03503", "Dynamics of Machinery",                     "MECH",     3, 1, "theory", 3, 3.0),
    ("23A03504", "Manufacturing Technology II",               "MECH",     3, 1, "theory", 3, 3.0),
    ("23A03PE1", "Professional Elective I",                   "MECH",     3, 1, "theory", 3, 3.0),
    ("23A03551", "Heat Transfer Lab",                         "MECH",     3, 1, "lab",    3, 1.5),
    ("23A03552", "Machine Design Lab",                        "MECH",     3, 1, "lab",    3, 1.5),

    # ═══ 3RD YEAR CHEMICAL SEM 5 ═════════════════════════════
    ("23A06501", "Mass Transfer Operations I",                "CHEMICAL", 3, 1, "theory", 3, 3.0),
    ("23A06502", "Chemical Reaction Engineering",             "CHEMICAL", 3, 1, "theory", 3, 3.0),
    ("23A06503", "Heat Transfer Operations",                  "CHEMICAL", 3, 1, "theory", 3, 3.0),
    ("23A06504", "Process Dynamics & Control",                "CHEMICAL", 3, 1, "theory", 3, 3.0),
    ("23A06PE1", "Professional Elective I",                   "CHEMICAL", 3, 1, "theory", 3, 3.0),
    ("23A06551", "Mass Transfer Lab",                         "CHEMICAL", 3, 1, "lab",    3, 1.5),
    ("23A06552", "Chemical Reaction Engineering Lab",         "CHEMICAL", 3, 1, "lab",    3, 1.5),
]

# ── R21 SUBJECTS (4th Year) ───────────────────────────────────
R21_SUBJECTS = [
    # ═══ 4TH YEAR CSE SEM 7 ══════════════════════════════════
    ("21A05701", "Compiler Design",                           "CSE",      4, 1, "theory", 3, 3.0),
    ("21A05702", "Information Security",                      "CSE",      4, 1, "theory", 3, 3.0),
    ("21A05703", "Cloud Computing",                           "CSE",      4, 1, "theory", 3, 3.0),
    ("21A05PE3", "Professional Elective III",                 "CSE",      4, 1, "theory", 3, 3.0),
    ("21A05OE1", "Open Elective I",                           "CSE",      4, 1, "theory", 3, 3.0),
    ("21A05751", "Compiler Design Lab",                       "CSE",      4, 1, "lab",    3, 1.5),
    ("21A05752", "Cloud Computing Lab",                       "CSE",      4, 1, "lab",    3, 1.5),

    # ═══ 4TH YEAR CSE SEM 8 ══════════════════════════════════
    ("21A05801", "Project Work Phase II",                     "CSE",      4, 2, "lab",    6, 6.0),
    ("21A05802", "Industry Internship",                       "CSE",      4, 2, "lab",    6, 6.0),

    # ═══ 4TH YEAR ECE SEM 7 ══════════════════════════════════
    ("21A04701", "Digital Communications",                    "ECE",      4, 1, "theory", 3, 3.0),
    ("21A04702", "Embedded Systems",                          "ECE",      4, 1, "theory", 3, 3.0),
    ("21A04PE3", "Professional Elective III",                 "ECE",      4, 1, "theory", 3, 3.0),
    ("21A04OE1", "Open Elective I",                           "ECE",      4, 1, "theory", 3, 3.0),
    ("21A04751", "Digital Communications Lab",                "ECE",      4, 1, "lab",    3, 1.5),
    ("21A04752", "Embedded Systems Lab",                      "ECE",      4, 1, "lab",    3, 1.5),

    # ═══ 4TH YEAR EEE SEM 7 ══════════════════════════════════
    ("21A60201", "Power System Analysis",                     "EEE",      4, 1, "theory", 3, 3.0),
    ("21A60202", "Measurements & Sensors",                    "EEE",      4, 1, "theory", 3, 3.0),
    ("21A60203", "Digital Signal Processing",                 "EEE",      4, 1, "theory", 3, 3.0),
    ("21A60PE2", "Professional Elective II",                  "EEE",      4, 1, "theory", 3, 3.0),
    ("21A60206", "Power Systems Lab",                         "EEE",      4, 1, "lab",    3, 1.5),
    ("21A60207", "Measurements & Sensors Lab",                "EEE",      4, 1, "lab",    3, 1.5),

    # ═══ 4TH YEAR CIVIL SEM 7 ════════════════════════════════
    ("21A01701", "Design of Steel Structures",                "CIVIL",    4, 1, "theory", 3, 3.0),
    ("21A01702", "Prestressed Concrete",                      "CIVIL",    4, 1, "theory", 3, 3.0),
    ("21A01703", "Quantity Surveying & Valuation",            "CIVIL",    4, 1, "theory", 3, 3.0),
    ("21A01PE3", "Professional Elective III",                 "CIVIL",    4, 1, "theory", 3, 3.0),
    ("21A01751", "Structural Design Lab",                     "CIVIL",    4, 1, "lab",    3, 1.5),
    ("21A01752", "Project Work Phase I",                      "CIVIL",    4, 1, "lab",    4, 3.0),

    # ═══ 4TH YEAR MECH SEM 7 ══════════════════════════════════
    ("21A03701", "Finite Element Methods",                    "MECH",     4, 1, "theory", 3, 3.0),
    ("21A03702", "Computer Integrated Manufacturing",         "MECH",     4, 1, "theory", 3, 3.0),
    ("21A03PE3", "Professional Elective III",                 "MECH",     4, 1, "theory", 3, 3.0),
    ("21A03OE1", "Open Elective I",                           "MECH",     4, 1, "theory", 3, 3.0),
    ("21A03751", "FEM Lab",                                   "MECH",     4, 1, "lab",    3, 1.5),
    ("21A03752", "CIM Lab",                                   "MECH",     4, 1, "lab",    3, 1.5),

    # ═══ 4TH YEAR CHEMICAL SEM 7 ═════════════════════════════
    ("21A06701", "Mass Transfer Operations II",               "CHEMICAL", 4, 1, "theory", 3, 3.0),
    ("21A06702", "Plant Design & Economics",                  "CHEMICAL", 4, 1, "theory", 3, 3.0),
    ("21A06PE3", "Professional Elective III",                 "CHEMICAL", 4, 1, "theory", 3, 3.0),
    ("21A06OE1", "Open Elective I",                           "CHEMICAL", 4, 1, "theory", 3, 3.0),
    ("21A06751", "Mass Transfer Lab II",                      "CHEMICAL", 4, 1, "lab",    3, 1.5),
    ("21A06752", "Plant Design Lab",                          "CHEMICAL", 4, 1, "lab",    3, 1.5),
]

SAMPLE_FACULTY = [
    # (emp_id, name, designation, dept_code)
    ("CSE001", "Dr. Ramesh Kumar Sharma",      "Professor",         "CSE"),
    ("CSE002", "Dr. Priya Lakshmi Devi",       "Associate Professor","CSE"),
    ("CSE003", "Dr. Suresh Babu Naidu",        "Professor",         "CSE"),
    ("CSE004", "Prof. Anitha Reddy",           "Assistant Professor","CSE"),
    ("CSE005", "Prof. Venkata Rao Chandra",    "Assistant Professor","CSE"),
    ("CSE006", "Dr. Kavitha Sundaram",         "Associate Professor","CSE"),
    ("ECE001", "Dr. Srinivas Rao Patel",       "Professor",         "ECE"),
    ("ECE002", "Dr. Madhavi Latha Varma",      "Associate Professor","ECE"),
    ("ECE003", "Prof. Kiran Kumar Reddy",      "Assistant Professor","ECE"),
    ("ECE004", "Prof. Usha Rani Goud",         "Assistant Professor","ECE"),
    ("EEE001", "Dr. Narasimha Rao Yadav",      "Professor",         "EEE"),
    ("EEE002", "Dr. Saraswathi Devi Pillai",   "Associate Professor","EEE"),
    ("EEE003", "Prof. Ravi Shankar Murthy",    "Assistant Professor","EEE"),
    ("CIVIL001","Dr. Venkatesh Prasad Rao",    "Professor",         "CIVIL"),
    ("CIVIL002","Prof. Padmavathi Subramaniam","Associate Professor","CIVIL"),
    ("CIVIL003","Prof. Anil Kumar Verma",      "Assistant Professor","CIVIL"),
    ("MECH001", "Dr. Bhaskar Rao Krishnamurthy","Professor",        "MECH"),
    ("MECH002", "Prof. Lakshmi Prasad Nair",   "Associate Professor","MECH"),
    ("MECH003", "Prof. Sateesh Babu Goud",     "Assistant Professor","MECH"),
    ("CHEM001", "Dr. Vijaya Lakshmi Raju",     "Professor",         "CHEMICAL"),
    ("CHEM002", "Prof. Srikanth Rao Naidu",    "Associate Professor","CHEMICAL"),
    ("MATH001", "Dr. Srinivasa Murthy Rao",    "Professor",         "MATH"),
    ("MATH002", "Prof. Jyothi Devi Varma",     "Associate Professor","MATH"),
    ("PHY001",  "Dr. Chandrasekhar Rao",       "Professor",         "PHYSICS"),
    ("CHEM001B","Dr. Padma Rao Krishnan",      "Professor",         "CHEMISTRY"),
    ("ENG001",  "Prof. Meena Kumari Sharma",   "Associate Professor","ENGLISH"),
]


def seed_all():
    from auth.security import hash_password
    conn = get_conn()
    c = conn.cursor()

    # Departments
    dept_id_map = {}
    for code, name in DEPARTMENTS:
        c.execute("INSERT OR IGNORE INTO departments(code,name) VALUES(?,?)", (code, name))
    conn.commit()
    rows = c.execute("SELECT id, code FROM departments").fetchall()
    for row in rows:
        dept_id_map[row[1]] = row[0]

    # Super Admin
    admin_pwd = hash_password("Admin@JNTUA2024")
    c.execute("""INSERT OR IGNORE INTO users(username,password,role,full_name,email)
                 VALUES(?,?,?,?,?)""",
              ("superadmin", admin_pwd, "superadmin",
               "Super Administrator", "admin@jntuacea.ac.in"))

    # HOD accounts per dept
    hod_accounts = [
        ("hod_cse",  "CSE",      "HOD_CSE@2024",   "Dr. HOD CSE",      "hod.cse@jntuacea.ac.in"),
        ("hod_ece",  "ECE",      "HOD_ECE@2024",   "Dr. HOD ECE",      "hod.ece@jntuacea.ac.in"),
        ("hod_eee",  "EEE",      "HOD_EEE@2024",   "Dr. HOD EEE",      "hod.eee@jntuacea.ac.in"),
        ("hod_civil","CIVIL",    "HOD_CIVIL@2024", "Dr. HOD Civil",    "hod.civil@jntuacea.ac.in"),
        ("hod_mech", "MECH",     "HOD_MECH@2024",  "Dr. HOD Mech",     "hod.mech@jntuacea.ac.in"),
        ("hod_chem", "CHEMICAL", "HOD_CHEM@2024",  "Dr. HOD Chemical", "hod.chem@jntuacea.ac.in"),
    ]
    for uname, dept_code, pwd, fname, email in hod_accounts:
        hpwd = hash_password(pwd)
        dept_id = dept_id_map.get(dept_code)
        c.execute("""INSERT OR IGNORE INTO users(username,password,role,dept_id,full_name,email)
                     VALUES(?,?,?,?,?,?)""",
                  (uname, hpwd, "hod", dept_id, fname, email))

    # Faculty
    for emp_id, name, desig, dept_code in SAMPLE_FACULTY:
        dept_id = dept_id_map.get(dept_code)
        if dept_id:
            c.execute("""INSERT OR IGNORE INTO faculty(emp_id,name,designation,dept_id)
                         VALUES(?,?,?,?)""", (emp_id, name, desig, dept_id))

    # Subjects R23
    for s in R23_SUBJECTS:
        code, name, dept_code, year, sem, typ, hrs, credits = s
        dept_id = dept_id_map.get(dept_code)
        if dept_id:
            c.execute("""INSERT OR IGNORE INTO subjects
                         (code,name,dept_id,year,semester,regulation,type,hours_week,credits)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (code, name, dept_id, year, sem, "R23", typ, hrs, credits))

    # Subjects R21
    for s in R21_SUBJECTS:
        code, name, dept_code, year, sem, typ, hrs, credits = s
        dept_id = dept_id_map.get(dept_code)
        if dept_id:
            c.execute("""INSERT OR IGNORE INTO subjects
                         (code,name,dept_id,year,semester,regulation,type,hours_week,credits)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (code, name, dept_id, year, sem, "R21", typ, hrs, credits))

    conn.commit()
    conn.close()
    print("✅ Database seeded successfully!")
