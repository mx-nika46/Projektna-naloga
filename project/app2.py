from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
from datetime import datetime

app = Flask(__name__, template_folder='templates2', static_folder="static2")
app.secret_key = 'tvoj_skrivni_kljuc_12345'

db = TinyDB('database.json')
users_table = db.table('users')
posts_table = db.table('posts')

User = Query()
Post = Query()

@app.route('/register2', methods=['GET', 'POST'])
def register2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_table.search(User.username == username):
            return "Uporabnik že obstaja!"
        
        users_table.insert({
            'username': username,
            'password': password
        })
        return redirect('/login2')
    
    return render_template('register2.html')

@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_table.search((User.username == username) & (User.password == password))
        
        if user:
            session['username'] = username
            return redirect('/objave')
        else:
            return "Napačno uporabniško ime ali geslo!"
    
    return render_template('login2.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login2')

@app.route('/objave')
def objave():
    if 'username' not in session:
        return redirect('/login2')
    
    vsi_posts = posts_table.all()
    vsi_posts.reverse()
    
    return render_template('objave.html', posts=vsi_posts, username=session['username'])

@app.route('/dodaj_objavo', methods=['POST'])
def dodaj_objavo():
    if 'username' not in session:
        return redirect('/login2')
    
    besedilo = request.form['besedilo']
    slika_url = request.form.get('slika_url', '')
    
    posts_table.insert({
        'avtor': session['username'],
        'besedilo': besedilo,
        'slika': slika_url,
        'datum': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    
    return redirect('/objave')

@app.route('/api/objave')
def api_objave():
    vsi_posts = posts_table.all()
    vsi_posts.reverse()
    return jsonify(vsi_posts)

@app.route('/api/izbrisi/<int:post_id>', methods=['DELETE'])
def izbrisi_objavo(post_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Nisi prijavljen'})
    
    post = posts_table.get(doc_id=post_id)
    
    if post and post['avtor'] == session['username']:
        posts_table.remove(doc_ids=[post_id])
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Nimate pravice za brisanje'})

@app.route('/')
def index():
    return redirect('/login2')

if __name__ == '__main__':
    app.run(debug=True)
