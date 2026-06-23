import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

BOT_TOKEN = "8730289859:AAExSPtszO3fBfhMfUbInB-ISf45UlG-J6Q"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# -----------------------------
# ФУНКЦИЯ ДЛЯ ЗАПРОСОВ К БАЗЕ
# -----------------------------
def db_query(query, params=()):
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# -----------------------------
# /start — главное меню
# -----------------------------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = InlineKeyboardBuilder()

    kb.button(text="📂 Выбрать чат", callback_data="select_chat")
    kb.button(text="🔍 Поиск", callback_data="search_menu")

    await message.answer(
        "👋 Бизнес‑бот запущен.\nВыбери действие:",
        reply_markup=kb.as_markup()
    )


# -----------------------------
# МЕНЮ ВЫБОРА ЧАТА
# -----------------------------
@dp.callback_query(lambda c: c.data == "select_chat")
async def select_chat_menu(callback: types.CallbackQuery):
    chats = db_query("SELECT DISTINCT chat_id FROM messages ORDER BY chat_id")

    if not chats:
        return await callback.message.edit_text("❌ В базе нет чатов")

    kb = InlineKeyboardBuilder()

    for (chat_id,) in chats:
        kb.button(text=f"Чат {chat_id}", callback_data=f"chat_{chat_id}")

    kb.adjust(1)

    await callback.message.edit_text(
        "📂 Выбери чат:",
        reply_markup=kb.as_markup()
    )


# -----------------------------
# МЕНЮ ДЕЙСТВИЙ ДЛЯ КОНКРЕТНОГО ЧАТА
# -----------------------------
@dp.callback_query(lambda c: c.data.startswith("chat_"))
async def chat_actions(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[1])

    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Удалённые", callback_data=f"deleted_{chat_id}")
    kb.button(text="✏️ Редактированные", callback_data=f"edited_{chat_id}")
    kb.button(text="🔍 Поиск в чате", callback_data=f"searchchat_{chat_id}")
    kb.button(text="⬅️ Назад", callback_data="select_chat")

    kb.adjust(1)

    await callback.message.edit_text(
        f"📌 Чат {chat_id}\nВыбери действие:",
        reply_markup=kb.as_markup()
    )


# -----------------------------
# ПОКАЗАТЬ УДАЛЁННЫЕ СООБЩЕНИЯ
# -----------------------------
@dp.callback_query(lambda c: c.data.startswith("deleted_"))
async def show_deleted(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[1])

    rows = db_query("""
        SELECT user_id, message_id, text, date
        FROM messages
        WHERE chat_id = ? AND is_deleted = 1
        ORDER BY date DESC
        LIMIT 30
    """, (chat_id,))

    if not rows:
        return await callback.message.edit_text("❌ Нет удалённых сообщений")

    text = f"🗑 Удалённые сообщения в чате {chat_id}:\n\n"

    for user_id, msg_id, msg_text, date in rows:
        text += (
            f"👤 {user_id}\n"
            f"💬 {msg_text}\n"
            f"🕒 {date}\n"
            f"🆔 msg_id: {msg_id}\n\n"
        )

    await callback.message.edit_text(text)


# -----------------------------
# ПОКАЗАТЬ РЕДАКТИРОВАННЫЕ
# -----------------------------
@dp.callback_query(lambda c: c.data.startswith("edited_"))
async def show_edited(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[1])

    rows = db_query("""
        SELECT user_id, message_id, text, date
        FROM messages
        WHERE chat_id = ? AND is_edited = 1
        ORDER BY date DESC
        LIMIT 30
    """, (chat_id,))

    if not rows:
        return await callback.message.edit_text("❌ Нет редактированных сообщений")

    text = f"✏️ Редактированные сообщения в чате {chat_id}:\n\n"

    for user_id, msg_id, msg_text, date in rows:
        text += (
            f"👤 {user_id}\n"
            f"💬 {msg_text}\n"
            f"🕒 {date}\n"
            f"🆔 msg_id: {msg_id}\n\n"
        )

    await callback.message.edit_text(text)


# -----------------------------
# ПОИСК В КОНКРЕТНОМ ЧАТЕ
# -----------------------------
@dp.callback_query(lambda c: c.data.startswith("searchchat_"))
async def search_in_chat(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[1])

    await callback.message.edit_text(
        f"🔍 Введи текст для поиска в чате {chat_id}"
    )

    @dp.message()
    async def search_handler(message: types.Message):
        query = f"%{message.text}%"

        rows = db_query("""
            SELECT user_id, message_id, text, date
            FROM messages
            WHERE chat_id = ? AND text LIKE ?
            ORDER BY date DESC
            LIMIT 30
        """, (chat_id, query))

        if not rows:
            return await message.answer("❌ Ничего не найдено")

        text = f"🔍 Результаты поиска в чате {chat_id}:\n\n"

        for user_id, msg_id, msg_text, date in rows:
            text += (
                f"👤 {user_id}\n"
                f"💬 {msg_text}\n"
                f"🕒 {date}\n"
                f"🆔 msg_id: {msg_id}\n\n"
            )

        await message.answer(text)


# -----------------------------
# ЗАПУСК
# -----------------------------
async def main():
    print("Business bot started")
    await dp.start_polling(bot)

asyncio.run(main())
