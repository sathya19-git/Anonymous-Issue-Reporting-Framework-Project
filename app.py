import sqlite3
from flask import url_for
from flask import Flask, render_template, request, redirect, flash, session
from database import get_connection, insert_student, check_student_exists, init_db, get_all_complaints, insert_complaint, get_complaints_by_student
import random

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

init_db()

# ----------------- Landing Page -----------------
@app.route('/')
def index():
    return render_template('index.html')


# ----------------- Student Registration -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        register_number = request.form['register_number']

        if check_student_exists(email, register_number):
            flash("Email or Register Number already exists!", "danger")
            return redirect('/register')

        insert_student(name, email, password, register_number)
        flash("Registration Successful! Please login.", "success")
        return redirect('/login')
    return render_template('register.html')


# ----------------- Student Login -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = check_student_exists(email, "")  # fetch by email
        if student and student[3] == password:  # student[3] is password
            session['student_register'] = student[4]  # store register_number
            session['student_name'] = student[1]  # store student name
            flash("Login Successful!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid Email or Password", "danger")
            return redirect('/login')

    return render_template('login.html')


# ----------------- Student Dashboard -----------------
@app.route('/dashboard')
def dashboard():
    if 'student_register' not in session:
        flash("Please login first", "warning")
        return redirect('/login')
    
    student_name = session.get('student_name')
    return render_template('dashboard.html', student_name=student_name)


# ----------------- Submit Complaint -----------------
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'student_register' not in session:
        flash("Please login first", "warning")
        return redirect('/login')

    complaint_id = None

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form['severity']
        anonymous = 'anonymous' in request.form

        complaint_id = "CMP" + str(random.randint(100000, 999999))
        insert_complaint(complaint_id, session['student_register'], title, description, severity, anonymous=anonymous)

        flash(f"Complaint Submitted! Your ID: {complaint_id}", "success")
        return redirect('/complaint')

    return render_template('complaint.html', complaint_id=complaint_id)


# ----------------- Logout -----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ----------------- View My Complaints -----------------
@app.route('/my_complaints')
def my_complaints():
    if 'student_register' not in session:
        return redirect('/login')

    complaints = get_complaints_by_student(session['student_register'])
    return render_template('my_complaints.html', complaints=complaints)


# ----------------- Edit Complaint -----------------
@app.route('/edit_complaint/<complaint_id>', methods=['GET', 'POST'])
def edit_complaint(complaint_id):
    if 'student_register' not in session:
        return redirect('/login')

    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form['severity']

        cur.execute("""
            UPDATE complaints 
            SET title=?, description=?, severity=?
            WHERE id=? AND student_register=?
        """, (title, description, severity, complaint_id, session['student_register']))

        conn.commit()
        conn.close()
        return redirect('/my_complaints')

    cur.execute("SELECT title, description, severity FROM complaints WHERE id=? AND student_register=?", 
                (complaint_id, session['student_register']))
    complaint = cur.fetchone()
    conn.close()

    if not complaint:
        return "Complaint not found", 404

    return render_template('edit_complaint.html', complaint=complaint, complaint_id=complaint_id)


# ----------------- Delete Complaint -----------------
@app.route('/delete_complaint/<complaint_id>')
def delete_complaint(complaint_id):
    if 'student_register' not in session:
        return redirect('/login')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id=? AND student_register=?", 
                (complaint_id, session['student_register']))
    conn.commit()
    conn.close()
    
    return redirect('/my_complaints')


# ----------------- Admin Login -----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "admin@college.com" and password == "admin123":
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return redirect('/admin_dashboard')
        else:
            error = "Invalid admin credentials!"

    return render_template('admin_login.html', error=error)


# ----------------- Admin Logout -----------------
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    return redirect('/admin_login')


# ----------------- Admin Dashboard -----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect('/admin_login')

    complaints = get_all_complaints()
    return render_template('admin_dashboard.html', complaints=complaints)

@app.route('/assign/<complaint_id>', methods=['POST'])
def assign_complaint(complaint_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    assigned_to = request.form['assigned_to']

    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    # Get complaint details
    cursor.execute("""
        SELECT title, description, severity, student_register
        FROM complaints
        WHERE id = ?
    """, (complaint_id,))
    
    complaint = cursor.fetchone()

    # Store values
    title = complaint[0]
    description = complaint[1]
    severity = complaint[2]
    student_register = complaint[3]
    

    # Update complaint
    cursor.execute("""
        UPDATE complaints
        SET assigned_to = ?, status = 'Assigned'
        WHERE id = ?
    """, (assigned_to, complaint_id))

    conn.commit()
    conn.close()

@app.route('/admin_delete/<complaint_id>')
def admin_delete(complaint_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()

    flash("Complaint deleted successfully!", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_edit_status/<complaint_id>', methods=['GET', 'POST'])
def admin_edit_status(complaint_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        status = request.form['status']

        cursor.execute("""
            UPDATE complaints
            SET status = ?
            WHERE id = ?
        """, (status, complaint_id))

        conn.commit()
        conn.close()

        flash("Status updated successfully!", "info")
        return redirect(url_for('admin_dashboard'))

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    complaint = cursor.fetchone()
    conn.close()

    return render_template('admin_edit_status.html', complaint=complaint)



if __name__ == "__main__":
    app.run(debug=True)
