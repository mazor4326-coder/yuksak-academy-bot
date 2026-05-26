import os
import time
import sqlite3
import threading
import atexit
from flask import Flask
from dotenv import load_dotenv
import telebot
from telebot import types

# Load .env file
load_dotenv()

# Write PID to file for stopping easily
with open("bot.pid", "w") as f:
    f.write(str(os.getpid()))

@atexit.register
def remove_pid_file():
    if os.path.exists("bot.pid"):
        try:
            os.remove("bot.pid")
        except:
            pass

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = os.getenv("OWNER_IDS", "").split(",")

# Initialize Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Web server for Render health checks
app = Flask('')
@app.route('/')
def home():
    return "OMAVIY2026 Ad-Posting Bot is running!"

def run():
    try:
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except:
        pass

def keep_alive():
    threading.Thread(target=run, daemon=True).start()

# DATABASE
DB_NAME = "promo.db"
class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.lock = threading.Lock()
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.lock:
            conn = self.get_conn()
            curr = conn.cursor()
            curr.execute("""CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                username TEXT,
                phone TEXT,
                lang TEXT,
                sub_status TEXT DEFAULT 'none',
                sub_expire TEXT,
                step TEXT
            )""")
            curr.execute("""CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                text TEXT,
                photo TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )""")
            curr.execute("""CREATE TABLE IF NOT EXISTS groups (
                chat_id TEXT PRIMARY KEY,
                title TEXT
            )""")
            conn.commit()
            conn.close()

    def get_user(self, uid):
        conn = self.get_conn()
        r = conn.execute("SELECT * FROM users WHERE id=?", (str(uid),)).fetchone()
        conn.close()
        return dict(r) if r else None

    def create_user(self, uid, name, username):
        with self.lock:
            conn = self.get_conn()
            conn.execute("INSERT OR IGNORE INTO users (id, name, username, step) VALUES (?,?,?,?)", (str(uid), name, username, 'lang'))
            conn.commit()
            conn.close()

    def update_user(self, uid, **kwargs):
        cols = ", ".join([f"{k}=?" for k in kwargs.keys()])
        vals = list(kwargs.values()) + [str(uid)]
        with self.lock:
            conn = self.get_conn()
            conn.execute(f"UPDATE users SET {cols} WHERE id=?", vals)
            conn.commit()
            conn.close()

    def add_group(self, chat_id, title):
        with self.lock:
            conn = self.get_conn()
            conn.execute("INSERT OR REPLACE INTO groups (chat_id, title) VALUES (?,?)", (str(chat_id), title))
            conn.commit()
            conn.close()

    def remove_group(self, chat_id):
        with self.lock:
            conn = self.get_conn()
            conn.execute("DELETE FROM groups WHERE chat_id=?", (str(chat_id),))
            conn.commit()
            conn.close()

    def get_groups(self):
        conn = self.get_conn()
        rows = conn.execute("SELECT * FROM groups").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_users(self):
        conn = self.get_conn()
        rows = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_ad(self, user_id, text, photo):
        with self.lock:
            conn = self.get_conn()
            curr = conn.cursor()
            curr.execute("INSERT INTO ads (user_id, text, photo, created_at) VALUES (?,?,?,?)",
                         (str(user_id), text, photo, time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()

    def get_user_ads_count(self, user_id):
        conn = self.get_conn()
        r = conn.execute("SELECT COUNT(*) FROM ads WHERE user_id=?", (str(user_id),)).fetchone()
        conn.close()
        return r[0] if r else 0

db = Database(DB_NAME)

# LOCALISED TEXTS
TEXTS = {
    'ru': {
        'welcome': "Assalomu alaykum! Добро пожаловать в наш бот массовой рекламы.",
        'req_contact': "Пожалуйста, поделитесь вашим номером телефона для регистрации.",
        'thanks_reg': "Спасибо за регистрацию! Теперь вам доступно главное меню.",
        'main_menu': "🏠 Главное меню:",
        'profile_btn': "👤 Мой профиль",
        'post_ad_btn': "📣 Разместить рекламу",
        'buy_sub_btn': "💳 Купить подписку",
        'change_lang_btn': "🌐 Изменить язык",
        'back_btn': "⬅️ Назад",
        'no_photo_btn': "❌ Без фото",
        'publish_btn': "🚀 Опубликовать в группы/каналы",
        'sub_active': "✅ Активна (до {expire})",
        'sub_none': "❌ Отсутствует",
        'profile_txt': "👤 *Ваш профиль:*\n\n📞 Телефон: `{phone}`\n💎 Подписка: *{sub}*\n📣 Всего объявлений: `{ads_count}`",
        'buy_sub_txt': "💳 *КУПИТЬ ПОДПИСКУ (20,000 сум / 30 дней)*\n\nДля оплаты переведите средства на одну из карт:\n\n💳 HUMO: `9860 1604 2025 6085` (KAMOLOV A.)\n💳 UZCARD: `5440 8100 1696 6946` (KAMOLOV A.)\n\n📸 *После оплаты обязательно отправьте сюда скриншот или фото чека.* Наш администратор проверит платеж и активирует вам подписку.",
        'no_sub_warn': "🔒 Размещение рекламы доступно только пользователям с активной подпиской.\n\nПожалуйста, перейдите в раздел «💳 Купить подписку» для активации.",
        'create_ad_txt': "✍️ *Введите текст вашего объявления:*\n\nОно будет отправлено во все наши группы и каналы рекламы.",
        'create_ad_photo': "📸 *Отправьте изображение для вашего объявления:*\n\nЕсли фото не требуется, нажмите кнопку ниже.",
        'ad_preview': "📝 *Предпросмотр объявления:*\n\n{text}\n\nХотите опубликовать его?",
        'ad_posted_success': "🚀 Ваше объявление успешно разослано во все группы и каналы!",
        'payment_pending': "✅ Ваша квитанция отправлена администратору на проверку. Мы уведомим вас об активации подписки!",
        'group_not_found': "Не найдено активных групп или каналов для размещения объявлений. Пожалуйста, свяжитесь с поддержкой."
    },
    'uz': {
        'welcome': "Assalomu alaykum! Ommaviy reklama botimizga xush kelibsiz.",
        'req_contact': "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.",
        'thanks_reg': "Ro'yxatdan o'tganingiz uchun tashakkur! Endi siz bosh menyudan foydalanishingiz mumkin.",
        'main_menu': "🏠 Bosh menyu:",
        'profile_btn': "👤 Mening profilim",
        'post_ad_btn': "📣 Reklama joylashtirish",
        'buy_sub_btn': "💳 Obuna sotib olish",
        'change_lang_btn': "🌐 Tilni o'zgartirish",
        'back_btn': "⬅️ Orqaga",
        'no_photo_btn': "❌ Rasm yo'q",
        'publish_btn': "🚀 Guruh va kanallarga yuklash",
        'sub_active': "✅ Faol ({expire} gacha)",
        'sub_none': "❌ Mavjud emas",
        'profile_txt': "👤 *Sizning profilingiz:*\n\n📞 Telefon: `{phone}`\n💎 Obuna: *{sub}*\n📣 Jami e'lonlar: `{ads_count}`",
        'buy_sub_txt': "💳 *OBUNA SOTIB OLISH (20 000 so'm / 30 kun)*\n\nTo'lov uchun quyidagi kartalardan biriga pul o'tkazing:\n\n💳 HUMO: `9860 1604 2025 6085` (KAMOLOV A.)\n💳 UZCARD: `5440 8100 1696 6946` (KAMOLOV A.)\n\n📸 *To'lovdan so'ng skrinshot yoki rasm (chek)ni yuboring.* Administrator to'lovni tekshirib, obunangizni faollashtiradi.",
        'no_sub_warn': "🔒 E'lon joylashtirish faqat faol obunaga ega foydalanuvchilar uchun ruxsat etiladi.\n\nIltimos, faollashtirish uchun «💳 Obuna sotib olish» bo'limiga o'ting.",
        'create_ad_txt': "✍️ *E'loningiz matnini kiriting:*\n\nU barcha reklama guruhlari va kanallariga yuboriladi.",
        'create_ad_photo': "📸 *E'lon uchun rasm yuboring:*\n\nAgar rasm kerak bo'lmasa, quyidagi tugmani bosing.",
        'ad_preview': "📝 *E'lonning ko'rinishi:*\n\n{text}\n\nUshbu e'lonni guruh va kanallarga joylashtirishni xohlaysizmi?",
        'ad_posted_success': "🚀 E'loningiz barcha guruh va kanallarga muvaffaqiyatli yuborildi!",
        'payment_pending': "✅ Chekingiz administratorga tekshirish uchun yuborildi. Obuna faollashishi bilanoq sizga xabar beramiz!",
        'group_not_found': "E'lon joylashtirish uchun faol guruhlar yoki kanallar topilmadi. Iltimos, qo'llab-quvvatlash xizmatiga murojaat qiling."
    }
}

# In-memory temporary storage for advertisements being created
user_ads_in_progress = {}

# Dynamic Expiration Checker
def check_and_update_subscription(uid, u):
    if u and u.get('sub_status') == 'active' and u.get('sub_expire'):
        try:
            expire_time = time.strptime(u['sub_expire'], '%Y-%m-%d %H:%M:%S')
            if time.time() > time.mktime(expire_time):
                db.update_user(uid, sub_status='none', sub_expire=None)
                u['sub_status'] = 'none'
                u['sub_expire'] = None

                # Notify user
                t_lang = u.get('lang', 'ru')
                msg = {
                    'ru': "⚠️ Срок действия вашей подписки истек. Пожалуйста, продлите её в разделе «Купить подписку».",
                    'uz': "⚠️ Obunangiz muddati tugadi. Iltimos, «Obuna sotib olish» bo'limida uni uzaytiring."
                }
                try:
                    bot.send_message(uid, msg.get(t_lang, msg['ru']))
                except:
                    pass
                return True
        except Exception as e:
            print(f"Error checking sub expiration: {e}")
    return False

# Keyboards
def get_lang_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🇺🇿 O'zbekcha", "🇷🇺 Русский")
    return kb

def get_contact_kb(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_text = "📱 Telefon yuborish" if lang == 'uz' else "📱 Поделиться контактом"
    kb.add(types.KeyboardButton(btn_text, request_contact=True))
    return kb

def get_main_kb(uid, lang, is_owner):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    t = TEXTS.get(lang, TEXTS['ru'])
    kb.row(t['profile_btn'], t['post_ad_btn'])
    kb.row(t['buy_sub_btn'], t['change_lang_btn'])
    if is_owner:
        kb.row("🛠️ Admin panel")
    return kb

def get_admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📊 Статистика", "📢 Рассылка")
    kb.row("👥 Группы и Каналы", "⬅️ В меню")
    return kb

def get_groups_mgmt_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➕ Добавить группу/канал", "🗑️ Список/Удалить")
    kb.row("⬅️ Назад")
    return kb

# Posting Logic
def post_ad_to_all_groups(user_id, text, photo_id):
    groups = db.get_groups()
    if not groups:
        return False

    sent_count = 0
    for g in groups:
        chat_id = g['chat_id']
        try:
            if photo_id:
                try:
                    bot.send_photo(chat_id, photo_id, caption=text, parse_mode='Markdown')
                except:
                    bot.send_photo(chat_id, photo_id, caption=text)
            else:
                try:
                    bot.send_message(chat_id, text, parse_mode='Markdown')
                except:
                    bot.send_message(chat_id, text)
            sent_count += 1
            time.sleep(0.1)
        except Exception as e:
            print(f"Error sending ad to group {chat_id}: {e}")

    db.add_ad(user_id, text, photo_id)
    return sent_count > 0

# Start Command
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid = str(m.from_user.id)
    db.create_user(uid, m.from_user.first_name or "User", m.from_user.username or "None")
    db.update_user(uid, step='lang')
    bot.send_message(m.chat.id, "Tilni tanlang / Выберите язык:", reply_markup=get_lang_kb())

# Handler for everything
@bot.message_handler(func=lambda message: True, content_types=['text', 'contact', 'photo'])
def handle_all_messages(m):
    uid = str(m.from_user.id)
    u = db.get_user(uid)
    if not u:
        db.create_user(uid, m.from_user.first_name or "User", m.from_user.username or "None")
        u = db.get_user(uid)

    is_owner = uid in OWNER_IDS
    check_and_update_subscription(uid, u)

    lang = u.get('lang', 'ru')
    step = u.get('step', 'lang')
    cid = m.chat.id

    # 1. Choose Language
    if step == 'lang':
        if m.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"]:
            lang_code = 'uz' if "O'z" in m.text else 'ru'
            db.update_user(uid, lang=lang_code, step='contact')
            t = TEXTS[lang_code]
            bot.send_message(cid, t['welcome'])
            bot.send_message(cid, t['req_contact'], reply_markup=get_contact_kb(lang_code))
        else:
            bot.send_message(cid, "Tilni tanlang / Выберите язык:", reply_markup=get_lang_kb())
        return

    # 2. Registration Contact
    if step == 'contact':
        if m.content_type == 'contact' and m.contact:
            db.update_user(uid, phone=m.contact.phone_number, step='main')
            t = TEXTS[lang]
            bot.send_message(cid, t['thanks_reg'])
            bot.send_message(cid, t['main_menu'], reply_markup=get_main_kb(uid, lang, is_owner))
        else:
            bot.send_message(cid, TEXTS[lang]['req_contact'], reply_markup=get_contact_kb(lang))
        return

    # Admin Panel invocation
    if m.text == "/admin" or (m.text == "🛠️ Admin panel" and is_owner):
        db.update_user(uid, step='admin_main')
        bot.send_message(cid, "🛠️ *Панель администратора*", parse_mode='Markdown', reply_markup=get_admin_kb())
        return

    # Owner Handlers
    if is_owner:
        if m.text == "⬅️ В меню":
            db.update_user(uid, step='main')
            bot.send_message(cid, TEXTS[lang]['main_menu'], reply_markup=get_main_kb(uid, lang, is_owner))
            return

        if step == 'admin_main':
            if m.text == "📊 Статистика":
                users = db.get_all_users()
                groups = db.get_groups()
                total_users = len(users)
                active_subs = len([x for x in users if x.get('sub_status') == 'active'])
                total_groups = len(groups)

                stats_msg = (
                    f"📊 *СТАТИСТИКА БОТА:*\n\n"
                    f"👥 Всего пользователей: `{total_users}`\n"
                    f"💎 Активных подписок: `{active_subs}`\n"
                    f"📢 Целевых групп: `{total_groups}`"
                )
                bot.send_message(cid, stats_msg, parse_mode='Markdown', reply_markup=get_admin_kb())
                return

            elif m.text == "📢 Рассылка":
                db.update_user(uid, step='admin_broadcast')
                bot.send_message(cid, "📢 *Отправьте сообщение для рассылки (текст или фото с описанием):*", parse_mode='Markdown', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад"))
                return

            elif m.text == "👥 Группы и Каналы":
                db.update_user(uid, step='admin_groups_mgmt')
                bot.send_message(cid, "👥 *Управление целевыми группами и каналами:*", parse_mode='Markdown', reply_markup=get_groups_mgmt_kb())
                return

        elif step == 'admin_groups_mgmt':
            if m.text == "⬅️ Назад":
                db.update_user(uid, step='admin_main')
                bot.send_message(cid, "🛠️ *Панель администратора*", parse_mode='Markdown', reply_markup=get_admin_kb())
                return

            elif m.text == "➕ Добавить группу/канал":
                db.update_user(uid, step='admin_add_group')
                bot.send_message(cid, "➕ *Добавление группы или канала:*\n\nОтправьте ID (начинается с `-100` для супергрупп/каналов) или юзернейм (например, `@mychannel`), либо перешлите пост из канала / сообщение из группы:", parse_mode='Markdown', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад"))
                return

            elif m.text == "🗑️ Список/Удалить":
                groups = db.get_groups()
                if not groups:
                    bot.send_message(cid, "📭 Список пуст.", reply_markup=get_groups_mgmt_kb())
                    return

                markup = types.InlineKeyboardMarkup()
                text_lines = ["📋 *Список групп и каналов:*"]
                for i, g in enumerate(groups):
                    title = g['title']
                    gid = g['chat_id']
                    text_lines.append(f"{i+1}. {title} (ID: `{gid}`)")
                    markup.add(types.InlineKeyboardButton(text=f"🗑️ Удалить: {title}", callback_data=f"del_grp_{gid}"))

                bot.send_message(cid, "\n".join(text_lines), reply_markup=markup, parse_mode='Markdown')
                return

        elif step == 'admin_add_group':
            if m.text == "⬅️ Назад":
                db.update_user(uid, step='admin_groups_mgmt')
                bot.send_message(cid, "👥 *Управление целевыми группами и каналами:*", parse_mode='Markdown', reply_markup=get_groups_mgmt_kb())
                return

            chat_id = None
            title = None
            if m.forward_from_chat:
                chat_id = m.forward_from_chat.id
                title = m.forward_from_chat.title or m.forward_from_chat.username or str(chat_id)
            else:
                text = m.text.strip()
                if text.startswith("@"):
                    chat_id = text
                elif "/" in text:
                    parts = text.split("/")
                    if parts[-1]:
                        chat_id = "@" + parts[-1]
                else:
                    try:
                        chat_id = int(text)
                    except ValueError:
                        chat_id = text

            if chat_id:
                try:
                    chat_info = bot.get_chat(chat_id)
                    chat_id = chat_info.id
                    title = chat_info.title or chat_info.username or str(chat_id)
                    db.add_group(chat_id, title)
                    bot.send_message(cid, f"✅ Успешно добавлено!\n📌 Название: *{title}*\n🆔 ID: `{chat_id}`", parse_mode='Markdown', reply_markup=get_groups_mgmt_kb())
                    db.update_user(uid, step='admin_groups_mgmt')
                except Exception as e:
                    bot.send_message(cid, f"❌ Ошибка добавления: {e}\n\nУбедитесь, что бот является участником/администратором этой группы или канала.")
            return

        elif step == 'admin_broadcast':
            if m.text == "⬅️ Назад":
                db.update_user(uid, step='admin_main')
                bot.send_message(cid, "🛠️ *Панель администратора*", parse_mode='Markdown', reply_markup=get_admin_kb())
                return

            all_u = db.get_all_users()
            sent_count = 0
            photo_id = m.photo[-1].file_id if m.content_type == 'photo' else None
            caption = m.caption or m.text

            bot.send_message(cid, f"📢 Началась рассылка для {len(all_u)} пользователей...")

            for user in all_u:
                user_id = user['id']
                try:
                    if photo_id:
                        bot.send_photo(user_id, photo_id, caption=caption, parse_mode='Markdown')
                    else:
                        bot.send_message(user_id, caption, parse_mode='Markdown')
                    sent_count += 1
                    time.sleep(0.05)
                except:
                    pass

            db.update_user(uid, step='admin_main')
            bot.send_message(cid, f"✅ Рассылка завершена. Успешно отправлено {sent_count} из {len(all_u)} пользователей.", reply_markup=get_admin_kb())
            return

    # Language Switcher
    if m.text == TEXTS[lang]['change_lang_btn']:
        db.update_user(uid, step='lang')
        bot.send_message(cid, "Tilni tanlang / Выберите язык:", reply_markup=get_lang_kb())
        return

    # User Profile
    if m.text == TEXTS[lang]['profile_btn']:
        ads_count = db.get_user_ads_count(uid)
        sub_status = u.get('sub_status', 'none')

        if sub_status == 'active':
            sub_text = TEXTS[lang]['sub_active'].format(expire=u.get('sub_expire', '-'))
        else:
            sub_text = TEXTS[lang]['sub_none']

        profile_msg = TEXTS[lang]['profile_txt'].format(
            phone=u.get('phone', '-'),
            sub=sub_text,
            ads_count=ads_count
        )
        bot.send_message(cid, profile_msg, parse_mode='Markdown', reply_markup=get_main_kb(uid, lang, is_owner))
        return

    # Buy Subscription
    if m.text == TEXTS[lang]['buy_sub_btn']:
        db.update_user(uid, step='awaiting_payment')
        bot.send_message(cid, TEXTS[lang]['buy_sub_txt'], parse_mode='Markdown', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(TEXTS[lang]['back_btn']))
        return

    # Handle Payment Photo Upload
    if m.content_type == 'photo' and step == 'awaiting_payment':
        caption = f"💳 *НОВЫЙ ЧЕК НА ОПЛАТУ (20 000 сум)*\n\n👤 Пользователь: {u.get('name')} (@{u.get('username')})\n🆔 ID: `{uid}`\n📱 Телефон: `{u.get('phone')}`"

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ Одобрить", callback_data=f"sub_approve_{uid}"),
            types.InlineKeyboardButton("❌ Отклонить", callback_data=f"sub_reject_{uid}")
        )

        for oid in OWNER_IDS:
            try:
                bot.send_photo(oid, m.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode='Markdown')
            except Exception as e:
                print(f"Error sending photo to owner {oid}: {e}")

        db.update_user(uid, step='main')
        bot.send_message(cid, TEXTS[lang]['payment_pending'], reply_markup=get_main_kb(uid, lang, is_owner))
        return

    # Create Ad Flow
    if m.text == TEXTS[lang]['post_ad_btn']:
        sub_status = u.get('sub_status', 'none')
        if sub_status != 'active' and not is_owner:
            bot.send_message(cid, TEXTS[lang]['no_sub_warn'], parse_mode='Markdown')
            return

        db.update_user(uid, step='ad_text')
        bot.send_message(cid, TEXTS[lang]['create_ad_txt'], parse_mode='Markdown', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(TEXTS[lang]['back_btn']))
        return

    # Back Handler (returns to main menu)
    if m.text == TEXTS[lang]['back_btn']:
        db.update_user(uid, step='main')
        bot.send_message(cid, TEXTS[lang]['main_menu'], reply_markup=get_main_kb(uid, lang, is_owner))
        return

    # State: Awaiting Ad Text
    if step == 'ad_text':
        if not m.text:
            bot.send_message(cid, TEXTS[lang]['create_ad_txt'], parse_mode='Markdown')
            return

        user_ads_in_progress[uid] = {'text': m.text, 'photo': None}
        db.update_user(uid, step='ad_photo')

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row(TEXTS[lang]['no_photo_btn'])
        kb.row(TEXTS[lang]['back_btn'])
        bot.send_message(cid, TEXTS[lang]['create_ad_photo'], parse_mode='Markdown', reply_markup=kb)
        return

    # State: Awaiting Ad Photo
    if step == 'ad_photo':
        photo_id = None
        if m.content_type == 'photo':
            photo_id = m.photo[-1].file_id
        elif m.text == TEXTS[lang]['no_photo_btn']:
            photo_id = None
        else:
            bot.send_message(cid, "Пожалуйста, отправьте фото или нажмите кнопку ниже.")
            return

        ad_in_progress = user_ads_in_progress.get(uid, {'text': ''})
        ad_in_progress['photo'] = photo_id
        user_ads_in_progress[uid] = ad_in_progress

        db.update_user(uid, step='ad_confirm')

        has_photo_str = "Да" if photo_id else "Нет" if lang == 'ru' else "Yo'q"
        preview_text = TEXTS[lang]['ad_preview'].format(
            text=ad_in_progress['text'],
            has_photo=has_photo_str
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row(TEXTS[lang]['publish_btn'])
        kb.row(TEXTS[lang]['back_btn'])

        if photo_id:
            try:
                bot.send_photo(cid, photo_id, caption=preview_text, reply_markup=kb, parse_mode='Markdown')
            except:
                bot.send_photo(cid, photo_id, caption=preview_text, reply_markup=kb)
        else:
            try:
                bot.send_message(cid, preview_text, reply_markup=kb, parse_mode='Markdown')
            except:
                bot.send_message(cid, preview_text, reply_markup=kb)
        return

    # State: Awaiting Ad Publish Confirmation
    if step == 'ad_confirm':
        if m.text == TEXTS[lang]['publish_btn']:
            ad = user_ads_in_progress.get(uid)
            if not ad:
                bot.send_message(cid, "Ошибка. Пожалуйста, начните заново.")
                db.update_user(uid, step='main')
                return

            groups = db.get_groups()
            if not groups:
                bot.send_message(cid, TEXTS[lang]['group_not_found'], reply_markup=get_main_kb(uid, lang, is_owner))
                db.update_user(uid, step='main')
                return

            msg_wait = bot.send_message(cid, "🔄 Публикация объявлений..." if lang == 'ru' else "🔄 E'lonlar joylashtirilmoqda...")
            success = post_ad_to_all_groups(uid, ad['text'], ad['photo'])
            bot.delete_message(cid, msg_wait.message_id)

            if success:
                bot.send_message(cid, TEXTS[lang]['ad_posted_success'], reply_markup=get_main_kb(uid, lang, is_owner))
            else:
                bot.send_message(cid, "Ошибка отправки в группы.", reply_markup=get_main_kb(uid, lang, is_owner))

            db.update_user(uid, step='main')
            user_ads_in_progress.pop(uid, None)
            return

    # Fall-through in main step
    if step == 'main':
        bot.send_message(cid, TEXTS[lang]['main_menu'], reply_markup=get_main_kb(uid, lang, is_owner))
        return

# Inline callback handler
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    cid = call.message.chat.id
    uid = str(call.from_user.id)
    is_owner = uid in OWNER_IDS
    data = call.data

    # Group deletion
    if data.startswith("del_grp_") and is_owner:
        gid = data.replace("del_grp_", "")
        db.remove_group(gid)
        bot.answer_callback_query(call.id, "Удалено успешно")
        bot.edit_message_text(f"✅ Группа/канал с ID {gid} удален из списка автопостинга.", chat_id=cid, message_id=call.message.message_id)

    # Subscription approvals
    elif data.startswith("sub_approve_") and is_owner:
        target_uid = data.replace("sub_approve_", "")
        exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 30*86400))
        db.update_user(target_uid, sub_status='active', sub_expire=exp)

        bot.answer_callback_query(call.id, "Подписка активирована")
        bot.edit_message_caption(caption=call.message.caption + "\n\n🟢 *Статус: Одобрено*", chat_id=cid, message_id=call.message.message_id, parse_mode='Markdown')

        target_u = db.get_user(target_uid)
        t_lang = target_u.get('lang', 'ru') if target_u else 'ru'
        msg_map = {
            'ru': f"🎉 Ваша подписка успешно активирована на 30 дней! До `{exp}`.",
            'uz': f"🎉 Obunangiz 30 kunga muvaffaqiyatli faollashtirildi! `{exp}` gacha."
        }
        try:
            bot.send_message(target_uid, msg_map.get(t_lang, msg_map['ru']), parse_mode='Markdown')
        except:
            pass

    elif data.startswith("sub_reject_") and is_owner:
        target_uid = data.replace("sub_reject_", "")
        bot.answer_callback_query(call.id, "Платеж отклонен")
        bot.edit_message_caption(caption=call.message.caption + "\n\n🔴 *Статус: Отклонено*", chat_id=cid, message_id=call.message.message_id, parse_mode='Markdown')

        target_u = db.get_user(target_uid)
        t_lang = target_u.get('lang', 'ru') if target_u else 'ru'
        msg_map = {
            'ru': "❌ Ваш платеж был отклонен администратором. Пожалуйста, проверьте квитанцию и повторите попытку.",
            'uz': "❌ To'lovingiz administrator tomonidan rad etildi. Iltimos, chekni tekshirib, qaytadan urinib ko'ring."
        }
        try:
            bot.send_message(target_uid, msg_map.get(t_lang, msg_map['ru']))
        except:
            pass

if __name__ == "__main__":
    keep_alive()
    print("[BOT] Removing webhook...")
    try:
        bot.remove_webhook()
    except Exception as e:
        print(f"[BOT] Error removing webhook: {e}")
    print("[BOT] Starting polling...")
    bot.infinity_polling(timeout=20, long_polling_timeout=15)
