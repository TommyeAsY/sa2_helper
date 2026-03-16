import os
from agno.knowledge.knowledge import Knowledge

from rag.agent import (
    chunk_text,
    is_valid_text,
    knowledge as global_knowledge,
)
from rag.parsing_knowledge import load_messages_for_knowledge


EXTRA_SOURCES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "rag",
    "knowledge_base",
    "extra_sources",
)


class KnowledgeIndex:
    def __init__(self, guild_ids: list[int]):
        self.guild_ids = guild_ids
        self.index: Knowledge | None = None

    async def load(self):
        print("START LOADING")

        kb = global_knowledge

        # ============================
        # 1. Discord-based database (priority)
        # ============================
        for guild_id in self.guild_ids:
            docs = load_messages_for_knowledge(guild_id)

            for doc in docs:
                raw_text = (doc["text"] or "").strip()
                if not raw_text:
                    continue

                chunks = chunk_text(raw_text)

                for chunk in chunks:
                    if not is_valid_text(chunk):
                        continue

                    meta = {
                        "author": str(doc["metadata"]["author"]),
                        "url": str(doc["metadata"]["url"]),
                        "timestamp": str(doc["metadata"]["timestamp"]),
                        "guild_id": int(doc["metadata"]["guild_id"]),
                        "source": "discord",
                    }

                    await kb.add_content_async(
                        text_content=chunk,
                        metadata=meta,
                        skip_if_exists=True,
                    )

        # ============================
        # 2. Extra sources (inner documentation)
        # ============================
        if os.path.exists(EXTRA_SOURCES_DIR):
            for filename in os.listdir(EXTRA_SOURCES_DIR):
                path = os.path.join(EXTRA_SOURCES_DIR, filename)
                if not os.path.isfile(path):
                    continue

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                except Exception as e:
                    print(f"Failed to read extra source {filename}: {e}")
                    continue

                if not text:
                    continue

                chunks = chunk_text(text)

                for chunk in chunks:
                    if not is_valid_text(chunk):
                        continue

                    meta = {
                        "source": "extra",
                        "filename": filename,
                    }

                    await kb.add_content_async(
                        text_content=chunk,
                        metadata=meta,
                        skip_if_exists=True,
                    )

        self.index = kb

        print("FINISHED LOADING")
