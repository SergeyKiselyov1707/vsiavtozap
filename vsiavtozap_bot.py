from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8080216198:AAEi07ywy8olOrbDdbxSwF-VOxQ4DCN1VCM"
MANAGER_CHAT_ID = -5576243097

ASK_PARTS = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Надішли мені дані про авто (Марка, модель, рік випуску, об'єм двигуна або фото VIN-коду)."
    )
    return ASK_PARTS

async def ask_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text or ""
    photo = update.message.photo

    # Зберігаємо дані авто у контексті користувача
    if photo:
        file_id = photo[-1].file_id
        context.user_data['auto_photo_id'] = file_id
        context.user_data['auto_text'] = None
    else:
        context.user_data['auto_text'] = text
        context.user_data['auto_photo_id'] = None

    # Питаємо, які запчастини потрібні
    await update.message.reply_text("Які саме запчастини вас цікавлять? Напишіть, будь ласка.")

    return ConversationHandler.END

async def handle_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    parts_text = update.message.text or "(немає тексту)"

    # Формуємо повідомлення для менеджера
    auto_text = context.user_data.get('auto_text')
    auto_photo_id = context.user_data.get('auto_photo_id')

    caption = f"Запит від @{user.username or user.first_name} ({user.id}):\n"
    if auto_text:
        caption += f"Інформація про авто:\n{auto_text}\n"
    if auto_photo_id:
        caption += "Фото VIN-коду надано.\n"
    caption += f"Потрібні запчастини:\n{parts_text}"

    # Відправляємо менеджеру
    if auto_photo_id:
        await context.bot.send_photo(chat_id=MANAGER_CHAT_ID, photo=auto_photo_id, caption=caption)
    else:
        await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=caption)

    # Відповідаємо користувачу
    await update.message.reply_text("✅ Ваш запит надіслано менеджеру. Очікуйте відповідь.")

    # Очищаємо дані користувача
    context.user_data.clear()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано. Якщо потрібно почати заново, надішліть /start.")
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == "__main__":
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PARTS: [MessageHandler(filters.TEXT | filters.PHOTO, ask_parts)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
        per_user=True,
    )

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_parts))  # Для обробки повідомлення із запчастинами

    print("Бот запущено...")
    app.run_polling()
