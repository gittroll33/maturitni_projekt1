# app/web_portal.py
from flask import Flask, render_template, request, session, redirect, url_for
import sys
import os

# Add database_local to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "database_local"))

from db_manager_local import get_leaderboard, delete_user, save_game_result

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key-mancala'

# NOTE: Removed init_db() call - the game already initializes it
# If you need to initialize fresh, delete mancala.db manually

# Hardcoded credentials for demo
USERS = {
    'admin': {'password': 'admin123', 'is_admin': True},
    'petr': {'password': 'heslo1', 'is_admin': False},
    'honza': {'password': 'heslo2', 'is_admin': False},
    'lucka': {'password': 'heslo3', 'is_admin': False},
}

@app.before_request
def check_session():
    """Ensure user data is available in templates."""
    if 'user' not in session:
        session['user'] = None
        session['is_admin'] = False

@app.route('/')
def index():
    """Homepage with login form."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    username = request.form.get('username', '').strip()
    
    if username in USERS:
        session['user'] = username
        session['is_admin'] = USERS[username].get('is_admin', False)
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/zebricek')
def zebricek():
    """Display leaderboard from database."""
    try:
        hraci = get_leaderboard()
        print(f"DEBUG: Leaderboard data: {hraci}")  # Debug output
    except Exception as e:
        print(f"ERROR fetching leaderboard: {e}")
        hraci = []
    return render_template('zebricek.html', hraci=hraci)

@app.route('/smazat_hrace/<int:user_id>')
def smazat_hrace(user_id):
    """Delete a user (admin only)."""
    if not session.get('is_admin'):
        return redirect(url_for('zebricek'))
    
    delete_user(user_id)
    return redirect(url_for('zebricek'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)