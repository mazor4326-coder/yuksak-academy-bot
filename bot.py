import sys, urllib.request, urllib.parse, json, time, os, threading, re, sqlite3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from flask import Flask

# Load .env file
load_dotenv()

# Web server for Render
app = Flask('')
@app.route('/')
def home(): return "Yuksak Academy Bot (Version 2.2 - GUARANTEED) is running!"
def run():
    try:
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except: pass
def keep_alive():
    threading.Thread(target=run, daemon=True).start()

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_IDS = ["1477103854"]

# DATABASE
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
    def get_payments(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM payments").fetchall(); c.close(); return [dict(r) for r in rows]
    def get_hacker_logs(self):
        c = self.get_conn(); rows = c.execute("SELECT * FROM hacker_logs ORDER BY id DESC LIMIT 50").fetchall(); c.close(); return [dict(r) for r in rows]

db = Database(DB_NAME)

TEXTS = {
    'ru': {
        'choose_lang': "Выберите язык / Tilni tanlang / Choose language:",
        'welcome': "Assalomu alaykum! Добро пожаловать на платформу YUKSAK ACADEMY.",
        'req_contact': "Для регистрации поделитесь вашим номером телефона.",
        'contact_btn': "📱 Поделиться контактом",
        'thanks': "Ваш номер успешно зарегистрирован. Ознакомьтесь с правилами и нажмите 'Согласен'.",
        'agreement': "⚠️ *ПРАВИЛА И УСЛОВИЯ YUKSAK ACADEMY:*\n\n1. **Конфиденциальность:** Запрещено копировать, скачивать или пересылать видео-уроки третьим лицам. Все материалы защищены авторским правом.\n2. **ИИ Помощник:** В общении с ИИ строго запрещен мат, оскорбления и оффтоп. ИИ предназначен только для обучения.\n3. **Безопасность:** Любые попытки взлома, поиска уязвимостей или использования админ-команд приведут к немедленной блокировке (БАН) без возврата средств.\n4. **Уважение:** Мы ценим каждого студента и ожидаем взаимного уважения.\n5. **Аккаунты:** Один аккаунт предназначен для одного человека. Использование одного аккаунта несколькими лицами запрещено.\n6. **Возврат:** После получения доступа к цифровым материалам возврат средств не производится.\n7. **Обновления:** Академия оставляет за собой право обновлять материалы и правила.\n\nВы подтверждаете, что прочитали и согласны с правилами?",
        'agree_btn': "✅ Согласен(а) и принимаю условия",
        'courses_btn': "📚 Мои Курсы", 'subs_btn': "💎 Тарифы", 'ai_btn': "🤖 ИИ Помощник", 'support_btn': "📞 Тех. поддержка", 'founder_btn': "👨‍💼 Основатель", 'back_btn': "⬅️ Назад",
        'access_granted': "Отлично! Вам доступны разделы платформы.",
        'subs_info': "💎 *ТАРИФЫ (на 1 месяц):*\n\n🥉 **Standard — 60,000 сум**\n(Доступ к 1 курсу на выбор + AI помощник 200 вопросов)\n\n🥈 **Platinum — 120,000 сум**\n(Доступ к 2 курсам на выбор + AI помощник 400 вопросов)\n\n🥇 **VIP — 2,000,000 сум**\n(Доступ КО ВСЕМ курсам навсегда + Личное наставничество + Безлимитный AI)",
        'ai_welcome': "🤖 Я ваш AI-помощник. Задавайте вопросы!",
        'categories': {'prog': "💻 Программирование", 'design': "🎨 Дизайн", 'lang': "🌐 Языки", '3d': "🏗️ 3D Моделирование"},
        'courses': {'prog': ["🤖 Создание телеграм ботов", "🌐 Создание сайтов"], 'design': ["Создать дизайн через ИИ"], 'lang': ["🇺🇸 Английский", "🇷🇺 Русский"], '3d': ["⚙️ SolidWorks"]},
        'founder_txt': "👨‍💼 Kamolov Abdulaziz Sherzodbekovich\nXalqaro darajali muhandis & IT-tadbirkor\n\n📚 Ta'lim va malaka:\n🎓 Xalqaro qo'sh diplom (O'zbekiston & Belarus)\n• Belarus milliy texnika universiteti (BNTU), Minsk sh.\n• Andijon mashinasozlik instituti (AndMI)\n• Yo'nalish: «Intellektual asboblar va ishlab chiqarish mashinalari»\n• Format: Birgalikdagi xalqaro dastur, kredit-modul tizimi\n• Asosiy tayyorgarlik: 9 yil rus sinfida + 2 yil akademik litsey\n\n💼 Kasbiy tajriba:\n🏆 «Yuksak Academy» asoschisi — ta'lim platformasini ishlab chiquvchi va rahbari\n🎓 Maxsus fanlar o'qituvchisi (Mashina va mexanizmlar qurilishi)\n🏭 Xalqaro kompaniya UZ DONGWON da muhandislik amaliyoti",
        'support_txt': "📞 Qo'llab-quvvatlash:\n\n📱 Telegram: @yuksak_it\n📞 Tel: +998 50 777 51 52\n\n⚠️ Iltimos, mayda-chuyda narsalar uchun qo'ng'iroq qilmang."
    },
    'uz': {
        'choose_lang': "Tilni tanlang / Выберите язык / Choose language:",
        'welcome': "Assalomu alaykum! YUKSAK ACADEMY platformasiga xush kelibsiz.",
        'req_contact': "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.",
        'contact_btn': "📱 Kontaktni yuborish",
        'thanks': "Raqamingiz ro'yxatga olindi. Qoidalar bilan tanishib chiqing va 'Roziman' tugmasini bosing.",
        'agreement': "⚠️ YUKSAK ACADEMY QOIDALARI:\n\n1. Maxfiylik: Videolarni ko'chirish yoki tarqatish taqiqlanadi. Barcha huquqlar himoyalangan.\n2. AI Yordamchi: So'kinish va o'rinsiz gaplar taqiqlanadi. Faqat ta'lim uchun.\n3. Xavfsizlik: Tizimni buzishga urinish bloklanishga sabab bo'ladi.\n4. Hurmat: O'zaro hurmat majburiy.\n5. Hisoblar: Bir kishi uchun bitta profil.\n6. To'lov: Kursga kirish ruxsati berilgach, pul qaytarilmaydi.\n7. Yangilanish: Akademiya qoidalarni o'zgartirish huquqiga ega.\n\nQoidalarni qabul qilasizmi?",
        'agree_btn': "✅ Roziman",
        'courses_btn': "📚 Kurslarim", 'subs_btn': "💎 Tariflar", 'ai_btn': "🤖 AI yordamchi", 'support_btn': "📞 Tex. yordam", 'founder_btn': "👨‍💼 Asoschi", 'back_btn': "⬅️ Orqaga",
        'access_granted': "Platformadan foydalanishingiz mumkin.",
        'subs_info': "💎 *TARIFLAR (1 oyga):*\n\n🥉 **Standard — 60,000 so'm**\n(1 ta kursga kirish + AI 200 ta savol)\n\n🥈 **Platinum — 120,000 so'm**\n(2 ta kursga kirish + AI 400 ta savol)\n\n🥇 **VIP — 2,000,000 so'm**\n(Barcha kurslar + Shaxsiy ustoz + Limitsiz AI)",
        'ai_welcome': "🤖 Men AI yordamchingizman. Savol bering!",
        'categories': {'prog': "💻 Dasturlash", 'design': "🎨 Dizayn", 'lang': "🌐 Tillar", '3d': "🏗️ 3D Modellashtirish"},
        'courses': {'prog': ["🤖 Telegram botlar", "🌐 Saytlar"], 'design': ["AI orqali dizayn"], 'lang': ["🇺🇸 Ingliz tili", "🇷🇺 Rus tili"], '3d': ["⚙️ SolidWorks"]},
        'founder_txt': "👨‍💼 Kamolov Abdulaziz Sherzodbekovich\nXalqaro darajali muhandis & IT-tadbirkor\n\n📚 Ta'lim va malaka:\n🎓 Xalqaro qo'sh diplom (O'zbekiston & Belarus)\n• Belarus milliy texnika universiteti (BNTU), Minsk sh.\n• Andijon mashinasozlik instituti (AndMI)\n• Yo'nalish: «Intellektual asboblar va ishlab chiqarish mashinalari»\n• Format: Birgalikdagi xalqaro dastur, kredit-modul tizimi\n• Asosiy tayyorgarlik: 9 yil rus sinfida + 2 yil akademik litsey\n\n💼 Kasbiy tajriba:\n🏆 «Yuksak Academy» asoschisi — ta'lim platformasini ishlab chiquvchi va rahbari\n🎓 Maxsus fanlar o'qituvchisi (Mashina va mexanizmlar qurilishi)\n🏭 Xalqaro kompaniya UZ DONGWON da muhandislik amaliyoti",
        'support_txt': "📞 Qo'llab-quvvatlash:\n\n📱 Telegram: @yuksak_it\n📞 Tel: +998 50 777 51 52\n\n⚠️ Iltimos, mayda-chuyda narsalar uchun qo'ng'iroq qilmang."
    },
    'en': {
        'choose_lang': "Choose language:",
        'welcome': "Welcome to YUKSAK ACADEMY!",
        'req_contact': "Share phone number to register.",
        'contact_btn': "📱 Share Contact",
        'thanks': "Registered! Read rules and click 'Agree'.",
        'agreement': "⚠️ *TERMS AND CONDITIONS:*\n\n1. No sharing videos.\n2. No swearing in AI.\n3. Hack attempts = BAN.\n4. Respect others.\n5. One account per person.\n6. No refunds.\n7. Rules can be updated.\n\nDo you agree?",
        'agree_btn': "✅ I Agree",
        'courses_btn': "📚 My Courses", 'subs_btn': "💎 Plans", 'ai_btn': "🤖 AI Assistant", 'support_btn': "📞 Support", 'founder_btn': "👨‍💼 Founder", 'back_btn': "⬅️ Back",
        'access_granted': "Welcome!",
        'subs_info': "💎 *PLANS (per month):*\n\n🥉 **Standard — 60,000 UZS**\n🥈 **Platinum — 120,000 UZS**\n🥇 **VIP — 2,000,000 UZS**",
        'ai_welcome': "🤖 I am your AI assistant.",
        'categories': {'prog': "💻 Programming", 'design': "🎨 Design", 'lang': "🌐 Languages", '3d': "🏗️ 3D Modeling"},
        'courses': {'prog': ["🤖 Telegram bots", "🌐 Web design"], 'design': ["Create design via AI"], 'lang': ["🇺🇸 English", "🇷🇺 Russian"], '3d': ["⚙️ SolidWorks"]},
        'founder_txt': "👨‍💼 Kamolov Abdulaziz Sherzodbekovich\nXalqaro darajali muhandis & IT-tadbirkor\n\n📚 Ta'lim va malaka:\n🎓 Xalqaro qo'sh diplom (O'zbekiston & Belarus)\n• Belarus milliy texnika universiteti (BNTU), Minsk sh.\n• Andijon mashinasozlik instituti (AndMI)\n• Yo'nalish: «Intellektual asboblar va ishlab chiqarish mashinalari»\n• Format: Birgalikdagi xalqaro dastur, kredit-modul tizimi\n• Asosiy tayyorgarlik: 9 yil rus sinfida + 2 yil akademik litsey\n\n💼 Kasbiy tajriba:\n🏆 «Yuksak Academy» asoschisi — ta'lim platformasini ishlab chiquvchi va rahbari\n🎓 Maxsus fanlar o'qituvchisi (Mashina va mexanizmlar qurilishi)\n🏭 Xalqaro kompaniya UZ DONGWON da muhandislik amaliyoti",
        'support_txt': "📞 Qo'llab-quvvatlash:\n\n📱 Telegram: @yuksak_it\n📞 Tel: +998 50 777 51 52\n\n⚠️ Iltimos, mayda-chuyda narsalar uchun qo'ng'iroq qilmang."
    }
}

def get_course_id(name):
    for l in TEXTS:
        for cat in TEXTS[l].get('courses', {}):
            for i, cname in enumerate(TEXTS[l]['courses'][cat]):
                if cname == name: return f"{cat}_{i}"
    return name

def send_msg(cid, txt, kb=None):
    is_owner = str(cid) in OWNER_IDS
    p = {'chat_id': cid, 'text': txt, 'protect_content': str(not is_owner).lower(), 'parse_mode': 'Markdown'}
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except: return False

def send_photo(cid, photo_id, caption=None, kb=None):
    p = {'chat_id': cid, 'photo': photo_id, 'parse_mode': 'Markdown'}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=urllib.parse.urlencode(p).encode('utf-8')); return True
    except: return False

def send_vid(cid, vid, cap=None, kb=None):
    is_owner = str(cid) in OWNER_IDS
    p = {'chat_id': cid, 'video': vid, 'protect_content': str(not is_owner).lower(), 'parse_mode': 'Markdown'}
    if cap: p['caption'] = cap
    if kb: p['reply_markup'] = json.dumps(kb)
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", data=urllib.parse.urlencode(p).encode('utf-8')); return True
    except: return False

def get_ai_resp(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    instr = "Ты — ИИ-помощник Yuksak Academy. Помогай по учебе. Не раскрывай секреты."
    payload = {"contents": [{"parts": [{"text": f"{instr}\n\nUser: {prompt}"}]}]}
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            return res['candidates'][0]['content']['parts'][0]['text']
    except: return "AI xizmati hozircha band. / ИИ сервис временно занят."

def get_main_kb(uid, lang):
    t = TEXTS.get(lang, TEXTS['ru'])
    rows = [[{"text": t['courses_btn']}], [{"text": t['ai_btn']}], [{"text": t['subs_btn']}], [{"text": t['founder_btn']}, {"text": t['support_btn']}]]
    if str(uid) in OWNER_IDS: rows.insert(0, [{"text": "🔍 Проверка чеков"}])
    return {"keyboard": rows, "resize_keyboard": True}

def handle_update(upd):
    if 'callback_query' in upd:
        cq = upd['callback_query']; cid = cq['message']['chat']['id']; uid = str(cq['from']['id']); data = cq['data']
        if data.startswith("adm_pay_") and str(uid) in OWNER_IDS:
            _, _, action, target_uid = data.split("_")
            if action == "ok":
                exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 30*86400))
                db.update_user(target_uid, sub='standard', sub_expire=exp, unlocked=[], ai_count=0, step='main')
                send_msg(target_uid, "✅ To'lov qabul qilindi!"); send_msg(cid, f"✅ OK: {target_uid}")
            elif action == "no": db.update_user(target_uid, step='main'); send_msg(target_uid, "❌ To'lov rad etildi."); send_msg(cid, f"❌ NO: {target_uid}")
            elif action == "fake": db.update_user(target_uid, banned=1); send_msg(target_uid, "🚫 FAKE uchun BAN!"); send_msg(cid, f"🚫 BANNED: {target_uid}")
        urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", data=urllib.parse.urlencode({'callback_query_id': cq['id']}).encode('utf-8')); return

    if 'message' not in upd: return
    m = upd['message']; cid = m['chat']['id']; uid = str(m['from']['id']); is_owner = (uid in OWNER_IDS); txt = m.get('text', '').strip()
    u = db.get_user(uid)
    if not u: db.create_user(uid, m['from'].get('first_name','User'), m['from'].get('username','None')); u = db.get_user(uid)
    print(f"[LOG] {uid} | {u['step']} | {txt}")

    if u.get('banned'): send_msg(cid, "🚫 BAN!"); return
    lang = u.get('lang', 'ru'); t = TEXTS.get(lang, TEXTS['ru'])

    if txt == '/reset': db.update_user(uid, step="lang", agreed=0, lang=None, phone=None); send_msg(cid, "🔄 Reset!"); return
    if txt == '/version': send_msg(cid, "🤖 Version 2.2 (Absolute Final)"); return

    if 'contact' in m:
        db.update_user(uid, phone=m['contact']['phone_number'], step="agreement")
        send_msg(cid, t['thanks']); send_msg(cid, t['agreement'], kb={"keyboard": [[{"text": t['agree_btn']}]], "resize_keyboard": True}); return

    if txt:
        if any(txt == TEXTS[l]['support_btn'] for l in TEXTS): send_msg(cid, t['support_txt']); return
        if any(txt == TEXTS[l]['founder_btn'] for l in TEXTS): send_msg(cid, t['founder_txt']); return
        if any(txt == TEXTS[l]['back_btn'] for l in TEXTS): db.update_user(uid, step="main"); send_msg(cid, "🏠", kb=get_main_kb(uid, lang)); return

    if txt == '/start':
        db.update_user(uid, lang=None, step="lang")
        send_msg(cid, "Tilni tanlang / Выберите язык:", kb={"keyboard": [[{"text": "🇺🇿 O'zbekcha"}, {"text": "🇷🇺 Русский"}, {"text": "🇺🇸 English"}]], "resize_keyboard": True}); return

    if txt == "🔍 Проверка чеков" and is_owner:
        pending = [pu for pu in db.get_all_users().values() if pu.get('step') == 'awaiting_payment']
        if not pending: send_msg(cid, "✅ Bo'sh."); return
        for pu in pending[:5]:
            kb = {"inline_keyboard": [[{"text": "✅ OK", "callback_data": f"adm_pay_ok_{pu['id']}"}, {"text": "❌ NO", "callback_data": f"adm_pay_no_{pu['id']}"}, {"text": "🚫 FAKE", "callback_data": f"adm_pay_fake_{pu['id']}"}]]}
            send_msg(cid, f"👤 {pu['name']}\n🆔 `{pu['id']}`", kb=kb)
        return

    if (txt == '/admin' or txt.lower() in ['admin', 'админ']) and is_owner:
        db.update_user(uid, step="admin_main")
        kb = [[{"text": "🔍 Проверка чеков"}, {"text": "📊 Статистика"}], [{"text": "💰 Финансы"}, {"text": "📢 Объявление"}], [{"text": "⬅️ В меню"}]]
        send_msg(cid, "🛠 Admin Panel", kb={"keyboard": kb, "resize_keyboard": True}); return

    if txt in ["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇺🇸 English"]:
        l = 'uz' if "O'z" in txt else ('ru' if "Рус" in txt else 'en')
        db.update_user(uid, lang=l, step="contact")
        send_msg(cid, TEXTS[l]['welcome']); send_msg(cid, TEXTS[l]['req_contact'], kb={"keyboard": [[{"text": TEXTS[l]['contact_btn'], "request_contact": True}]], "resize_keyboard": True}); return

    if u['step'] == "agreement":
        if "roziman" in txt.lower() or "согласен" in txt.lower() or txt == t['agree_btn']:
            db.update_user(uid, step="main", agreed=1); send_msg(cid, t['access_granted'], kb=get_main_kb(uid, lang)); return

    if txt == t['subs_btn']:
        db.update_user(uid, step="subs"); send_msg(cid, t['subs_info'], kb={"keyboard": [[{"text": "Standard"}, {"text": "Platinum"}, {"text": "VIP"}], [{"text": t['back_btn']}]], "resize_keyboard": True}); return
    elif u['step'] == "subs" and txt in ["Standard", "Platinum", "VIP"]:
        card = "💳 HUMO: `9860 1604 2025 6085` (KAMOLOV A.)\n💳 UZCARD: `5440 8100 1696 6946` (KAMOLOV A.)"
        send_msg(cid, f"{card}\n\n📸 To'lov chekini yuboring."); db.update_user(uid, step="awaiting_payment"); return

    if 'photo' in m and not is_owner:
        for oid in OWNER_IDS: send_photo(oid, m['photo'][-1]['file_id'], caption=f"📸 YANGI CHEK! ID: `{uid}`")
        send_msg(cid, "✅ Qabul qilindi!"); return

    if txt == t['ai_btn']:
        db.update_user(uid, step="ai_chat"); send_msg(cid, t['ai_welcome'], kb={"keyboard": [[{"text": t['back_btn']}]], "resize_keyboard": True}); return
    elif u['step'] == "ai_chat" and txt:
        resp = get_ai_resp(txt); send_msg(cid, resp); return

    if txt == t['courses_btn']:
        db.update_user(uid, step="cats"); items = [{"text": v} for v in t['categories'].values()]
        send_msg(cid, "Category:", kb={"keyboard": [items[i:i+2] for i in range(0, len(items), 2)] + [[{"text": t['back_btn']}]], "resize_keyboard": True}); return

    if u['step'] == "cats" and any(txt == v for v in t['categories'].values()):
        cat_id = [k for k, v in t['categories'].items() if v == txt][0]
        db.update_user(uid, step=f"c_{cat_id}"); items = [{"text": c} for c in t['courses'][cat_id]]
        send_msg(cid, f"{txt}:", kb={"keyboard": [items[i:i+2] for i in range(0, len(items), 2)] + [[{"text": t['back_btn']}]], "resize_keyboard": True}); return

    if u['step'].startswith("c_") and txt:
        cat = u['step'].split("_")[1]
        if txt in t['courses'].get(cat, []):
            if not is_owner and u['sub'] == 'none': send_msg(cid, "🔒 To'lov qiling!"); return
            db.update_user(uid, step=f"lessons||{txt}"); c_id = get_course_id(txt); data = db.get_courses().get(c_id, [])
            items = [{"text": f"Qism {i+1}"} for i in range(len(data))]
            send_msg(cid, f"Курс: {txt}", kb={"keyboard": [items[i:i+2] for i in range(0, len(items), 2)] + [[{"text": t['back_btn']}]], "resize_keyboard": True}); return

    if u['step'].startswith("lessons||") and txt:
        course_name = u['step'].split("||")[1]; c_id = get_course_id(course_name); data = db.get_courses().get(c_id, [])
        try:
            pnum = int(txt.split()[-1])
            if 1 <= pnum <= len(data): v = data[pnum-1]; send_vid(cid, v['video'], v.get('caption'))
        except: pass

def main():
    keep_alive(); offset = 0
    with ThreadPoolExecutor(max_workers=50) as ex:
        while True:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=15"
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for upd in data.get('result', []):
                        offset = upd['update_id'] + 1; ex.submit(handle_update, upd)
            except: time.sleep(0.5)

if __name__ == "__main__": main()
