import sqlite3
import os

# Definice cest
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mancala.db")
SQL_INIT_PATH = os.path.join(BASE_DIR, "create_tables_local.sql")
TEXT_EXPORT_PATH = os.path.join(BASE_DIR, "export_pro_komisi.sql")

def init_db():
    """Inicializuje DB a vytvoří tabulky podle SQL skriptu."""
    if not os.path.exists(SQL_INIT_PATH):
        print(f"Varování: {SQL_INIT_PATH} nenalezen. Vytvořte jej pro správnou inicializaci.")
        return

    conn = sqlite3.connect(DB_PATH)
    # Zapnutí cizích klíčů pro DELETE ON CASCADE
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SQL_INIT_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    generate_text_export()

def save_game_result(p1_id, p1_score, p2_id, p2_score):
    """Uloží výsledek zápasu (M:N vztah)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    try:
        # Ensure users exist before saving game result
        cursor.execute("INSERT OR IGNORE INTO uzivatele (id, jmeno, email, heslo, role) VALUES (?, ?, ?, ?, ?)",
                      (p1_id, f"Hráč {p1_id}", f"hrac{p1_id}@game.local", "password", "user"))
        cursor.execute("INSERT OR IGNORE INTO uzivatele (id, jmeno, email, heslo, role) VALUES (?, ?, ?, ?, ?)",
                      (p2_id, f"Hráč {p2_id}", f"hrac{p2_id}@game.local", "password", "user"))
        
        cursor.execute("INSERT INTO zapasy DEFAULT VALUES")
        match_id = cursor.lastrowid
        
        participants = [
            (p1_id, match_id, p1_score, 1 if p1_score > p2_score else 0),
            (p2_id, match_id, p2_score, 1 if p2_score > p1_score else 0)
        ]
        cursor.executemany(
            "INSERT INTO ucast_v_zapasu (uzivatel_id, zapas_id, skore, je_vitez) VALUES (?, ?, ?, ?)",
            participants
        )
        
        conn.commit()
        print(f"💾 Výsledek uložen: Hráč {p1_id} ({p1_score}) vs Hráč {p2_id} ({p2_score})")
    except Exception as e:
        print(f"❌ Chyba při ukládání: {e}")
        conn.rollback()
    finally:
        conn.close()
        generate_text_export()

def generate_text_export():
    """Vygeneruje čitelný SQL Dump."""
    conn = sqlite3.connect(DB_PATH)
    with open(TEXT_EXPORT_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    conn.close()
    print(f"✅ Data exportována: {TEXT_EXPORT_PATH}")

# --- TADY JSOU TY DOPLNĚNÉ/UPRAVENÉ FUNKCE ---

def get_leaderboard():
    """Vrátí jméno, skóre a ID (důležité pro mazání)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # PŘIDÁNO u.id do SELECTu
    query = """
        SELECT u.jmeno, SUM(uvz.skore) as celkem, u.id
        FROM uzivatele u
        JOIN ucast_v_zapasu uvz ON u.id = uvz.uzivatel_id
        GROUP BY u.id
        ORDER BY celkem DESC
    """
    cursor.execute(query)
    res = cursor.fetchall()
    conn.close()
    return res

def delete_user(user_id):
    """
    Smaže uživatele podle ID. 
    Splňuje podmínku 'Upravuje data v databázi (DELETE)'.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        # Musíme zapnout foreign keys, aby fungovalo ON DELETE CASCADE
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uzivatele WHERE id = ?", (user_id,))
        conn.commit()
        print(f"🗑️ Uživatel ID {user_id} byl smazán.")
    except Exception as e:
        print(f"❌ Chyba při mazání: {e}")
    finally:
        conn.close()
        generate_text_export() # Aktualizujeme textový export po smazání

if __name__ == "__main__":
    init_db()