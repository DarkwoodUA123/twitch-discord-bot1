import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "6125133441:AAH1DmGzp-MyNUlR2S_48ce4jveDFCC6mqc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен. Используй /spam <текст> <кол-во>")

async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("❗ Использование: /spam <текст> <кол-во>")
            return

        text = args[0]
        count = int(args[1])
        chat_id = update.effective_chat.id

        await update.message.reply_text(f"🚀 Начинаю спам: {text} × {count}")

        for i in range(count):
            await context.bot.send_message(chat_id=chat_id, text=text)
            await asyncio.sleep(0.7)  # ⏱ задержка 0.7 сек для обхода ограничения

        await update.message.reply_text("✅ Спам завершён.")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("spam", spam_command))

    print("✅ Бот запущен")
    app.run_polling()
