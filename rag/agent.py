import os
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.knowledge import Knowledge

# ============================
# Configuration
# ============================

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
MIN_WORDS = 3

IGNORED_TEXTS = {
    "a message with attachments",
    "message with attachments",
    "image",
    "attachment",
    "attachments",
}

embedder = SentenceTransformerEmbedder(id="intfloat/e5-base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "knowledge_base", "vector_db")

vector_db = LanceDb(
    table_name="discord_messages",
    uri=DB_PATH,
    search_type=SearchType.vector,
    embedder=embedder,
)

knowledge = Knowledge(vector_db=vector_db)


def is_valid_text(text: str | None) -> bool:
    """
    Validate whether a text string is meaningful enough to be included in the knowledge base.

    Args:
        text (str | None): Raw text extracted from a Discord message or documentation file.

    Returns:
        bool: True if the text is meaningful and should be indexed, False otherwise.
    """
    if not text:
        return False

    t = text.strip().lower()
    if not t:
        return False
    if t in IGNORED_TEXTS:
        return False
    if len(t.split()) < MIN_WORDS:
        return False

    return True


def chunk_text(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if text.lower() in IGNORED_TEXTS:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()

        if chunk:
            lower = chunk.lower()
            if lower in IGNORED_TEXTS:
                start += size - overlap
                continue
            if len(chunk.split()) >= MIN_WORDS:
                chunks.append(chunk)

        start += size - overlap

    return chunks

