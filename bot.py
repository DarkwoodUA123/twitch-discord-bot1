from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

BOT_TOKEN = "6125133441:AAH1DmGzp-MyNUlR2S_48ce4jveDFCC6mqc"
OWNER_ID = 948828396  # Твой ID

async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Ты не владелец бота.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❗ Использование:\n/spam <текст> <кол-во>")
        return

    text = " ".join(context.args[:-1])
    try:
        count = int(context.args[-1])
    except ValueError:
        await update.message.reply_text("❗ Кол-во должно быть числом.")
        return

    if count > 50:
        count = 50
        await update.message.reply_text("⚠️ Ограничено до 50 сообщений.")

    for i in range(count):
        try:
            await update.message.reply_text(text)
            await asyncio.sleep(0.07)
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
            break

    await update.message.reply_text(f"✅ Отправлено {count} сообщений.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler(["spam"], spam_command))

print("✅ Бот запущен")
app.run_polling()
