import os
import json
from tqdm import tqdm
import sqlite3
import discord

DATA_DIR = "rag/knowledge_base/data"
os.makedirs(DATA_DIR, exist_ok=True)


def get_db_path(guild_id: int) -> str:
    return f"{DATA_DIR}/guild_{guild_id}.sqlite"


def init_db(guild_id: int) -> None:
    """Create SQLite DB for a specific guild if it doesn't exist."""
    path = get_db_path(guild_id)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            message_id TEXT NOT NULL UNIQUE,
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


def save_message_to_db(message: discord.Message) -> None:
    """Save a single Discord message into SQLite."""
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
        str(message.id),
        str(message.author.id),
        message.author.name,
        message.content,
        json.dumps(attachments),
        f"https://discord.com/channels/{guild_id}/{message.channel.id}/{message.id}",
        message.created_at.isoformat()
    ))

    conn.commit()
    conn.close()


def get_last_message_id(guild_id, channel_id):
    db_path = get_db_path(guild_id)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_id FROM messages
        WHERE guild_id = ? AND channel_id = ?
        ORDER BY id DESC LIMIT 1
    """, (str(guild_id), str(channel_id)))

    row = cursor.fetchone()
    conn.close()

    return int(row[0]) if row else None


async def parse_guild(guild):
    """Parse all text channels of a guild and save messages to SQLite."""
    init_db(guild.id)
    count = 0

    for channel in tqdm(guild.text_channels, total=len(guild.text_channels)):
        try:
            last_id = get_last_message_id(guild.id, channel.id)

            if last_id:
                after = discord.Object(id=last_id)
                history = channel.history(limit=None, after=after)
            else:
                history = channel.history(limit=None)

            async for msg in history:
                save_message_to_db(msg)
                count += 1

        except Exception as e:
            print(f"[ERROR] Channel {channel.name}: {e}")

    return count



def load_messages_for_knowledge(guild_id: int) -> list:
    """Load messages from SQLite and convert them into Agno Documents."""
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


