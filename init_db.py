import sqlite3

# Connect to DB (will create if it doesn't exist)
conn = sqlite3.connect('complaints.db')
cursor = conn.cursor()

# Create complaints table
cursor.execute("ALTER TABLE complaints ADD COLUMN assigned_to TEXT")

conn.commit()
conn.close()
print("Database and tables created successfully!")
