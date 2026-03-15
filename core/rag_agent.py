from agno.knowledge.knowledge import Knowledge

from config.errors_logs import errors_logger
from rag.agent import build_context
from services.agno_client import AgnoClient


class RAGAgent:
    def __init__(self, model_id: str, prompt: str, knowledge: Knowledge | None):
        self.model_id = model_id
        self.prompt = prompt
        self.knowledge = knowledge
        self.client = AgnoClient(model_id)

    async def answer(self, message: str) -> str:
        if self.knowledge is None:
            return "Knowledge base is still loading. Please try again shortly."

        docs = self.knowledge.search(message)
        context = build_context(docs)

        final_prompt = (
            f"{self.prompt}\n\n"
            f"Relevant knowledge base documents (sorted by priority):\n"
            f"{context}\n\n"
            f"User question:\n{message}"
        )

        try:
            return await self.client.run_async(final_prompt, message)

        except Exception as e:
            text = str(e)
            errors_logger.error(f"RAGAgent error: {text}", exc_info=True)

            if "temporarily rate-limited upstream" in text:
                return (
                    "⚠️ The selected model is temporarily rate‑limited by the provider.\n"
                    "Please try again later or switch to another model."
                )

            if "rate limit" in text.lower() or "too many requests" in text.lower():
                return (
                    "⚠️ You may have reached dev's daily rate limit.\n"
                )

            return "⚠️ An internal error occurred while generating the answer."
