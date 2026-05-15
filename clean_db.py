import sqlite3, json

db_path = r"c:\Users\Admin\Music\Kamolov.A. PROEKT YUKSAK AKADEMIYA\yuksak.db"
conn = sqlite3.connect(db_path)
curr = conn.cursor()

# Чистим курсы
curr.execute("SELECT name, data FROM courses")
rows = curr.fetchall()
for name, data_json in rows:
    if "**" in data_json:
        new_data = data_json.replace("**", "")
        curr.execute("UPDATE courses SET data=? WHERE name=?", (new_data, name))
        print(f"Cleaned course: {name}")

# Чистим пользователей (если в именах есть **)
curr.execute("SELECT id, name FROM users")
rows = curr.fetchall()
for uid, name in rows:
    if name and "**" in name:
        new_name = name.replace("**", "")
        curr.execute("UPDATE users SET name=? WHERE id=?", (new_name, uid))
        print(f"Cleaned user: {uid}")

conn.commit()
conn.close()
print("Database is now CLEAN of **")
