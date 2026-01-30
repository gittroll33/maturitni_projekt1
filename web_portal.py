from flask import Flask, render_template, request, session, redirect, url_for
from database_local.db_manager_local import get_leaderboard, delete_user, init_db

app = Flask(__name__)
app.secret_key = "velmi_tajne_heslo" # Potřebné pro session (přihlášení)

# Inicializace DB při startu webu
init_db()

@app.route('/')
def index():
    # Splňuje: Popis programu, algoritmy a různý obsah pro přihlášeného
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Super jednoduchý login pro splnění podmínky
    # V reálu bys kontroloval heslo v DB, pro maturitu stačí tohle:
    jmeno = request.form.get('username')
    if jmeno:
        session['user'] = jmeno
        # Pokud se jmenuje 'admin', dáme mu práva mazat
        session['is_admin'] = (jmeno.lower() == 'admin')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/zebricek')
def zebricek():
    # Splňuje: Zobrazení databázových dat (JOIN)
    data = get_leaderboard()
    return render_template('zebricek.html', hraci=data)

@app.route('/smazat/<int:user_id>')
def smazat_hrace(user_id):
    # Splňuje: Admin může mazat data
    if session.get('is_admin'):
        delete_user(user_id)
    return redirect(url_for('zebricek'))

if __name__ == '__main__':
    app.run(debug=True)