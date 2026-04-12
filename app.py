import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
app = Flask(__name__)

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
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

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

if __name__ == '__main__':
    app.run(debug=True)