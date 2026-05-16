import sys, urllib.request, urllib.parse, json, time, os, threading, re, sqlite3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask('')
@app.route('/')
def home(): return "Yuksak Academy Bot is running!"
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
def keep_alive():
    threading.Thread(target=run, daemon=True).start()

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_IDS = ["1477103854"]

DB_NAME = "yuksak.db"
class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.lock = threading.Lock()
        self.init_db()
    def get_conn(self):
        conn = sqlite3.connect(self.db_name); conn.row_factory = sqlite3.Row; return conn
    def init_db(self):
        with self.lock:
            c = self.get_conn(); curr = c.cursor()
            curr.execute("""CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, name TEXT, username TEXT, phone TEXT, step TEXT, sub TEXT DEFAULT 'none',
                ai_count INTEGER DEFAULT 0, violations INTEGER DEFAULT 0, banned BOOLEAN DEFAULT 0,
                lang TEXT, agreed BOOLEAN DEFAULT 0, unlocked TEXT DEFAULT '[]',
                ai_history TEXT DEFAULT '[]', violation_history TEXT DEFAULT '[]', temp_video_id TEXT, sub_expire TEXT
            )""")
            curr.execute("CREATE TABLE IF NOT EXISTS courses (name TEXT PRIMARY KEY, data TEXT DEFAULT '[]')")
            curr.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, amount INTEGER, date TEXT, phone TEXT, tariff TEXT)")
            curr.execute("CREATE TABLE IF NOT EXISTS hacker_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, name TEXT, username TEXT, phone TEXT, bad_text TEXT, reason TEXT, timestamp TEXT)")
            curr.execute("CREATE TABLE IF NOT EXISTS interests (category TEXT PRIMARY KEY, user_ids TEXT DEFAULT '[]')")
            curr.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            c.commit(); c.close()
    def get_user(self, uid):
        c = self.get_conn(); r = c.execute("SELECT * FROM users WHERE id=?", (str(uid),)).fetchone(); c.close()
        if r:
            u = dict(r); u['unlocked'] = json.loads(u['unlocked']); u['ai_history'] = json.loads(u['ai_history'])
            u['violation_history'] = json.loads(u['violation_history']); return u
        return None
    def update_user(self, uid, **kw):
        for k in ['unlocked', 'ai_history', 'violation_history']:
            if k in kw: kw[k] = json.dumps(kw[k])
        cols = ", ".join([f"{k}=?" for k in kw.keys()]); vals = list(kw.values()) + [str(uid)]
        with self.lock:
            c = self.get_conn(); c.execute(f"UPDATE users SET {cols} WHERE id=?", vals); c.commit(); c.close()
    def create_user(self, uid, n, un):
        with self.lock:
            c = self.get_conn(); c.execute("INSERT OR IGNORE INTO users (id, name, username, step) VALUES (?,?,?, 'lang')", (str(uid), n, un)); c.commit(); c.close()
    def get_all_users(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM users").fetchall(); c.close(); res = {}
        for r in rows:
            u = dict(r); u['unlocked'] = json.loads(u['unlocked']); u['ai_history'] = json.loads(u['ai_history'])
            u['violation_history'] = json.loads(u['violation_history']); res[r['id']] = u
        return res
    def get_courses(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM courses").fetchall(); c.close()
        return {r['name']: json.loads(r['data']) for r in rows}
    def update_course(self, n, d):
        with self.lock:
            c = self.get_conn(); c.execute("INSERT OR REPLACE INTO courses (name, data) VALUES (?,?)", (n, json.dumps(d))); c.commit(); c.close()
    def get_payments(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM payments").fetchall(); c.close(); return [dict(r) for r in rows]
    def get_hacker_logs(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM hacker_logs ORDER BY id DESC LIMIT 50").fetchall(); c.close(); return [dict(r) for r in rows]
    def get_interests_all(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM interests").fetchall(); c.close()
        return {r['category']: json.loads(r['user_ids']) for r in rows}
    def get_setting(self, key):
        c = self.get_conn(); r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone(); c.close()
        return r['value'] if r else None
    def set_setting(self, key, value):
        with self.lock:
            c = self.get_conn(); c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value)); c.commit(); c.close()

db = Database(DB_NAME)

TEXTS = {
    'ru': {
        'choose_lang': "Выберите язык:", 'welcome': "Добро пожаловать в YUKSAK ACADEMY.", 'req_contact': "Поделитесь номером телефона для регистрации.", 'contact_btn': "📱 Отправить контакт", 'thanks': "Регистрация завершена. Примите правила.", 'agreement': "⚠️ Правила: Не копировать контент, не спамить. Согласны?", 'agree_btn': "✅ Согласен", 'courses_btn': "📚 Мои Курсы", 'subs_btn': "💎 Тарифы", 'ai_btn': "🤖 ИИ Помощник", 'support_btn': "📞 Поддержка", 'founder_btn': "👨‍💼 Основатель", 'back_btn': "⬅️ Назад", 'access_granted': "Доступ открыт!", 'subs_info': "💎 Тарифы: Standard (60к), Platinum (120к), VIP (2млн).", 'ai_welcome': "🤖 Я ваш AI-помощник.", 'user_banned': "🚫 БАН.",
        'categories': {'prog': "💻 Программирование", 'design': "🎨 Дизайн", 'lang': "🌐 Языки", '3d': "🏗️ 3D Моделирование", '1c': "📊 1С Бухгалтерия", 'comp': "🖥️ Компьютерная грамотность"},
        'courses': {'prog': ["🤖 Телеграм боты", "🌐 Сайты"], 'design': ["Дизайн через AI"], 'lang': ["🇺🇸 English", "🇷🇺 Русский"], '3d': ["⚙️ SolidWorks"], '1c': [f"📉 1С: Бухгалтерия {i}-курс" for i in range(1, 6)], 'comp': ["🖥️ Компьютер с нуля"]}
    },
    'uz': {
        'choose_lang': "Tilni tanlang:", 'welcome': "YUKSAK ACADEMYga xush kelibsiz.", 'req_contact': "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.", 'contact_btn': "📱 Kontaktni yuborish", 'thanks': "Ro'yxatdan o'tdingiz. Qoidalarni qabul qiling.", 'agreement': "⚠️ Qoidalar: Videolarni tarqatish taqiqlanadi. Rozimisiz?", 'agree_btn': "✅ Roziman", 'courses_btn': "📚 Kurslarim", 'subs_btn': "💎 Tariflar", 'ai_btn': "🤖 AI yordamchi", 'support_btn': "📞 Tex. yordam", 'founder_btn': "👨‍💼 Asoschi", 'back_btn': "⬅️ Orqaga", 'access_granted': "Xush kelibsiz!", 'subs_info': "💎 Tariflar: Standard (60k), Platinum (120k), VIP (2mln).", 'ai_welcome': "🤖 Men AI yordamchingizman.", 'user_banned': "🚫 SIZ BLOKLANDINGIZ!",
        'categories': {'prog': "💻 Dasturlash", 'design': "🎨 Dizayn", 'lang': "🌐 Tillar", '3d': "🏗️ 3D Modellashtirish", '1c': "📊 1С Buxgalteriya", 'comp': "🖥️ Kompyuter savodxonligi"},
        'courses': {'prog': ["🤖 Telegram botlar", "🌐 Saytlar"], 'design': ["AI orqali dizayn"], 'lang': ["🇺🇸 Ingliz tili", "🇷🇺 Rus tili"], '3d': ["⚙️ SolidWorks"], '1c': [f"📉 1С: Buxgalteriya {i}-kurs" for i in range(1, 6)], 'comp': ["🖥️ Kompyuter savodxonligi"]}
    }
}

def get_course_id(name):
    for l in TEXTS:
        for cat in TEXTS[l].get('courses', {}):
            for i, c in enumerate(TEXTS[l]['courses'][cat]):
                if c == name: return f"{cat}_{i}"
    return name

def send_msg(cid, txt, kb=None):
    p = {'chat_id': cid, 'text': txt, 'parse_mode': 'Markdown', 'protect_content': 'true' if str(cid) not in OWNER_IDS else 'false'}
    if kb: p['reply_markup'] = json.dumps(kb)
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8')); return True
    except: return False

def send_photo(cid, photo_id, caption=None, kb=None):
    p = {'chat_id': cid, 'photo': photo_id, 'parse_mode': 'Markdown'}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=urllib.parse.urlencode(p).encode('utf-8')); return True
    except: return False

def get_ai_resp(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())['candidates'][0]['content']['parts'][0]['text']
    except: return "AI busy."

def get_main_kb(uid, lang):
    t = TEXTS.get(lang, TEXTS['ru'])
    rows = [[{"text": t['courses_btn']}], [{"text": t['ai_btn']}], [{"text": t['subs_btn']}], [{"text": t['founder_btn']}, {"text": t['support_btn']}]]
    if str(uid) in OWNER_IDS: rows.insert(0, [{"text": "🔍 Проверка чеков"}])
    return {"keyboard": rows, "resize_keyboard": True}

def handle_update(upd):
    if 'callback_query' in upd:
        cq = upd['callback_query']; uid = str(cq['from']['id']); data = cq['data']; cid = cq['message']['chat']['id']
        if data.startswith("adm_pay_") and uid in OWNER_IDS:
            _, _, action, target_id = data.split("_")
            if action == "ok":
                exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 30*86400))
                db.update_user(target_id, sub='standard', sub_expire=exp, unlocked=[], ai_count=0, step='main')
                send_msg(target_id, "✅ Доступ разрешен! / Ruxsat berildi!"); send_msg(cid, f"✅ OK: {target_id}")
            elif action == "no": send_msg(target_id, "❌ Отклонено. / Rad etildi."); send_msg(cid, f"❌ NO: {target_id}")
            elif action == "fake": db.update_user(target_id, banned=1); send_msg(target_id, "🚫 БАН за фейк!"); send_msg(cid, f"🚫 BANNED: {target_id}")
        urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", data=urllib.parse.urlencode({'callback_query_id': cq['id']}).encode('utf-8')); return

    if 'message' not in upd: return
    m = upd['message']; cid = m['chat']['id']; uid = str(m['from']['id']); is_owner = (uid in OWNER_IDS); txt = m.get('text', '').strip()
    u = db.get_user(uid)
    if not u: db.create_user(uid, m['from'].get('first_name','User'), m['from'].get('username','None')); u = db.get_user(uid)
    if u.get('banned'): send_msg(cid, "🚫 BAN!"); return
    lang = u.get('lang', 'ru'); t = TEXTS.get(lang, TEXTS['ru'])

    if 'contact' in m:
        db.update_user(uid, phone=m['contact']['phone_number'], step="agreement")
        send_msg(cid, t['agreement'], kb={"keyboard": [[{"text": t['agree_btn']}]], "resize_keyboard": True}); return

    if txt == '/start':
        db.update_user(uid, step="lang")
        send_msg(cid, "Tilni tanlang / Выберите язык:", kb={"keyboard": [[{"text": "🇺🇿 O'zbekcha"}, {"text": "🇷🇺 Русский"}]], "resize_keyboard": True}); return

    if txt == "🔍 Проверка чеков" and is_owner:
        pending = [p for p in db.get_all_users().values() if p.get('step') == 'awaiting_payment']
        if not pending: send_msg(cid, "✅ Нет чеков."); return
        for p in pending[:5]:
            kb = {"inline_keyboard": [[{"text": "✅ OK", "callback_data": f"adm_pay_ok_{p['id']}"}, {"text": "❌ NO", "callback_data": f"adm_pay_no_{p['id']}"}, {"text": "🚫 FAKE", "callback_data": f"adm_pay_fake_{p['id']}"}]]}
            send_msg(cid, f"👤 {p['name']}\n📞 {p.get('phone')}\n🆔 `{p['id']}`", kb=kb)
        return

    if txt == '/admin' and is_owner:
        db.update_user(uid, step="admin_main")
        kb = [[{"text": "🔍 Проверка чеков"}, {"text": "📊 Статистика"}], [{"text": "📢 Объявление"}, {"text": "⬅️ В меню"}]]
        send_msg(cid, "🛠 Admin Panel", kb={"keyboard": kb, "resize_keyboard": True}); return

    if u['step'] == "admin_main" and is_owner:
        if txt == "📊 Статистика":
            users = db.get_all_users(); send_msg(cid, f"📊 Всего: {len(users)}")
        elif txt == "📢 Объявление":
            db.update_user(uid, step="admin_bc"); send_msg(cid, "Текст рассылки:")
        elif txt == "⬅️ В меню":
            db.update_user(uid, step="main"); send_msg(cid, "🏠", kb=get_main_kb(uid, lang))
        return

    if u['step'] == "admin_bc" and is_owner and txt:
        all_u = db.get_all_users(); count = 0
        for tid in all_u:
            if send_msg(tid, f"📢 E'LON:\n\n{txt}"): count += 1
            time.sleep(0.05)
        send_msg(cid, f"✅ OK: {count}"); db.update_user(uid, step="admin_main"); return

    if txt in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"]:
        l = 'uz' if "O'z" in txt else 'ru'
        db.update_user(uid, lang=l, step="contact" if not u.get('phone') else "main")
        if not u.get('phone'): send_msg(cid, TEXTS[l]['req_contact'], kb={"keyboard": [[{"text": TEXTS[l]['contact_btn'], "request_contact": True}]], "resize_keyboard": True})
        else: send_msg(cid, TEXTS[l]['access_granted'], kb=get_main_kb(uid, l)); return

    if u['step'] == "agreement" and txt == t['agree_btn']:
        db.update_user(uid, step="main", agreed=1); send_msg(cid, t['access_granted'], kb=get_main_kb(uid, lang)); return

    if txt == t['subs_btn']:
        db.update_user(uid, step="subs"); send_msg(cid, t['subs_info'], kb={"keyboard": [[{"text": "Standard"}, {"text": "Platinum"}], [{"text": t['back_btn']}]], "resize_keyboard": True}); return
    elif u['step'] == "subs" and txt in ["Standard", "Platinum"]:
        send_msg(cid, "💳 HUMO: `9860 1604 2025 6085` (KAMOLOV A.)\n\n📸 Отправьте чек сюда."); db.update_user(uid, step="awaiting_payment"); return

    if 'photo' in m and not is_owner:
        for oid in OWNER_IDS: send_photo(oid, m['photo'][-1]['file_id'], caption=f"📸 YANGI CHEK! ID: `{uid}`")
        send_msg(cid, "✅ Чек получен! Ждите проверки."); return

    if txt == t['courses_btn']:
        db.update_user(uid, step="cats"); items = [[{"text": v}] for v in t['categories'].values()]
        send_msg(cid, "Category:", kb={"keyboard": items + [[{"text": t['back_btn']}]], "resize_keyboard": True}); return

def main():
    keep_alive(); offset = 0
    with ThreadPoolExecutor(max_workers=50) as ex:
        while True:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=15"
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode())
                    for upd in data.get('result', []):
                        offset = upd['update_id'] + 1; ex.submit(handle_update, upd)
            except: time.sleep(0.5)

if __name__ == "__main__": main()
