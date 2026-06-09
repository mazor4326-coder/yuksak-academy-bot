import sys, urllib.request, urllib.parse, json, time, os, threading, sqlite3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask('')
@app.route('/')
def home(): return "PUBG UC Shop Bot is running!"
def run():
    try: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10001)), debug=False, use_reloader=False)
    except: pass
def keep_alive(): threading.Thread(target=run, daemon=True).start()

TOKEN = os.getenv("PUBG_BOT_TOKEN")
if not TOKEN:
    print("[ERROR] Не найден переменный PUBG_BOT_TOKEN в .env. Завершаю работу.")
    exit(1)

OWNER_IDS = ["1477103854"]
CARD = "8888 0144 9062 6927"

# UC Packages: (name, uc_amount, price_uzs)
PACKAGES = [
    ("60 UC", 60, 15000),
    ("325 UC", 325, 70000),
    ("660 UC", 660, 135000),
    ("1800 UC", 1800, 350000),
    ("3850 UC", 3850, 700000),
    ("8100 UC", 8100, 1400000),
]

TEXTS = {
    'uz': {
        'choose_lang': "Tilni tanlang:",
        'welcome': "🎮 *PUBG UC SHOP* ga xush kelibsiz!\nBu yerda siz PUBG Mobile uchun UC sotib olishingiz mumkin.",
        'req_contact': "📱 Telefon raqamingizni yuboring:",
        'contact_btn': "📱 Kontaktni yuborish",
        'main_menu': "🏠 Asosiy menyu:",
        'buy_uc': "🛒 UC Sotib olish",
        'my_orders': "📦 Buyurtmalarim",
        'profile': "👤 Profilim",
        'support': "📞 Yordam",
        'back': "⬅️ Orqaga",
        'choose_pkg': "📦 UC paketini tanlang:",
        'enter_id': "🎮 PUBG Player ID raqamingizni yuboring:",
        'enter_nick': "👤 PUBG nikneymingizni yuboring:",
        'confirm': "✅ *Buyurtmani tasdiqlang:*\n\n📦 Paket: {pkg}\n💰 Narx: {price} so'm\n🎮 Player ID: {pid}\n👤 Nikneym: {nick}\n\nTo'g'rimi?",
        'yes': "✅ Tasdiqlash",
        'no': "❌ Bekor qilish",
        'pay_info': "💳 *To'lov ma'lumotlari:*\n\n💳 Karta: `{card}`\n💰 Summa: {price} so'm\n\n📸 To'lov chekini (screenshot) yuboring.",
        'order_sent': "✅ Chek qabul qilindi! Admin tekshirgandan so'ng UC yuboriladi.",
        'order_approved': "✅ Buyurtmangiz tasdiqlandi! UC tez orada yuboriladi.",
        'order_rejected': "❌ Buyurtmangiz rad etildi. Iltimos, qaytadan urinib ko'ring.",
        'no_orders': "📭 Sizda hali buyurtmalar yo'q.",
        'support_txt': "📞 Yordam: @yuksak_it\n📱 Tel: +998 50 777 51 52",
        'banned': "🚫 Siz bloklangansiz!",
        'cancelled': "❌ Buyurtma bekor qilindi.",
        'topup_success': "✅ *Sizning PUBG balansingiz muvaffaqiyatli to'ldirildi!*\n\n🚀 Bizning xizmatimiz eng tezkor va ishonchli! Bizni tanlaganingiz uchun tashakkur! 🎮",
    },
    'ru': {
        'choose_lang': "Выберите язык:",
        'welcome': "🎮 Добро пожаловать в *PUBG UC SHOP*!\nЗдесь вы можете купить UC для PUBG Mobile.",
        'req_contact': "📱 Отправьте ваш номер телефона:",
        'contact_btn': "📱 Поделиться контактом",
        'main_menu': "🏠 Главное меню:",
        'buy_uc': "🛒 Купить UC",
        'my_orders': "📦 Мои заказы",
        'profile': "👤 Профиль",
        'support': "📞 Поддержка",
        'back': "⬅️ Назад",
        'choose_pkg': "📦 Выберите пакет UC:",
        'enter_id': "🎮 Отправьте ваш PUBG Player ID:",
        'enter_nick': "👤 Отправьте ваш никнейм в PUBG:",
        'confirm': "✅ *Подтвердите заказ:*\n\n📦 Пакет: {pkg}\n💰 Цена: {price} сум\n🎮 Player ID: {pid}\n👤 Никнейм: {nick}\n\nВсё верно?",
        'yes': "✅ Подтвердить",
        'no': "❌ Отменить",
        'pay_info': "💳 *Данные для оплаты:*\n\n💳 Карта: `{card}`\n💰 Сумма: {price} сум\n\n📸 Отправьте скриншот чека об оплате.",
        'order_sent': "✅ Чек принят! UC будут отправлены после проверки.",
        'order_approved': "✅ Ваш заказ подтверждён! UC скоро будут отправлены.",
        'order_rejected': "❌ Ваш заказ отклонён. Попробуйте снова.",
        'no_orders': "📭 У вас пока нет заказов.",
        'support_txt': "📞 Поддержка: @yuksak_it\n📱 Тел: +998 50 777 51 52",
        'banned': "🚫 Вы заблокированы!",
        'cancelled': "❌ Заказ отменён.",
        'topup_success': "✅ *Ваш баланс в PUBG успешно пополнен!*\n\n🚀 Лучший, самый качественный и надежный сервис — только у нас! Спасибо, что выбираете нас! 🎮",
    },
    'en': {
        'choose_lang': "Choose language:",
        'welcome': "🎮 Welcome to *PUBG UC SHOP*!\nBuy UC for PUBG Mobile here.",
        'req_contact': "📱 Share your phone number:",
        'contact_btn': "📱 Share Contact",
        'main_menu': "🏠 Main menu:",
        'buy_uc': "🛒 Buy UC",
        'my_orders': "📦 My Orders",
        'profile': "👤 Profile",
        'support': "📞 Support",
        'back': "⬅️ Back",
        'choose_pkg': "📦 Choose a UC package:",
        'enter_id': "🎮 Send your PUBG Player ID:",
        'enter_nick': "👤 Send your PUBG nickname:",
        'confirm': "✅ *Confirm your order:*\n\n📦 Package: {pkg}\n💰 Price: {price} UZS\n🎮 Player ID: {pid}\n👤 Nickname: {nick}\n\nIs this correct?",
        'yes': "✅ Confirm",
        'no': "❌ Cancel",
        'pay_info': "💳 *Payment details:*\n\n💳 Card: `{card}`\n💰 Amount: {price} UZS\n\n📸 Send a screenshot of your payment receipt.",
        'order_sent': "✅ Receipt received! UC will be sent after verification.",
        'order_approved': "✅ Your order is confirmed! UC will be sent soon.",
        'order_rejected': "❌ Your order was rejected. Please try again.",
        'no_orders': "📭 You have no orders yet.",
        'support_txt': "📞 Support: @yuksak_it\n📱 Tel: +998 50 777 51 52",
        'banned': "🚫 You are banned!",
        'cancelled': "❌ Order cancelled.",
        'topup_success': "✅ *Your PUBG balance has been successfully topped up!*\n\n🚀 The best, highest quality, and most reliable service is only with us! Thank you for choosing us! 🎮",
    }
}

# ===== DATABASE =====
DB = "pubg.db"
lock = threading.Lock()

def init_db():
    with lock:
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, name TEXT, username TEXT, phone TEXT,
            lang TEXT, step TEXT DEFAULT 'lang', banned INTEGER DEFAULT 0,
            temp_pkg TEXT, temp_pid TEXT, temp_nick TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, pkg TEXT,
            player_id TEXT, nickname TEXT, price INTEGER, status TEXT DEFAULT 'pending',
            receipt_id TEXT, created TEXT
        )""")
        c.commit(); c.close()

def get_user(uid):
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    r = c.execute("SELECT * FROM users WHERE id=?", (str(uid),)).fetchone(); c.close()
    return dict(r) if r else None

def save_user(uid, **kw):
    cols = ", ".join([f"{k}=?" for k in kw]); vals = list(kw.values()) + [str(uid)]
    with lock:
        c = sqlite3.connect(DB); c.execute(f"UPDATE users SET {cols} WHERE id=?", vals); c.commit(); c.close()

def create_user(uid, name, uname):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?,?,?)", (str(uid), name, uname))
        c.commit(); c.close()

def add_order(uid, pkg, pid, nick, price, receipt_id):
    with lock:
        c = sqlite3.connect(DB)
        c.execute("INSERT INTO orders (user_id, pkg, player_id, nickname, price, receipt_id, created) VALUES (?,?,?,?,?,?,?)",
                  (str(uid), pkg, pid, nick, price, receipt_id, time.strftime('%Y-%m-%d %H:%M:%S')))
        c.commit(); c.close()

def get_orders(uid=None, status=None):
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    q = "SELECT * FROM orders"; params = []; conds = []
    if uid: conds.append("user_id=?"); params.append(str(uid))
    if status: conds.append("status=?"); params.append(status)
    if conds: q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY id DESC"
    rows = c.execute(q, params).fetchall(); c.close()
    return [dict(r) for r in rows]

def update_order(oid, **kw):
    cols = ", ".join([f"{k}=?" for k in kw]); vals = list(kw.values()) + [oid]
    with lock:
        c = sqlite3.connect(DB); c.execute(f"UPDATE orders SET {cols} WHERE id=?", vals); c.commit(); c.close()

def get_all_users():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    rows = c.execute("SELECT * FROM users").fetchall(); c.close()
    return [dict(r) for r in rows]

# ===== TELEGRAM API =====
def send_msg(cid, text, kb=None):
    p = {'chat_id': cid, 'text': text, 'parse_mode': 'Markdown'}
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except:
        p.pop('parse_mode', None)
        try:
            urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
            return True
        except: return False

def send_photo(cid, photo_id, caption=None, kb=None):
    p = {'chat_id': cid, 'photo': photo_id, 'parse_mode': 'Markdown'}
    if caption: p['caption'] = caption
    if kb: p['reply_markup'] = json.dumps(kb)
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data=urllib.parse.urlencode(p).encode('utf-8'))
        return True
    except: return False

def answer_cb(cb_id):
    try: urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", data=urllib.parse.urlencode({'callback_query_id': cb_id}).encode('utf-8'))
    except: pass

# ===== KEYBOARDS =====
def main_kb(lang):
    t = TEXTS.get(lang, TEXTS['uz'])
    return {"keyboard": [[{"text": t['buy_uc']}], [{"text": t['my_orders']}, {"text": t['profile']}], [{"text": t['support']}]], "resize_keyboard": True}

def pkg_kb(lang):
    t = TEXTS.get(lang, TEXTS['uz'])
    cur = "сум" if lang == 'ru' else ("UZS" if lang == 'en' else "so'm")
    rows = [[{"text": f"🎮 {p[0]} — {p[2]:,} {cur}"}] for p in PACKAGES]
    rows.append([{"text": t['back']}])
    return {"keyboard": rows, "resize_keyboard": True}

# ===== HANDLER =====
def handle(upd):
    # Callback queries (admin approve/reject)
    if 'callback_query' in upd:
        cq = upd['callback_query']; cid = cq['message']['chat']['id']; uid = str(cq['from']['id']); data = cq['data']
        answer_cb(cq['id'])
        if uid not in OWNER_IDS: return
        # Format: order_ok_ID or order_no_ID or order_fake_ID
        if data.startswith('topup_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found for top-up.")
                return
            target_uid = order['user_id']
            uc_pkg = order['pkg']
            nickname = order['nickname']
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            success_text = t_user.get('topup_success', "✅ Ваш баланс в PUBG пополнен!")
            
            for aid in OWNER_IDS:
                send_msg(aid, f"✅ Пополнение аккаунта: ID {target_uid}, ник {nickname}, {uc_pkg}.")
            send_msg(target_uid, success_text)
            send_msg(cid, f"✅ Top-up for order #{oid} processed.")
            return
            
        if data.startswith('order_topup_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='completed')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            success_text = t_user.get('topup_success', "✅ Ваш баланс в PUBG пополнен!")
            
            send_msg(target_uid, success_text)
            send_msg(cid, f"✅ Order #{oid} marked as topped up.")
            return

        if data.startswith('order_ok_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='approved')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            send_msg(target_uid, t_user['order_approved'])
            
            kb = {"inline_keyboard": [[
                {"text": "🚀 ТОП-АП", "callback_data": f"order_topup_{oid}"}
            ]]}
            send_msg(cid, f"✅ Заказ #{oid} подтвержден. Нажмите кнопку ниже после пополнения аккаунта:", kb=kb)
            return

        if data.startswith('order_no_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='rejected')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            send_msg(target_uid, t_user['order_rejected'])
            
            send_msg(cid, f"❌ Заказ #{oid} отклонен.")
            return

        if data.startswith('order_fake_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(cid, f"⚠️ Order #{oid} not found.")
                return
            target_uid = order['user_id']
            update_order(oid, status='fake')
            
            target_user = get_user(target_uid)
            lang = target_user.get('lang') or 'uz'
            t_user = TEXTS.get(lang, TEXTS['uz'])
            send_msg(target_uid, t_user['order_rejected'])
            
            send_msg(cid, f"🚫 Заказ #{oid} отмечен как FAKE.")
            return

        if data.startswith('uc_received_'):
            oid = int(data.split('_')[-1])
            order = next((o for o in get_orders() if o['id'] == oid), None)
            if not order:
                send_msg(uid, f"⚠️ Заказ #{oid} не найден.")
                return
            target_uid = order['user_id']
            update_order(oid, status='delivered')
            send_msg(target_uid, "✅ Спасибо! UC успешно получено и зачислено.")
            for aid in OWNER_IDS:
                send_msg(aid, f"🔔 Пользователь подтвердил получение UC для заказа #{oid}.")
            return

        return

    if 'message' not in upd: return
    m = upd['message']; cid = m['chat']['id']; uid = str(m['from']['id'])
    txt = m.get('text', '').strip()
    is_owner = uid in OWNER_IDS

    u = get_user(uid)
    if not u:
        create_user(uid, m['from'].get('first_name', 'User'), m['from'].get('username', ''))
        u = get_user(uid)

    if u.get('banned') and not is_owner:
        send_msg(cid, "🚫 BAN!"); return

    lang = u.get('lang') or 'uz'
    t = TEXTS.get(lang, TEXTS['uz'])

    # /start
    if txt in ['/start', 'Старт', '▶️ Старт', '/start@PubgUcShopBot']:
        save_user(uid, step='lang', lang=None)
        send_msg(cid, "🎮 *PUBG UC SHOP*\n\nTilni tanlang / Выберите язык / Choose language:",
                 kb={"keyboard": [[{"text": "🇺🇿 O'zbekcha"}, {"text": "🇷🇺 Русский"}, {"text": "🇺🇸 English"}]], "resize_keyboard": True})
        return

    # Admin panel
    if txt == '/admin' and is_owner:
        save_user(uid, step='admin')
        kb = {"keyboard": [
            [{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}],
            [{"text": "📢 Broadcast"}, {"text": "⬅️ Main Menu"}]
        ], "resize_keyboard": True}
        send_msg(cid, "🛠️ *Admin Panel*", kb=kb); return

    if is_owner and u.get('step') == 'admin':
        if txt == "🔍 Pending Orders":
            pending = get_orders(status='pending')
            if not pending: send_msg(cid, "✅ No pending orders."); return
            for o in pending[:10]:
                ou = get_user(o['user_id'])
                oname = ou.get('name', '?') if ou else '?'
                msg = f"📦 *Order #{o['id']}*\n👤 {oname} (`{o['user_id']}`)\n🎮 PID: `{o['player_id']}`\n👤 Nick: `{o['nickname']}`\n📦 {o['pkg']}\n💰 {o['price']:,}\n📅 {o['created']}"
                kb = {"inline_keyboard": [[
                    {"text": "✅ OK", "callback_data": f"order_ok_{o['id']}"},
                    {"text": "❌ NO", "callback_data": f"order_no_{o['id']}"},
                    {"text": "🚫 FAKE", "callback_data": f"order_fake_{o['id']}"},
                    {"text": "🚀 ТОП-АП", "callback_data": f"order_topup_{o['id']}"}
                ]]}
                if o.get('receipt_id'):
                    send_photo(cid, o['receipt_id'], caption=msg, kb=kb)
                else:
                    send_msg(cid, msg, kb=kb)
            return
        elif txt == "📊 Stats":
            all_u = get_all_users(); all_o = get_orders()
            completed = [o for o in all_o if o['status'] == 'completed']
            pending = [o for o in all_o if o['status'] == 'pending']
            revenue = sum(o['price'] for o in completed)
            send_msg(cid, f"📊 *Statistics:*\n\n👥 Users: {len(all_u)}\n📦 Total orders: {len(all_o)}\n✅ Completed: {len(completed)}\n⏳ Pending: {len(pending)}\n💰 Revenue: {revenue:,} UZS")
            return
        elif txt == "📢 Broadcast":
            save_user(uid, step='admin_broadcast')
            send_msg(cid, "📢 Send the message to broadcast to all users:", kb={"keyboard": [[{"text": "⬅️ Cancel"}]], "resize_keyboard": True})
            return
        elif txt == "⬅️ Main Menu":
            save_user(uid, step='main')
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            return
# Removed obsolete handling of '❌ Не удалять бота' button


    if is_owner and u.get('step') == 'admin_broadcast':
        if txt in ["⬅️ Cancel", "/admin"]:
            save_user(uid, step='admin')
            send_msg(cid, "Cancelled.", kb={"keyboard": [[{"text": "🔍 Pending Orders"}, {"text": "📊 Stats"}], [{"text": "📢 Broadcast"}, {"text": "⬅️ Main Menu"}]], "resize_keyboard": True})
            return
        all_u = get_all_users(); cnt = 0
        for usr in all_u:
            if send_msg(usr['id'], f"📢 *Announcement:*\n\n{txt}"): cnt += 1
            time.sleep(0.05)
        save_user(uid, step='admin')
        send_msg(cid, f"✅ Sent to {cnt} users.")
        return

    # Back button (universal)
    if txt == t['back']:
        save_user(uid, step='main')
        send_msg(cid, t['main_menu'], kb=main_kb(lang)); return

    # Language selection
    if u.get('step') == 'lang':
        if "O'z" in txt: lang = 'uz'
        elif "Рус" in txt: lang = 'ru'
        elif "Eng" in txt: lang = 'en'
        else: return
        save_user(uid, lang=lang, step='contact')
        t = TEXTS[lang]
        send_msg(cid, t['welcome'])
        send_msg(cid, t['req_contact'], kb={"keyboard": [[{"text": t['contact_btn'], "request_contact": True}]], "resize_keyboard": True})
        return

    # Contact
    if 'contact' in m:
        save_user(uid, phone=m['contact']['phone_number'], step='main')
        send_msg(cid, t['main_menu'], kb=main_kb(lang)); return

    # Main menu buttons
    if txt == t['buy_uc']:
        save_user(uid, step='choose_pkg')
        send_msg(cid, t['choose_pkg'], kb=pkg_kb(lang)); return

    if txt == t['my_orders']:
        orders = get_orders(uid=uid)
        if not orders: send_msg(cid, t['no_orders']); return
        for o in orders[:5]:
            st = {"pending": "⏳", "completed": "✅", "rejected": "❌"}.get(o['status'], "?")
            send_msg(cid, f"{st} *#{o['id']}* | {o['pkg']} | {o['price']:,} | {o['created']}")
        return

    if txt == t['profile']:
        send_msg(cid, f"👤 *{'Profil' if lang=='uz' else ('Профиль' if lang=='ru' else 'Profile')}*\n\n🆔 ID: `{uid}`\n👤 {u.get('name','?')}\n📱 {u.get('phone', '-')}")
        return

    if txt == t['support']:
        send_msg(cid, t['support_txt']); return

    # Choose package
    if u.get('step') == 'choose_pkg' and txt:
        pkg = None
        for p in PACKAGES:
            if p[0] in txt: pkg = p; break
        if not pkg: return
        save_user(uid, step='enter_pid', temp_pkg=f"{pkg[0]}||{pkg[2]}")
        send_msg(cid, t['enter_id'], kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
        return

    # Enter Player ID
    if u.get('step') == 'enter_pid' and txt:
        save_user(uid, step='enter_nick', temp_pid=txt)
        send_msg(cid, t['enter_nick'], kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
        return

    # Enter Nickname
    if u.get('step') == 'enter_nick' and txt:
        save_user(uid, step='confirm_order', temp_nick=txt)
        pkg_info = u.get('temp_pkg', '60 UC||15000').split("||")
        pkg_name, price = pkg_info[0], int(pkg_info[1])
        msg = t['confirm'].format(pkg=pkg_name, price=f"{price:,}", pid=u.get('temp_pid', '?'), nick=txt)
        send_msg(cid, msg, kb={"keyboard": [[{"text": t['yes']}, {"text": t['no']}]], "resize_keyboard": True})
        return

    # Confirm order
    if u.get('step') == 'confirm_order':
        if txt == t['yes']:
            pkg_info = u.get('temp_pkg', '60 UC||15000').split("||")
            price = int(pkg_info[1])
            save_user(uid, step='awaiting_receipt')
            send_msg(cid, t['pay_info'].format(card=CARD, price=f"{price:,}"),
                     kb={"keyboard": [[{"text": t['back']}]], "resize_keyboard": True})
            return
        elif txt == t['no']:
            save_user(uid, step='main')
            send_msg(cid, t['cancelled'])
            send_msg(cid, t['main_menu'], kb=main_kb(lang))
            return

    # Receipt photo
    if 'photo' in m and u.get('step') == 'awaiting_receipt':
        photo_id = m['photo'][-1]['file_id']
        pkg_info = u.get('temp_pkg', '60 UC||15000').split("||")
        pkg_name, price = pkg_info[0], int(pkg_info[1])
        pid = u.get('temp_pid', '?')
        nick = u.get('temp_nick', '?')
        add_order(uid, pkg_name, pid, nick, price, photo_id)
        save_user(uid, step='main')
        send_msg(cid, t['order_sent'])
        send_msg(cid, t['main_menu'], kb=main_kb(lang))
        # Notify admin
        orders = get_orders(uid=uid, status='pending')
        if orders:
            o = orders[0]
            admin_msg = f"🔔 *NEW ORDER!*\n\n👤 {u.get('name','?')} (@{u.get('username','?')})\n🆔 `{uid}`\n📱 {u.get('phone','-')}\n🎮 PID: `{pid}`\n👤 Nick: {nick}\n📦 {pkg_name}\n💰 {price:,} UZS"
            kb = {"inline_keyboard": [[
                {"text": "✅ OK", "callback_data": f"order_ok_{o['id']}"},
                {"text": "❌ NO", "callback_data": f"order_no_{o['id']}"},
                {"text": "🚫 FAKE", "callback_data": f"order_fake_{o['id']}"}
            ]]}
            for oid in OWNER_IDS:
                send_photo(oid, photo_id, caption=admin_msg, kb=kb)
        return

def main():
    init_db(); keep_alive(); offset = 0
    print("🎮 PUBG UC Shop Bot started!")
    with ThreadPoolExecutor(max_workers=20) as ex:
        while True:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=15"
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for upd in data.get('result', []):
                        offset = upd['update_id'] + 1; ex.submit(handle, upd)
            except: time.sleep(0.5)

if __name__ == "__main__": main()
