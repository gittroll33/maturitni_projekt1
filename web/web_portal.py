# app/web_portal.py
from flask import Flask, render_template, request, session, redirect, url_for
import sys
import os

# --- LOGIKA PRO CESTY A IMPORTY ---
# 1. Získáme absolutní cestu ke složce, kde leží tento soubor (web)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Získáme cestu o úroveň výš (kořen projektu maturitni_projekt1)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# 3. Přidáme kořen projektu do sys.path, aby Python viděl složku 'database_local'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 4. Definujeme přesnou cestu ke složce s obrázky
# Tímto opravujeme problém s načítáním obrázků
IMG_FOLDER = os.path.join(BASE_DIR, 'imgs')

# Importy z tvé databázové vrstvy
try:
    from database_local.db_manager_local import get_leaderboard, delete_user, save_game_result
except ImportError as e:
    print(f"Chyba: Nepodařilo se najít databázový modul. Zkontrolujte strukturu složek. {e}")

# Inicializace Flasku s opravenou cestou k obrázkům
app = Flask(__name__, 
            template_folder='templates',
            static_url_path='/imgs',     # URL na webu (např. /imgs/pravidla1.png)
            static_folder=IMG_FOLDER)    # Fyzické umístění na disku

app.secret_key = 'your-secret-key-mancala'

# --- DEMO UŽIVATELÉ ---
USERS = {
    'admin': {'password': 'admin123', 'is_admin': True},
    'petr': {'password': 'heslo1', 'is_admin': False},
    'honza': {'password': 'heslo2', 'is_admin': False},
    'lucka': {'password': 'heslo3', 'is_admin': False},
}

@app.before_request
def check_session():
    """Zajišťuje, že data o uživateli jsou dostupná v šablonách."""
    if 'user' not in session:
        session['user'] = None
        session['is_admin'] = False

@app.route('/')
def index():
    """Hlavní stránka s popisem projektu, pravidly a autory."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Zpracuje přihlášení uživatele."""
    username = request.form.get('username', '').strip()
    
    if username in USERS:
        session['user'] = username
        session['is_admin'] = USERS[username].get('is_admin', False)
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Odhlášení uživatele."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/zebricek')
def zebricek():
    """Zobrazení databázových dat - žebříček hráčů."""
    try:
        hraci = get_leaderboard()
    except Exception as e:
        print(f"Chyba při čtení z DB: {e}")
        hraci = []
    return render_template('zebricek.html', hraci=hraci)

@app.route('/smazat_hrace/<int:user_id>')
def smazat_hrace(user_id):
    """Smaže uživatele z DB (přístupné pouze pro admina)."""
    if not session.get('is_admin'):
        return redirect(url_for('zebricek'))
    
    delete_user(user_id)
    return redirect(url_for('zebricek'))

if __name__ == '__main__':
    # Debug mode je zapnutý pro snazší vývoj
    app.run(debug=True, host='localhost', port=5000)