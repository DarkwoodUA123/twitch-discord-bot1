import os
import asyncio
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# Отправить сообщение в Discord
def send_to_discord(text):
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    json_data = {"content": text}
    response = requests.post(url, headers=headers, json=json_data)
    if response.ok:
        print("✅ Отправлено в Discord.")
    else:
        print(f"❌ Ошибка Discord: {response.status_code}, {response.text}")

# Получить Twitch access token
def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    resp = requests.post(url, params=params)
    if resp.ok:
        return resp.json().get("access_token")
    else:
        print(f"❌ Ошибка получения токена Twitch: {resp.status_code}, {resp.text}")
        return None

# Проверка, онлайн ли стрим
def is_stream_live():
    token = get_twitch_access_token()
    if not token:
        return False
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    if resp.ok:
        data = resp.json().get("data", [])
        return bool(data)
    else:
        print(f"❌ Ошибка Twitch API: {resp.status_code}, {resp.text}")
        return False

# Цикл проверки стрима
async def check_stream_periodically(app):
    notified = False
    while True:
        if is_stream_live():
            if not notified:
                # Стрим начался — отправить в ТГ-канал
                text = f"Кажется, стрим начинается... https://www.twitch.tv/{TWITCH_USERNAME}"
                await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=text)
                print("✅ Сообщение отправлено в Telegram-канал.")
                notified = True
        else:
            notified = False
        await asyncio.sleep(30)  # Проверка каждые 30 секунд

# Личные сообщения → Discord
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        user = update.message.from_user
        text = update.message.text
        message = f"[{user.first_name}]: {text}"
        send_to_discord(message)
        await update.message.reply_text("✅ Сообщение отправлено в Discord!")

# Запуск бота
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработка личных сообщений
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_private_message))

    # Запуск проверки стрима
    app.create_task(check_stream_periodically(app))

    print("🚀 Telegram-бот запущен и ждёт сообщений...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
