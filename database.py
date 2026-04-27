import sqlite3


# ---------- CONNECTION ----------
def get_connection():
    conn = sqlite3.connect('complaints.db')
    conn.row_factory = sqlite3.Row   # ⭐ Important for dictionary access
    return conn


# ---------- INITIAL DB SETUP ----------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            register_number TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_complaint_table():
    conn = get_connection()
    cur = conn.cursor()

    # Complaints table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            student_register TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT,
            anonymous INTEGER,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ---------- STUDENT FUNCTIONS ----------
def insert_student(name, email, password, register_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students (name, email, password, register_number) VALUES (?, ?, ?, ?)",
        (name, email, password, register_number)
    )

    conn.commit()
    conn.close()


def check_student_exists(email, register_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=? OR register_number=?",
        (email, register_number)
    )

    student = cur.fetchone()
    conn.close()
    return student


def check_student_login(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT register_number, name FROM students WHERE email=? AND password=?",
        (email, password)
    )

    student = cur.fetchone()
    conn.close()
    return student


# ---------- COMPLAINT FUNCTIONS ----------

def insert_complaint(complaint_id, student_register, title, description, severity, anonymous=False):
    conn = get_connection()
    cur = conn.cursor()

    if anonymous:
        student_register = "Anonymous"
        anonymous_value = 1
    else:
        anonymous_value = 0

    cur.execute("""
        INSERT INTO complaints 
        (id, student_register, title, description, severity, anonymous, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id,
        student_register,
        title,
        description,
        severity,
        anonymous_value,
        "Pending"
    ))

    conn.commit()
    conn.close()


def get_complaints_by_student(register_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, description, severity, status
        FROM complaints
        WHERE student_register = ?
        ORDER BY id DESC
    """, (register_number,))

    complaints = cur.fetchall()
    conn.close()
    return complaints

def get_complaint_by_id(complaint_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints WHERE id=?", (complaint_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "student_register": row[1],
            "title": row[2],
            "description": row[3],
            "severity": row[4],
            "anonymous": row[5],
            "status": row[6]
        }
    return None

def update_complaint(complaint_id, title, description, severity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE complaints SET title=?, description=?, severity=? WHERE id=?",
        (title, description, severity, complaint_id)
    )
    conn.commit()
    conn.close()

def remove_complaint(complaint_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id=?", (complaint_id,))
    conn.commit()
    conn.close()

# Get all complaints for admin
def get_all_complaints():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all complaints with student info
    cur.execute("""
        SELECT id, student_register, title, description, severity, status
        FROM complaints
        ORDER BY id DESC
    """)
    complaints = cur.fetchall()
    conn.close()

    # Convert each row to a dictionary for easier template rendering
    complaints_list = []
    for c in complaints:
        complaints_list.append({
            "id": c[0],
            "student_register": c[1],
            "title": c[2],
            "description": c[3],
            "severity": c[4],
            "status": c[5]
        })

    return complaints_list
