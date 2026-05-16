import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, Response, send_from_directory, redirect

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='templates')

ADMIN_USER = "aziz67876578"
ADMIN_PASS = "67596854903876584"
DB_PATH = r"C:\Users\Admin\Music\Kamolov.A. PROEKT YUKSAK AKADEMIYA\yuksak.db"

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response(
    'Вход в Админ-панель YUKSAK ACADEMY\n'
    'Пожалуйста, введите логин и пароль.', 401,
    {'WWW-Authenticate': 'Basic realm="Admin Access"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin')
@requires_auth
def admin_panel():
    conn = get_db_connection()
    users_count = conn.execute("SELECT count(*) FROM users").fetchone()[0]
    banned_count = conn.execute("SELECT count(*) FROM users WHERE banned=1").fetchone()[0]
    payments_total = conn.execute("SELECT sum(amount) FROM payments").fetchone()[0] or 0
    hacker_logs = conn.execute("SELECT * FROM hacker_logs ORDER BY id DESC LIMIT 10").fetchall()
    
    # Check if extra_ai column exists
    try:
        conn.execute("ALTER TABLE users ADD COLUMN extra_ai INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
        
    users = conn.execute("SELECT * FROM users ORDER BY rowid DESC LIMIT 50").fetchall()
    extra_buyers = conn.execute("SELECT count(*) FROM users WHERE extra_ai > 0").fetchone()[0]
    
    conn.close()
    
    return render_template('admin.html', 
                           users_count=users_count, 
                           banned_count=banned_count,
                           payments_total=payments_total,
                           hacker_logs=hacker_logs,
                           users=users,
                           extra_buyers=extra_buyers)

@app.route('/grant_access', methods=['POST'])
@requires_auth
def grant_access():
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    
    conn = get_db_connection()
    if action in ['standard', 'platinum', 'vip']:
        conn.execute("UPDATE users SET sub=? WHERE id=?", (action, user_id))
    elif action == 'extra100':
        conn.execute("UPDATE users SET extra_ai = extra_ai + 100 WHERE id=?", (user_id,))
    elif action == 'extra200':
        conn.execute("UPDATE users SET extra_ai = extra_ai + 200 WHERE id=?", (user_id,))
        
    conn.commit()
    conn.close()
    
    return redirect('/admin')

@app.route('/unban', methods=['POST'])
@requires_auth
def unban_user():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    # Разблокируем, сбрасываем нарушения и "сжигаем" тариф
    conn.execute("UPDATE users SET banned=0, violations=0, sub='none', extra_ai=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("YUKSAK ACADEMY Web Server starting on http://localhost:5000")
    print("Admin Panel available at http://localhost:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=True)
