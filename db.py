import aiosqlite

DB_NAME = "requests.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            auto_info TEXT,
            parts TEXT
        )""")
        await db.commit()

async def save_request(user_id, username, auto_info, parts):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO requests (user_id, username, auto_info, parts) VALUES (?, ?, ?, ?)",
                         (user_id, username, auto_info, parts))
        await db.commit()
