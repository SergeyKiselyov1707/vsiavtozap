import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from db import init_db, save_request

TOKEN = "8080216198:AAEi07ywy8olOrbDdbxSwF-VOxQ4DCN1VCM"
MANAGER_CHAT_ID = 5576243097  # ваш ID чату
ASK_PARTS = 1

# Кнопка зв'язку з менеджером
def get_contact_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔧 Зв'язатися з менеджером", url="https://t.me/Vsiavtozap")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Надішли мені дані про авто (марка, модель, рік, об'єм або фото VIN-коду)."
    )
    return ASK_PARTS

async def ask_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text or ""
    photo = update.message.photo

    if photo:
        file_id = photo[-1].file_id
        context.user_data['auto_photo'] = file_id
        context.user_data['auto_text'] = None
    else:
        context.user_data['auto_text'] = text
        context.user_data['auto_photo'] = None

    await update.message.reply_text("Які саме запчастини вас цікавлять?")
    return ConversationHandler.END

async def handle_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    parts_text = update.message.text or "(немає тексту)"
    auto_text = context.user_data.get('auto_text')
    auto_photo = context.user_data.get('auto_photo')

    caption = f"Запит від @{user.username or user.first_name} ({user.id}):\n"
    if auto_text:
        caption += f"Інфо про авто:\n{auto_text}\n"
    if auto_photo:
        caption += "Фото VIN-коду додано.\n"
    caption += f"Запчастини:\n{parts_text}"

    # Надсилання менеджеру
    if auto_photo:
        await context.bot.send_photo(chat_id=MANAGER_CHAT_ID, photo=auto_photo, caption=caption)
    else:
        await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=caption)

    # Зберігаємо в базу
    await save_request(user.id, user.username, auto_text or "[Фото VIN]", parts_text)

    # Відповідь клієнту
    await update.message.reply_text(
        "✅ Ваш запит прийнято. Очікуйте відповідь від менеджера.",
        reply_markup=get_contact_keyboard()
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запит скасовано.")
    context.user_data.clear()
    return ConversationHandler.END

async def main():
    await init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PARTS: [MessageHandler(filters.TEXT | filters.PHOTO, ask_parts)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_parts))

    print("Бот запущено...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
