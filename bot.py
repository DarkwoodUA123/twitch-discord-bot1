from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Использование: /spam <сообщение> <кол-во>")
            return

        text = args[0]
        count = int(args[1])

        for _ in range(count):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
