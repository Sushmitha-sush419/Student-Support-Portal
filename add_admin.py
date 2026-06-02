import sqlite3
# This is the exact path we confirmed works
db_path = r"C:\Users\DELL\PycharmProjects\Student-Support-Portal\database.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# This adds the admin user to your existing database
try:
    cur.execute("INSERT INTO users (role, username, email, password) VALUES (?, ?, ?, ?)",
                ("Admin", "admin1", "admin1@gmail.com", "admin@123"))
    conn.commit()
    print("Admin user added successfully!")
except sqlite3.IntegrityError:
    print("Admin user already exists in the database.")
finally:
    conn.close()