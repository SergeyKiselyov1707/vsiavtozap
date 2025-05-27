import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup
from db import init_db, save_request

TOKEN = "ВСТАВ_ТУТ_СВІЙ_ТОКЕН"
MANAGER_CHAT_ID = -5576243097  # Замінити на реальний chat_id супергрупи

ASK_AUTO = 1
ASK_PARTS = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Вкажіть дані про авто або фото VIN-коду:")
    return ASK_AUTO

async def ask_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['auto_info'] = update.message.text or "(немає тексту)"
    await update.message.reply_text("Які саме запчастини потрібні?")
    return ASK_PARTS

async def ask_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    parts = update.message.text
    auto_info = context.user_data.get('auto_info')

    caption = f"Запит від @{user.username or user.first_name} ({user.id}):\n\nАвто: {auto_info}\nЗапчастини: {parts}"
    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=caption)

    await save_request(user.id, user.username, auto_info, parts)

    contact_button = ReplyKeyboardMarkup([["Зв'язок з менеджером"]], resize_keyboard=True)
    await update.message.reply_text("✅ Ваш запит надіслано менеджеру.", reply_markup=contact_button)

    return ConversationHandler.END

async def contact_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Менеджер зв’яжеться з вами найближчим часом.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

async def main():
    await init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_AUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_auto)],
            ASK_PARTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_parts)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("Зв'язок з менеджером"), contact_manager))

    print("Бот запущено...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        if str(e).startswith('This event loop is already running'):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main())
        else:
            raise
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
