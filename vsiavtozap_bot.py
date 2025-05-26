from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8080216198:AAEi07ywy8olOrbDdbxSwF-VOxQ4DCN1VCM"
MANAGER_CHAT_ID = -5576243097

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли мені дані про авто (Марка, модель, рік випуску, об'єм двигуна або фото VIN-коду).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text or "(немає тексту)"
    photo = update.message.photo

    await update.message.reply_text("✅ Запит прийнято. Менеджер відповість найближчим часом.")

    if photo:
        file_id = photo[-1].file_id
        await context.bot.send_photo(chat_id=5576243097, photo=file_id, caption=f"Запит від @{user.username or user.first_name} ({user.id})")
    else:
        await context.bot.send_message(chat_id=5576243097, text=f"Запит від @{user.username or user.first_name} ({user.id}):\n{text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    print("Бот запущено...")
    app.run_polling()
