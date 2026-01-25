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
    with open(SQL_INIT_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    generate_text_export()

def save_game_result(p1_id, p1_score, p2_id, p2_score):
    """
    Uloží výsledek zápasu (M:N vztah).
    Vytvoří záznam v 'zapasy' a dva záznamy v 'ucast_v_zapasu'.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Vytvoření zápasu
    cursor.execute("INSERT INTO zapasy DEFAULT VALUES")
    match_id = cursor.lastrowid
    
    # 2. Vložení obou hráčů (M:N účast)
    participants = [
        (p1_id, match_id, p1_score, 1 if p1_score > p2_score else 0),
        (p2_id, match_id, p2_score, 1 if p2_score > p1_score else 0)
    ]
    cursor.executemany(
        "INSERT INTO ucult_v_zapasu (uzivatel_id, zapas_id, skore, je_vitez) VALUES (?, ?, ?, ?)",
        participants
    )
    
    conn.commit()
    conn.close()
    generate_text_export() # Po každém zápasu aktualizujeme čitelný text

def generate_text_export():
    """
    Vygeneruje čitelný SQL Dump. 
    Tohle je ten soubor, který ukážeš komisi jako 'čitelná data'.
    """
    conn = sqlite3.connect(DB_PATH)
    with open(TEXT_EXPORT_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    conn.close()
    print(f"✅ Data exportována do čitelné podoby: {TEXT_EXPORT_PATH}")

def get_leaderboard():
    """Příklad JOINu pro maturitu."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
        SELECT u.jmeno, SUM(uvz.skore) as celkem
        FROM uzivatele u
        JOIN ucult_v_zapasu uvz ON u.id = uvz.uzivatel_id
        GROUP BY u.id
        ORDER BY celkem DESC
    """
    cursor.execute(query)
    res = cursor.fetchall()
    conn.close()
    return res

if __name__ == "__main__":
    init_db()