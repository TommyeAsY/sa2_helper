from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from config.errors_logs import errors_logger


class RAGAgent:
    def __init__(self, model_id: str, prompt: str):
        self.model_id = model_id

        from rag.agent import knowledge

        self.agent = Agent(
            model=OpenRouter(id=model_id),
            description=prompt,
            knowledge=knowledge,
            search_knowledge=True,
            add_history_to_context=False,
            debug_mode=True,
            telemetry=False,
        )

    def switch_model(self, new_model_id: str):
        self.model_id = new_model_id
        self.agent.model = OpenRouter(id=new_model_id)

        if hasattr(self.agent, "_client"):
            self.agent._client = None

    async def answer(self, message: str) -> str:
        try:
            result = await self.agent.arun(message)
            return result.content or "I could not generate a response."
        except Exception as e:
            text = str(e)
            errors_logger.error(f"RAGAgent error: {text}", exc_info=True)

            if "temporarily rate-limited upstream" in text:
                return (
                    "⚠️ The selected model is temporarily rate‑limited by the provider.\n"
                    "Please try again later or switch to another model."
                )

            if "rate limit" in text.lower() or "too many requests" in text.lower():
                return "⚠️ You may have reached dev's daily rate limit."

            return "⚠️ An internal error occurred while generating the answer."
