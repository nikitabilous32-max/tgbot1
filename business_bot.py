import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Подключение к базе
conn = sqlite3.connect("messages.db")
cursor = conn.cursor()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бизнес-бот. Используй /help.")


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "/deleted — показать последние удалённые сообщения\n"
        "/stats — статистика сообщений\n"
        "/help — помощь"
    )


@dp.message(Command("deleted"))
async def deleted_cmd(message: types.Message):
    cursor.execute("SELECT sender_id, text, date FROM messages ORDER BY rowid DESC LIMIT 10")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("Нет данных.")
        return

    text = "🗑 Последние сообщения:\n\n"
    for sender, msg, date in rows:
        text += f"👤 {sender}\n🕒 {date}\n💬 {msg}\n\n"

    await message.answer(text)


@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    cursor.execute("SELECT COUNT(*) FROM messages")
    total = cursor.fetchone()[0]

    await message.answer(f"📊 Всего сообщений в базе: {total}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
