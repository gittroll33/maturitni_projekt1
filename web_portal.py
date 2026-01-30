from flask import Flask, render_template, request, session, redirect, url_for
import os
import sys

# Zajistíme, aby Python viděl složku database_local
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_local.db_manager_local import get_leaderboard, delete_user, init_db

app = Flask(__name__)
app.secret_key = "velmi_tajne_heslo" 

# Inicializace DB při startu webu (vytvoří tabulky, pokud nejsou)
init_db()

@app.route('/')
def index():
    # Předáme session do šablony, aby web věděl, jestli je někdo přihlášen
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    jmeno = request.form.get('username')
    if jmeno:
        session['user'] = jmeno
        # Admin práva pro jméno 'admin'
        session['is_admin'] = (jmeno.lower() == 'admin')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/zebricek')
def zebricek():
    # get_leaderboard teď vrací (jméno, skóre, id)
    data = get_leaderboard()
    return render_template('zebricek.html', hraci=data)

@app.route('/smazat/<int:user_id>')
def smazat_hrace(user_id):
    # Jen přihlášený admin může mazat
    if session.get('is_admin'):
        delete_user(user_id)
        print(f"DEBUG: Admin smazal uživatele {user_id}")
    return redirect(url_for('zebricek'))

if __name__ == '__main__':
    # debug=True je super při vývoji, automaticky restartuje server po změně kódu
    app.run(debug=True, port=5000)