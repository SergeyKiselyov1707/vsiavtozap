import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import aiosqlite
from datetime import datetime

TOKEN = "8080216198:AAEi07ywy8olOrbDdbxSwF-VOxQ4DCN1VCM"
MANAGER_CHAT_ID = -5576243097  # заміни на свій
ASK_CAR, ASK_PARTS = range(2)

# Включаємо логування
logging.basicConfig(level=logging.INFO)

# Створення таблиці SQLite
async def init_db():
    async with aiosqlite.connect("requests.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                car_info TEXT,
                parts_needed TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()

# Старт: запитуємо інфо про авто
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Надішліть, будь ласка, дані про авто (марка, модель, рік, об’єм або фото VIN-коду)."
    )
    return ASK_CAR

# Отримуємо дані про авто
async def receive_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['car_info'] = update.message.text or "(фото)"
    await update.message.reply_text("Які саме запчастини вас цікавлять?")
    return ASK_PARTS

# Отримуємо перелік запчастин і надсилаємо менеджеру
async def receive_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    car_info = context.user_data.get('car_info')
    parts = update.message.text

    # Збереження в БД
    async with aiosqlite.connect("requests.db") as db:
        await db.execute("""
            INSERT INTO requests (user_id, username, car_info, parts_needed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user.id,
            user.username,
            car_info,
            parts,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        await db.commit()

    # Надсилаємо менеджеру
    caption = (
        f"🔔 Новий запит від @{user.username or user.first_name} ({user.id}):\n\n"
        f"🚗 Авто: {car_info}\n"
        f"🧩 Запчастини: {parts}"
    )
    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=caption)

    # Кнопка для зв’язку з менеджером
    keyboard = [
        [InlineKeyboardButton("📞 Зв'язатися з менеджером", url="https://t.me/Vsiavtozap")]  # Замінити
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("✅ Запит прийнято! Менеджер скоро зв’яжеться з вами.", reply_markup=reply_markup)
    context.user_data.clear()
    return ConversationHandler.END

# Скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запит скасовано.")
    context.user_data.clear()
    return ConversationHandler.END

# Повторний обробник усіх текстів → автоматично як новий запит
async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ASK_CAR

# Основна функція запуску
async def main():
    await init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CAR: [MessageHandler(filters.TEXT | filters.PHOTO, receive_car)],
            ASK_PARTS: [MessageHandler(filters.TEXT, receive_parts)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_user=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    print("Бот запущено ✅")
    await app.run_polling()

# Запуск
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
