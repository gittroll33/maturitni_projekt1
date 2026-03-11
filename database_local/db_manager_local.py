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
        print(f"Varování: {SQL_INIT_PATH} nenalezen.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SQL_INIT_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    generate_text_export()

def get_or_create_user(cursor, jmeno):
    """Pomocná funkce: Najde ID uživatele podle jména, nebo vytvoří nového."""
    cursor.execute("SELECT id FROM uzivatele WHERE jmeno = ?", (jmeno,))
    res = cursor.fetchone()
    if res:
        return res[0]
    else:
        # Vytvoření nového uživatele s výchozími údaji
        cursor.execute(
            "INSERT INTO uzivatele (jmeno, email, heslo, role) VALUES (?, ?, ?, ?)",
            (jmeno, f"{jmeno.lower()}@mancala.local", "password123", "user")
        )
        return cursor.lastrowid

def save_game_result(p1_name, p1_score, p2_name, p2_score):
    """Uloží výsledek zápasu (M:N vztah přes tabulku ucast_v_zapasu)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    try:
        # 1. Získání ID uživatelů podle jmen z Pygame
        p1_id = get_or_create_user(cursor, p1_name)
        p2_id = get_or_create_user(cursor, p2_name)
        
        # 2. Vytvoření záznamu o zápasu
        cursor.execute("INSERT INTO zapasy DEFAULT VALUES")
        match_id = cursor.lastrowid
        
        # 3. Rozdělení výsledků do spojovací tabulky (M:N)
        participants = [
            (p1_id, match_id, p1_score, 1 if p1_score > p2_score else 0),
            (p2_id, match_id, p2_score, 1 if p2_score > p1_score else 0)
        ]
        cursor.executemany(
            "INSERT INTO ucast_v_zapasu (uzivatel_id, zapas_id, skore, je_vitez) VALUES (?, ?, ?, ?)",
            participants
        )
        
        conn.commit()
        print(f"💾 Výsledek uložen: {p1_name} ({p1_score}) vs {p2_name} ({p2_score})")
    except Exception as e:
        print(f"❌ Chyba při ukládání: {e}")
        conn.rollback()
    finally:
        conn.close()
        generate_text_export()

def update_user_name(user_id, new_name):
    """
    Upraví jméno uživatele.
    Splňuje podmínku 'Upravuje data v databázi (UPDATE)'.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE uzivatele SET jmeno = ? WHERE id = ?", (new_name, user_id))
        conn.commit()
        print(f"📝 Uživatel ID {user_id} změněn na '{new_name}'.")
    except Exception as e:
        print(f"❌ Chyba při aktualizaci: {e}")
    finally:
        conn.close()
        generate_text_export()

def delete_user(user_id):
    """Smaže uživatele. Díky ON DELETE CASCADE se smažou i jeho účasti v zápasech."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uzivatele WHERE id = ?", (user_id,))
        conn.commit()
        print(f"🗑️ Uživatel ID {user_id} smazán.")
    except Exception as e:
        print(f"❌ Chyba při mazání: {e}")
    finally:
        conn.close()
        generate_text_export()

def get_leaderboard():
    """Vrátí žebříček pomocí JOINu."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

def generate_text_export():
    """Vygeneruje čitelný SQL Dump pro komisi."""
    conn = sqlite3.connect(DB_PATH)
    with open(TEXT_EXPORT_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    conn.close()
    print(f"✅ Export vytvořen: {TEXT_EXPORT_PATH}")

if __name__ == "__main__":
    init_db()