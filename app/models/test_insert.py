from datetime import date
import mysql.connector

# 1️⃣ Připojení k databázi
try:
    conn = mysql.connector.connect(
        host="dbs.spskladno.cz",      # školní server
        user="student21",             # tvé uživatelské jméno
        password="spsnet",       # tvé heslo
        database="vyuka21"            # název databáze
    )
    print("✅ Připojeno k databázi")
except mysql.connector.Error as e:
    print("❌ Chyba při připojení:", e)
    exit()

# 2️⃣ Data, která chceme vložit
data = ("Test", "Hráč", 1, 6767, date.today())
print("Vkládám hodnoty:", data)

# 3️⃣ Vložení dat do tabulky
try:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO maturita (jmeno, prijmeni, level, score, posledni_hra)
        VALUES (%s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    print("✅ Záznam vložen do tabulky maturita")
except mysql.connector.Error as e:
    print("❌ Chyba při vložení:", e)
finally:
    cursor.close()
    conn.close()
