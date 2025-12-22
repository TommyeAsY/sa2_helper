import os
import asyncio
from typing import List, Optional

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from rag.tools import get_sa2_categories, get_sa2_leaderboard
from .parsing_knowledge import load_messages_for_knowledge


# ============================
# Constants and configuration
# ============================

MIN_TEXT_LENGTH = 20

IGNORED_TEXTS = {
    "a message with attachments",
    "message with attachments",
    "image",
    "attachment",
    "attachments",
}

embedder = SentenceTransformerEmbedder(id="all-MiniLM-L6-v2")

vector_db = LanceDb(
    table_name="discord_messages",
    uri="rag/knowledge_base/vector_db",
    search_type=SearchType.vector,
    embedder=embedder
)


# ============================
# Utility functions
# ============================

def is_valid_text(text: Optional[str]) -> bool:
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
    if len(t) < MIN_TEXT_LENGTH:
        return False

    if t in IGNORED_TEXTS:
        return False

    return True


def build_context(docs: List) -> str:
    """
    Build a combined textual context from a list of Document objects.

    Args:
        docs (List[Document]): Documents returned by the vector search.

    Returns:
        str: A concatenated string of document contents sorted by priority.
    """
    valid_docs = [d for d in docs if is_valid_text(d.content)]

    sorted_docs = sorted(
        valid_docs,
        key=lambda d: 0 if d.meta_data.get("priority") == "high" else 1
    )

    return "\n\n".join(d.content for d in sorted_docs)


# ============================
# Knowledge loading
# ============================

async def load_full_knowledge(guild_ids: List[int]) -> Knowledge:
    """
    Load all knowledge sources into the vector database:
    - Parsed Discord messages
    - Internal documentation files

    Args:
        guild_ids (List[int]): List of Discord guild IDs to load messages from.

    Returns:
        Knowledge: A fully populated Knowledge object ready for RAG queries.
    """
    kb = Knowledge(vector_db=vector_db)

    # Load Discord messages
    for gid in guild_ids:
        for doc in load_messages_for_knowledge(gid):
            text = (doc["text"] or "").strip()
            if not is_valid_text(text):
                continue

            await kb.add_content_async(
                text_content=text,
                metadata={**doc["metadata"], "priority": "low"},
                skip_if_exists=True
            )
            await asyncio.sleep(0.01)

    # Load internal documentation
    extra_dir = "rag/knowledge_base/extra_sources"
    if os.path.isdir(extra_dir):
        for filename in os.listdir(extra_dir):
            path = os.path.join(extra_dir, filename)
            if not os.path.isfile(path):
                continue

            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if not is_valid_text(text):
                continue

            await kb.add_content_async(
                text_content=text,
                metadata={"source": filename, "priority": "high"},
                skip_if_exists=True
            )

    return kb


# ============================
# Manual RAG query
# ============================

async def ask_rag_async(message: str, model: str, prompt: str, kb: Knowledge) -> str:
    """
    Asynchronously execute a RAG query using a thread executor.

    Args:
        message (str): User query.
        model (str): Model ID for OpenRouter.
        prompt (str): System prompt.
        kb (Knowledge): Knowledge base instance.

    Returns:
        str: Model-generated answer.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: ask_rag(message, model, prompt, kb)
    )


def ask_rag(message: str, model: str, prompt: str, kb: Knowledge) -> str:
    """
    Perform a manual RAG (Retrieval-Augmented Generation) query:
    - Search the knowledge base
    - Filter and prioritize documents
    - Build a contextual prompt
    - Run the model without tool usage

    Args:
        message (str): User query.
        model (str): Model ID for OpenRouter.
        prompt (str): System prompt.
        kb (Knowledge): Knowledge base instance.

    Returns:
        str: Final model response or fallback message.
    """
    docs = kb.search(message)
    context = build_context(docs)

    final_prompt = (
        f"{prompt}\n\n"
        f"Relevant knowledge base documents (sorted by priority):\n"
### BEGIN KNOWLEDGE CONTEXT ###
        f"{context}\n\n"
### END KNOWLEDGE CONTEXT ###
        f"User question:\n{message}"
    )

    agent = Agent(
        model=OpenRouter(id=model),
        description=final_prompt,
        tools=[],                 # Tools disabled
        knowledge=None,           # Disable built-in RAG
        search_knowledge=False,   # Disable built-in search
        debug_mode=True,
        telemetry=False
    )

    result = agent.run(message)
    return result.content or "I could not generate a response."
