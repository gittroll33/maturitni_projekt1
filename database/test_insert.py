import mysql.connector

conn = mysql.connector.connect(
    host="dbs.spskladno.cz",
    user="student21",
    password="spsnet",
    database="vyuka21"
)
cursor = conn.cursor()

with open("insert_sample_alt.sql", "r") as f:
    sql_commands = f.read().split(";")
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)

conn.commit()
cursor.close()
conn.close()
print("✅ Testovací data vložena")
