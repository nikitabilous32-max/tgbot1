import sqlite3
from pyrogram import Client
from pyrogram.types import Message

API_ID = 32816018
API_HASH = "73aa5abdd997d8dc991c261b010adfdf"

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH
)

# -----------------------------
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# -----------------------------
def init_db():
    conn = sqlite3.connect("messages.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            message_id INTEGER,
            text TEXT,
            date INTEGER,
            is_deleted INTEGER DEFAULT 0,
            is_edited INTEGER DEFAULT 0,
            media_type TEXT,
            file_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleted_unknown (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            reason TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()

# -----------------------------
# ЛОГИРОВАНИЕ НОВЫХ СООБЩЕНИЙ
# -----------------------------
@app.on_message()
def log_message(client: Client, message: Message):
    conn = sqlite3.connect("messages.db", check_same_thread=False)
    cursor = conn.cursor()

    text = message.text or ""
    media_type = None
    file_id = None

    # Фото
    if message.photo:
        media_type = "photo"
        file_id = message.photo.file_id

    # Видео
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id

    # Документы
    elif message.document:
        media_type = "document"
        file_id = message.document.file_id

    cursor.execute("""
        INSERT INTO messages (chat_id, user_id, message_id, text, date, media_type, file_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        message.chat.id,
        message.from_user.id if message.from_user else None,
        message.id,
        text,
        message.date,
        media_type,
        file_id
    ))

    conn.commit()
    conn.close()

    print(f"[NEW] chat={message.chat.id} msg={message.id} media={media_type} text={text}")


# -----------------------------
# ЛОГИРОВАНИЕ УДАЛЁННЫХ
# -----------------------------
@app.on_deleted_messages()
def log_deleted(client, messages):
    conn = sqlite3.connect("messages.db", check_same_thread=False)
    cursor = conn.cursor()

    for msg in messages:

        if msg is None:
            cursor.execute("INSERT INTO deleted_unknown (message_id, reason) VALUES (?, ?)", (None, "msg is None"))
            continue

        if msg.id is None:
            cursor.execute("INSERT INTO deleted_unknown (message_id, reason) VALUES (?, ?)", (None, "no message id"))
            continue

        message_id = msg.id

        if msg.chat is not None:
            chat_id = msg.chat.id
        else:
            cursor.execute("SELECT chat_id FROM messages WHERE message_id = ?", (message_id,))
            row = cursor.fetchone()

            if row:
                chat_id = row[0]
            else:
                cursor.execute("INSERT INTO deleted_unknown (message_id, reason) VALUES (?, ?)",
                               (message_id, "no chat and not found in DB"))
                continue

        cursor.execute("""
            UPDATE messages
            SET is_deleted = 1
            WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id))

        print(f"[DELETED] chat={chat_id} msg={message_id}")

    conn.commit()
    conn.close()


# -----------------------------
# ЛОГИРОВАНИЕ РЕДАКТИРОВАННЫХ
# -----------------------------
@app.on_edited_message()
def log_edited(client: Client, message: Message):
    conn = sqlite3.connect("messages.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages
        SET is_edited = 1, text = ?
        WHERE chat_id = ? AND message_id = ?
    """, (message.text or "", message.chat.id, message.id))

    conn.commit()
    conn.close()

    print(f"[EDITED] chat={message.chat.id} msg={message.id} text={message.text}")


print("Userbot started...")
app.run()
