import json
import os
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor

import discord


DATA_DIR = "rag/knowledge_base/data"
os.makedirs(DATA_DIR, exist_ok=True)

executor = ThreadPoolExecutor(max_workers=1)


def get_db_path(guild_id: int) -> str:
    return f"{DATA_DIR}/guild_{guild_id}.sqlite"


# -----------------------------
# DB INITIALIZATION
# -----------------------------

def init_db_sync(guild_id: int) -> None:
    path = get_db_path(guild_id)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            message_id INTEGER NOT NULL UNIQUE,
            author_id TEXT NOT NULL,
            author_name TEXT NOT NULL,
            content TEXT,
            attachments TEXT,
            message_url TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()


async def init_db(guild_id: int):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, init_db_sync, guild_id)


# -----------------------------
# SAVE MESSAGE
# -----------------------------

def save_message_sync(message: discord.Message):
    guild_id = message.guild.id
    db_path = get_db_path(guild_id)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    attachments = [att.url for att in message.attachments]

    cursor.execute("""
        INSERT OR IGNORE INTO messages (
            guild_id, channel_id, message_id, author_id, author_name,
            content, attachments, message_url, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(guild_id),
        str(message.channel.id),
        message.id,
        str(message.author.id),
        message.author.name,
        message.content,
        json.dumps(attachments),
        f"https://discord.com/channels/{guild_id}/{message.channel.id}/{message.id}",
        message.created_at.isoformat()
    ))

    conn.commit()
    conn.close()


async def save_message_to_db(message: discord.Message):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_message_sync, message)


# -----------------------------
# LAST MESSAGE ID
# -----------------------------

async def get_last_message_id(guild_id, channel_id):
    def _get_last():
        db_path = get_db_path(guild_id)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT message_id FROM messages
            WHERE guild_id = ? AND channel_id = ?
            ORDER BY message_id DESC LIMIT 1
        """, (str(guild_id), str(channel_id)))

        row = cursor.fetchone()
        conn.close()

        return int(row[0]) if row else None

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _get_last)


# -----------------------------
# ASYNC PROGRESS BAR
# -----------------------------

async def async_progress(iterable, desc=""):
    total = len(iterable)
    for i, item in enumerate(iterable, start=1):
        print(f"\r{desc}: {i}/{total}", end="")
        yield item
    print()


# -----------------------------
# PARSE GUILD (REVERSE HISTORY)
# -----------------------------

async def parse_guild(guild):
    await init_db(guild.id)
    count = 0

    async for channel in async_progress(guild.text_channels, desc=f"Parsing {guild.name}"):
        try:
            last_id = await get_last_message_id(guild.id, channel.id)

            if last_id is None:
                history = channel.history(limit=None, oldest_first=True)
                async for msg in history:
                    await save_message_to_db(msg)
                    count += 1
                continue

            before = None
            stop = False

            while not stop:
                batch_empty = True

                history = channel.history(
                    limit=100,
                    before=before,
                    oldest_first=False
                )

                async for msg in history:
                    batch_empty = False

                    if msg.id <= last_id:
                        stop = True
                        break

                    await save_message_to_db(msg)
                    count += 1

                    before = discord.Object(id=msg.id)

                if batch_empty:
                    break

        except Exception as e:
            print(f"[ERROR] Channel {channel.name}: {e}")

        await asyncio.sleep(0.1)

    return count


# -----------------------------
# LOAD MESSAGES FOR KNOWLEDGE
# -----------------------------

def load_messages_for_knowledge(guild_id: int) -> list:
    db_path = get_db_path(guild_id)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT author_name, content, message_url, timestamp FROM messages")
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for author, text, url, ts in rows:
        if not text:
            continue

        docs.append({
            "text": text,
            "metadata": {
                "author": author,
                "url": url,
                "timestamp": ts,
                "guild_id": guild_id
            }
        })

    return docs
