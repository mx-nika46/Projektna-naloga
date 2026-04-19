from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates3', static_folder="static3")
app.secret_key = 'izgubljene_zivali_secret_123'

DB_PATH = 'db/zivali.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS oglasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ime_zivali TEXT NOT NULL,
            vrsta TEXT NOT NULL,
            opis TEXT NOT NULL,
            lokacija TEXT NOT NULL,
            kontakt TEXT NOT NULL,
            slika_url TEXT,
            status TEXT DEFAULT 'izgubljena',
            datum TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



@app.route('/register3', methods=['GET', 'POST'])
def register3():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/login3')
        except sqlite3.IntegrityError:
            error = 'Uporabnik že obstaja!'
    return render_template('register3.html', error=error)

@app.route('/login3', methods=['GET', 'POST'])
def login3():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['user_id'] = user['id']
            return redirect('/')
        else:
            error = 'Napačno uporabniško ime ali geslo!'
    return render_template('login3.html', error=error)

@app.route('/logout3')
def logout3():
    session.clear()
    return redirect('/login3')



@app.route('/')
def index():
    vrsta = request.args.get('vrsta', '')
    status = request.args.get('status', '')
    iskanje = request.args.get('iskanje', '')

    conn = get_db()
    query = "SELECT oglasi.*, users.username FROM oglasi JOIN users ON oglasi.user_id = users.id WHERE 1=1"
    params = []

    if vrsta:
        query += " AND vrsta = ?"
        params.append(vrsta)
    if status:
        query += " AND status = ?"
        params.append(status)
    if iskanje:
        query += " AND (ime_zivali LIKE ? OR opis LIKE ? OR lokacija LIKE ?)"
        params.extend([f'%{iskanje}%', f'%{iskanje}%', f'%{iskanje}%'])

    query += " ORDER BY datum DESC"
    oglasi = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('index.html', oglasi=oglasi, vrsta=vrsta, status=status, iskanje=iskanje)

@app.route('/oglas/<int:oglas_id>')
def oglas(oglas_id):
    conn = get_db()
    o = conn.execute("SELECT oglasi.*, users.username FROM oglasi JOIN users ON oglasi.user_id = users.id WHERE oglasi.id = ?", (oglas_id,)).fetchone()
    conn.close()
    if not o:
        return "Oglas ne obstaja", 404
    return render_template('oglas.html', oglas=o)

@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj():
    if 'user_id' not in session:
        return redirect('/login3')
    if request.method == 'POST':
        conn = get_db()
        conn.execute("""
            INSERT INTO oglasi (user_id, ime_zivali, vrsta, opis, lokacija, kontakt, slika_url, datum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session['user_id'],
            request.form['ime_zivali'],
            request.form['vrsta'],
            request.form['opis'],
            request.form['lokacija'],
            request.form['kontakt'],
            request.form.get('slika_url', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M')
        ))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('dodaj.html')


@app.route('/api/najdena/<int:oglas_id>', methods=['POST'])
def oznaci_najdena(oglas_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Nisi prijavljen'})
    conn = get_db()
    oglas = conn.execute("SELECT * FROM oglasi WHERE id = ?", (oglas_id,)).fetchone()
    if not oglas:
        conn.close()
        return jsonify({'success': False, 'message': 'Oglas ne obstaja'})
    if oglas['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Nimate pravice'})
    conn.execute("UPDATE oglasi SET status = 'najdena' WHERE id = ?", (oglas_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/izbrisi_oglas/<int:oglas_id>', methods=['DELETE'])
def izbrisi_oglas(oglas_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Nisi prijavljen'})
    conn = get_db()
    oglas = conn.execute("SELECT * FROM oglasi WHERE id = ?", (oglas_id,)).fetchone()
    if not oglas or oglas['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Nimate pravice'})
    conn.execute("DELETE FROM oglasi WHERE id = ?", (oglas_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)