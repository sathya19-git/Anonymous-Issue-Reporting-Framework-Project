Project Overview

This project is a Secure and Anonymous Issue Reporting System for Academic Institutions built using Flask and SQLite.

It allows students to:

Register & login
Submit complaints (with optional anonymity)
Track their complaints
Edit/Delete complaints

Admins can:

View all complaints
Assign complaints
Update complaint status
Delete complaints
Features:
Student Module
Student Registration & Login
Submit Complaint (Anonymous option available)
View My Complaints
Edit & Delete Complaints
Admin Module:
Admin Login
View All Complaints
Assign Complaints
Update Complaint Status
Delete Complaints
Tech Stack:
Backend: Flask (Python)
Frontend: HTML, CSS
Database: SQLite
Session Management: Flask Sessions
📂 Project Structure:
project/
│── app.py
│── database.py
│── complaints.db
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── complaint.html
│   ├── my_complaints.html
│   ├── edit_complaint.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_edit_status.html
│
└── static/
    ├── css/
    └── js/
⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/sathya19-git/Anonymous Issue Reporting Framework Project.git
cd Anonymous Issue reporting Framework Project
2️⃣ Install Dependencies
pip install flask
3️⃣ Run the Application
python app.py
4️⃣ Open in Browser
http://127.0.0.1:5000/
Admin Credentials:
Email: admin@college.com
Password: admin123
🧠 How It Works
Students register and login
Complaints are stored in SQLite database
Each complaint gets a unique ID (e.g., CMP123456)
Admin can manage complaints through dashboard


🔒 Security Features
Session-based authentication
Anonymous complaint option
Student-specific complaint access control
✨ Future Improvements
Password hashing (security enhancement)
Email notifications
File attachments for complaints
Role-based access control
Deployment (Render / AWS)
