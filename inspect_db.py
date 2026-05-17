import sqlite3

DB_PATH = r"C:\Users\Admin\Music\Kamolov.A. PROEKT YUKSAK AKADEMIYA\yuksak.db"
conn = sqlite3.connect(DB_PATH)

# Show all tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

# Show courses table schema
for t in tables:
    print(f"\nSchema of '{t[0]}':")
    print(conn.execute(f"PRAGMA table_info({t[0]})").fetchall())
    if t[0] == 'courses':
        print("Courses data:", conn.execute("SELECT * FROM courses LIMIT 10").fetchall())

conn.close()
