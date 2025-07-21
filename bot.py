from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "ТВОЙ_ТОКЕН"
active_spams = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Используй /spam <текст> <кол-во> и /stop")

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if len(context.args) < 2:
        await update.message.reply_text("❗ Пример: /spam Привет 100")
        return

    text = context.args[0]
    try:
        count = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❗ Второй аргумент должен быть числом.")
        return

    active_spams[chat_id] = True
    await update.message.reply_text(f"🚀 Начинаю спам: {text} × {count}")

    sent = 0
    for _ in range(count):
        if not active_spams.get(chat_id):
            await update.message.reply_text("⛔ Спам остановлен.")
            break

        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
            sent += 1
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            break

    if active_spams.get(chat_id):
        await update.message.reply_text(f"✅ Спам завершён: {sent}/{count}")
    active_spams[chat_id] = False

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    active_spams[chat_id] = False
    await update.message.reply_text("🛑 Остановка спама...")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("stop", stop))
    print("✅ Бот запущен")
    app.run_polling()
