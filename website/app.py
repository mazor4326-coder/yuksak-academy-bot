import os
import sqlite3
import urllib.request
import urllib.parse
import json
from functools import wraps
from flask import Flask, render_template, request, Response, send_from_directory, redirect

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='templates')

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

def send_telegram_msg(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        data = urllib.parse.urlencode(payload).encode('utf-8')
        urllib.request.urlopen(url, data=data)
    except Exception as e:
        print(f"Error sending TG message: {e}")

import time
ADMIN_USER = "aziz67876578"
ADMIN_PASS = "67596854903876584"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yuksak.db")

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
        expire_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 30 * 86400))
        conn.execute("UPDATE users SET sub=?, sub_expire=?, unlocked='[]', ai_count=0 WHERE id=?", (action, expire_date, user_id))
        
        # Get phone number to log in payments table
        u = conn.execute("SELECT phone FROM users WHERE id=?", (user_id,)).fetchone()
        phone = u['phone'] if u and u['phone'] else '-'
        amount = 60000 if action == 'standard' else (120000 if action == 'platinum' else 2000000)
        pay_date = time.strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("INSERT INTO payments (user_id, amount, date, phone, tariff) VALUES (?,?,?,?,?)", (user_id, amount, pay_date, phone, action))
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

@app.route('/reject_payment', methods=['POST'])
@requires_auth
def reject_payment():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    user = conn.execute("SELECT lang FROM users WHERE id=?", (user_id,)).fetchone()
    lang = user['lang'] if user and user['lang'] else 'ru'
    
    msgs = {
        'ru': "❌ Ваш платеж отклонен. Пожалуйста, проверьте данные или свяжитесь с поддержкой.",
        'uz': "❌ To'lovingiz rad etildi. Iltimos, ma'lumotlarni tekshiring yoki qo'llab-quvvatlash xizmatiga murojaat qiling.",
        'en': "❌ Your payment was rejected. Please check the details or contact support."
    }
    send_telegram_msg(user_id, msgs.get(lang, msgs['ru']))
    conn.execute("UPDATE users SET step='main' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/fake_payment', methods=['POST'])
@requires_auth
def fake_payment():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    
    msg = (
        "⚠️ *ВНИМАНИЕ / DIQQAT / ATTENTION*\n\n"
        "🇷🇺 Вы отправили фальшивый чек. По закону Узбекистана это называется мошенничеством, и ваш аккаунт был зафиксирован. Если у вас есть претензии, пишите админу в техподдержку.\n\n"
        "🇺🇿 Siz soxta chek yubordingiz. O'zbekiston qonunchiligiga ko'ra bu firibgarlik deb ataladi va sizning hisobingiz qayd etildi. Agar e'tirozlaringiz bo'lsa, texnik yordamga murojaat qiling.\n\n"
        "🇺🇸 You sent a fake receipt. According to the laws of Uzbekistan, this is called fraud, and your account has been recorded. If you have any claims, contact tech support."
    )
    send_telegram_msg(user_id, msg)
    
    # Блокируем пользователя
    conn.execute("UPDATE users SET banned=1, step='banned' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("YUKSAK ACADEMY Web Server starting on http://localhost:5000")
    print("Admin Panel available at http://localhost:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=True)
