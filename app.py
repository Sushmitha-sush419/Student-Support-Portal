from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import os
import sqlite3

# ... rest of your code ...
app = Flask(__name__)
app.secret_key = 'student_support_portal'

# 2. Configure it SECOND
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# Replace with your actual email credentials
app.config['MAIL_USERNAME'] = 'poojithaa275@gmail.com'
app.config['MAIL_PASSWORD'] = 'nerieuvcmkvwuyvp'

# 3. Initialize extensions THIRD
mail = Mail(app)

# 4. Now define your routes/database paths...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            description TEXT,
            location TEXT,
            contact TEXT,
            image TEXT
        )
    
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            description TEXT,
            location TEXT,
            contact TEXT,
            image TEXT
        )
    ''')
    cur.execute('''
         CREATE TABLE IF NOT EXISTS doubts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0
         )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doubt_id INTEGER,
            username TEXT,
            type TEXT,
            UNIQUE(doubt_id, username)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doubt_id INTEGER,
            username TEXT,
            stars INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reported_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doubt_id INTEGER,
            username TEXT,
            reason TEXT,
            UNIQUE(doubt_id, username)
        )
    ''')
    # USERS TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    # COMPLAINT TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS complaint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ctype TEXT,
            issue TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # FEEDBACK TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ftype TEXT,
            dept TEXT,
            class TEXT,
            issue TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/home')
def home():
    if 'username' not in session: # This checks if the user is logged in
        return redirect('/')      # If not, it kicks them back to the login page
    return render_template('home.html', role=session.get('role'))

@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        item = request.form['item']
        desc = request.form['description']
        loc = request.form['location']
        contact = request.form['contact']
        file = request.files['image']

        filename = ""
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO lost_items (item_name, description, location, contact,image) VALUES (?, ?, ?, ?, ?)",
            (item, desc, loc, contact, filename)
        )
        conn.commit()
        conn.close()

        return "Item submitted successfully ✅"

    return render_template('lost.html')
@app.route('/view', methods=['GET', 'POST'])
def view():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    searched= False
    search=" "
    data = []
    no_result = False


    if request.method == 'POST':

        search = request.form.get('search','').strip()
        if search:
            searched =True
            cur.execute("SELECT * FROM lost_items WHERE LOWER(item_name) LIKE LOWER(?)",
        ('%' + search + '%',))

            data = cur.fetchall()
            if len(data) == 0:
                no_result = True
    conn.close()

    return render_template('view.html', items=data, search=search,searched = searched, no_result = no_result)

@app.route('/all_items')
def all_items():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Lost items
    cur.execute("SELECT * FROM lost_items")
    lost_items = cur.fetchall()

    # Found items
    cur.execute("SELECT * FROM found_items")
    found_items = cur.fetchall()

    conn.close()

    return render_template(
        'all_items.html',
        lost_items=lost_items,
        found_items=found_items
    )
@app.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        item = request.form['item']
        desc = request.form['description']
        loc = request.form['location']
        contact = request.form['contact']
        file = request.files['image']

        import os

        UPLOAD_FOLDER = 'static/uploads'

        file = request.files['image']

        if file and file.filename != "":
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
        else:
            filename = ""

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO found_items (item_name, description, location, contact, image) VALUES (?, ?, ?, ?, ?)",
            (item, desc, loc, contact, filename)
        )

        conn.commit()
        print("Inserted:",item, desc, loc, contact, filename)

        conn.close()

        return redirect('view_found')

    return render_template('found.html')
@app.route('/view_found')
def view_found():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM found_items")

    data = cur.fetchall()
    conn.close()



    return render_template('view_found.html', items=data)


# ---------------- MAIN DOUBT ROUTE ----------------
@app.route("/doubts")
def doubts():
    role = session.get("role")
    if not role:
        return redirect("/")

    search_query = request.args.get("search", "").lower()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if search_query:
        cursor.execute(
                "SELECT * FROM doubts WHERE lower(question) LIKE ? OR lower(answer) LIKE ? ORDER BY id DESC",
                (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute(
                "SELECT * FROM doubts ORDER BY id DESC"
        )

    raw_questions = cursor.fetchall()

    questions = []

    for q in raw_questions:
        qid = q[0]

        cursor.execute(
                "SELECT COUNT(*) FROM reactions WHERE doubt_id=? AND type='like'",
                (qid,)
        )
        likes = cursor.fetchone()[0]

        cursor.execute(
                "SELECT COUNT(*) FROM reactions WHERE doubt_id=? AND type='dislike'",
                (qid,)
        )
        dislikes = cursor.fetchone()[0]

        cursor.execute(
                "SELECT AVG(stars) FROM ratings WHERE doubt_id=?",
                (qid,)
        )
        avg = cursor.fetchone()[0]
        avg = round(avg, 1) if avg else 0

        questions.append(
                (q[0], q[1], q[2], likes, dislikes, avg)
        )
    conn.close()


    return render_template(
    "doubts.html",
    questions=questions,
    role=role,
    search_query=search_query
)


@app.route('/unanswered')
def unanswered_questions():
    # Ensure only teachers/admins can access
    if session.get('role') not in ['lecturer', 'admin']:
        return "Unauthorized", 403

    # Assuming 'db' is your database connection
    # Fetch questions where answer column is empty/null
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM doubts WHERE answer IS NULL OR answer = ''")
    questions = cursor.fetchall()

    return render_template('unanswered.html', questions=questions, role=session.get('role'))

@app.route("/add_question", methods=["POST"])
def add_question():
    if session.get("role") != "student":
        return redirect("/doubts")

    q = request.form.get("question")
    if q and q.strip():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO doubts (question, answer, likes, dislikes, rating) VALUES (?, '', 0, 0, 0)",
            (q,)
        )
        conn.commit()
        conn.close()

    return redirect("/doubts")

@app.route("/answer/<int:qid>", methods=["POST"])
def answer(qid):
    if session.get("role") not in ["lecturer", "admin"]:
        return redirect("/doubts")

    ans = request.form.get("answer")
    if ans and ans.strip():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE doubts SET answer = ? WHERE id = ?", (ans, qid))
        conn.commit()
        conn.close()

    return redirect("/doubts")

@app.route("/like/<int:qid>")
def like(qid):
    if session.get("role") == "student":
        user = session.get("username")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reactions (doubt_id, username, type)
            VALUES (?, ?, 'like')
            ON CONFLICT(doubt_id, username)
            DO UPDATE SET type='like'
        """, (qid, user))

        conn.commit()
        conn.close()

    return redirect("/doubts")

@app.route("/dislike/<int:qid>")
def dislike(qid):
    if session.get("role") == "student":
        user = session.get("username")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reactions (doubt_id, username, type)
            VALUES (?, ?, 'dislike')
            ON CONFLICT(doubt_id, username)
            DO UPDATE SET type='dislike'
        """, (qid, user))

        conn.commit()
        conn.close()

    return redirect("/doubts")

@app.route("/rate/<int:qid>/<int:stars>")
def rate(qid, stars):
    if session.get("role") == "student":
        user = session.get("username")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ratings WHERE doubt_id=? AND username=?", (qid, user))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE ratings SET stars=? WHERE doubt_id=? AND username=?", (stars, qid, user))
        else:
            cursor.execute("INSERT INTO ratings (doubt_id, username, stars) VALUES (?, ?, ?)", (qid, user, stars))

        conn.commit()
        conn.close()

    return redirect("/doubts")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/report/<int:qid>", methods=["GET","POST"])
def report(qid):

    if session.get("role") not in ["student", "teacher"]:
        return redirect("/doubts")

    if request.method == "POST":

        reason = request.form["reason"]
        user = session.get("username")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO reported_questions
                (doubt_id, username, reason)
                VALUES (?, ?, ?)
            """, (qid, user, reason))

            conn.commit()

        except:
            pass

        conn.close()

        return redirect("/doubts")

    return render_template("report.html", qid=qid)

@app.route("/view_reports")
def view_reports():

    if session.get("role") != "admin":
        return redirect("/doubts")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT doubts.id,
           doubts.question,
           COUNT(reported_questions.id) as report_count,
           GROUP_CONCAT(reported_questions.reason, ', ')
    FROM reported_questions
    JOIN doubts
    ON reported_questions.doubt_id = doubts.id
    GROUP BY doubts.id, doubts.question
    """)

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "view_reports.html",
        reports=reports
    )
@app.route("/delete_question/<int:qid>")
def delete_question(qid):

    if session.get("role") != "admin":
        return redirect("/doubts")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM doubts WHERE id=?",
        (qid,)
    )

    conn.commit()
    conn.close()
    return redirect("/doubts")

# ================= SIGNUP =================

@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():

    role = request.form['role']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users(role, username, email, password)
            VALUES (?, ?, ?, ?)
        """, (role, username, email, password))

        conn.commit()

    except:
        return "Username or Email already exists ⚠️"

    conn.close()

    return redirect('/')


# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/')

    role = session.get("role")

    return render_template(
        'home.html',
        role=role
    )

# ================= COMPLAINT PAGE =================

@app.route('/complaint')
def complaint():
    return render_template('complaint.html')


# ================= SUBMIT COMPLAINT =================
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    complaint_type = request.form.get('ctype')
    issue = request.form.get('issue_title')
    description = request.form.get('description')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Note: We skip 'id', 'status', and 'created_at' because
    # they are handled automatically by AUTOINCREMENT and DEFAULT
    cur.execute("""
        INSERT INTO complaint (ctype, issue, description)
        VALUES (?, ?, ?)
    """, (complaint_type, issue, description))

    conn.commit()
    conn.close()
    return redirect('/complaint')

# ================= SUBMIT FEEDBACK =================
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback_for = request.form.get('ftype')
    department = request.form.get('dept')
    student_class = request.form.get('class')
    issue = request.form.get('issue_title')
    description = request.form.get('description')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO feedback (ftype, dept, class, issue, description)
        VALUES (?, ?, ?, ?, ?)
    """, (feedback_for, department, student_class, issue, description))

    conn.commit()
    conn.close()
    return redirect('/complaint') # Redirecting back to the main portal

# ================= ADMIN COMPLAINTS =================

@app.route('/admin/complaints')
def admin_complaints():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaint")

    data = cur.fetchall()

    conn.close()

    return render_template(
        'admin_complaint.html',
        complaints=data
    )


@app.route('/resolve_complaint/<int:id>')
def resolve_complaint(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE complaint
        SET status='Resolved'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/admin/complaints')


# ================= ADMIN FEEDBACK =================

@app.route('/admin/feedback')
def admin_feedback():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM feedback")

    data = cur.fetchall()

    conn.close()

    return render_template(
        'admin_feedback.html',
        feedbacks=data
    )


@app.route('/resolve_feedback/<int:id>')
def resolve_feedback(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE feedback
        SET status='Resolved'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/admin/feedback')

@app.route("/chatbot")
def chatbot_page():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    reply = ask_ai(msg)
    return jsonify({"reply": reply})

@app.route('/study')
def study():
    return render_template('study.html')


# STEP 1
@app.route('/study/<material_type>')
def level(material_type):

    courses = ["BCA", "BSC", "BVOC"]

    return render_template(
        'level.html',
        material_type=material_type,
        courses=courses
    )


# STEP 2
@app.route('/subjects/<material_type>/<course>/<semester>')
def subjects(material_type, course, semester):

    subject_map = {
        "BCA": ["DBMS", "DSA", "Python", "OS"],
        "BSC": ["Maths", "Physics", "Chemistry"],
        "BVOC": ["Communication", "Web Tech"]
    }

    subjects = subject_map.get(course, [])

    return render_template(
        'subjects.html',
        material_type=material_type,
        course=course,
        value=semester,
        subjects=subjects
    )


# STEP 3
@app.route('/materials/<material_type>/<course>/<value>/<subject>', methods=['GET', 'POST'])
def materials(material_type, course, value, subject):

    folder = os.path.join(
        "static/uploads",
        material_type,
        course,
        value,
        subject
    )

    os.makedirs(folder, exist_ok=True)

    if request.method == 'POST':

        file = request.files['file']

        if file and file.filename != "":
            file.save(os.path.join(folder, file.filename))

        return redirect(request.url)

    files = os.listdir(folder)

    return render_template(
        'materials.html',
        material_type=material_type,
        course=course,
        value=value,
        subject=subject,
        files=files
    )

@app.route('/download/<material_type>/<course>/<value>/<subject>/<filename>')
def download(material_type, course, value, subject, filename):

    folder = f"static/uploads/{material_type}/{course}/{value}/{subject}"

    return send_from_directory(folder, filename, as_attachment=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

@app.route('/delete_file/<material_type>/<course>/<value>/<subject>/<filename>')
def delete_file(material_type, course, value, subject, filename):

    role = session.get("role")

    if role not in ["admin", "lecturer"]:
        return "Unauthorized ❌", 403

    file_path = os.path.join(
        "static/uploads",
        material_type,
        course,
        value,
        subject,
        filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(request.referrer)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_email = request.form.get('email')

        # Connect to DB to check if the email is registered
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (user_email,))
        user = cur.fetchone()
        conn.close()

        if user:
            try:
                # This is the actual sending part
                msg = Message("Password Reset Request",
                              sender="poojithaa275@gmail.com",
                              recipients=[user_email])
                msg.body = "Use this link to reset your password: http://127.0.0.1:5000/new-password"
                mail.send(msg)
                flash("Reset link sent! Please check your email.")
            except Exception as e:
                flash(f"Error: {e}")
        else:
            flash("If that email is registered, a link has been sent.")

        return redirect(url_for('login_page'))

    return render_template('forgot_password.html')


@app.route('/')
def login_page():
    return render_template('login.html')


# Ensure your 'login' route logic matches this exactly
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    # Find the user AND their role
    cur.execute("SELECT username, role FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session['username'] = user[0]
        session['role'] = user[1] # This is the crucial part!
        return redirect('/home')
    else:
        flash("Invalid username or password!")
        return redirect('/')


@app.route('/new-password', methods=['GET', 'POST'])
def new_password():
    if request.method == 'POST':
        new_pass = request.form.get('password')
        email = request.form.get('email')

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        # Update the password
        cur.execute("UPDATE users SET password = ? WHERE email = ?", (new_pass, email))

        # Fetch the user details to log them in automatically
        cur.execute("SELECT username, role FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.commit()
        conn.close()

        if user:
            # Set the session so the user is "logged in"
            session['username'] = user[0]
            session['role'] = user[1]
            flash("Password updated! You are now logged in.")
            return redirect(url_for('login_page'))  # Redirects to home.html

    return render_template('new_password.html')

if __name__ == "__main__":
    init_db()
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"Endpoint: {rule.endpoint} -> Route: {rule.rule}")
    app.run(debug=True)


