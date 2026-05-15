import asyncio
import os
import re
import yt_dlp
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Конфигурация
TELEGRAM_TOKEN = '8688180166:AAFGxxJ6qs0eWTTaS9R5GFQR3hpIytgXBvM'
GEMINI_API_KEY = 'AIzaSyBhOu1-NR6C8PYSqhlWml7YVZ8J0_KOt4Y'

# Gemini созламалари
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def download_instagram_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Салом! Мен Instagram видеоларини юклаб бераман ва Gemini AI ёрдамида саволларингизга жавоб бераман. Шунчаки линк ёки савол юборинг."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    # Инстаграм линкини текшириш
    if "instagram.com" in text:
        msg = await context.bot.send_message(chat_id=chat_id, text="Видео тайёрланмоқда, илтимос кутинг...")
        try:
            video_path = await asyncio.to_thread(download_instagram_video, text)
            if os.path.exists(video_path):
                await context.bot.send_video(chat_id=chat_id, video=open(video_path, 'rb'))
                await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                os.remove(video_path)
            else:
                await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="Видео топилмади.")
        except Exception as e:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"Хатолик: {str(e)}")
    else:
        # Gemini AI орқали жавоб бериш
        try:
            response = model.generate_content(text)
            await context.bot.send_message(chat_id=chat_id, text=response.text)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Gemini AI хатолиги: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("Бот ишга тушди (Standalone mode)...")
    application.run_polling()
