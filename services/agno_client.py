from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from config.errors_logs import errors_logger


class AgnoClient:
    def __init__(self, model_id: str):
        self.model_id = model_id

    def create_agent(self, final_prompt: str) -> Agent:
        return Agent(
            model=OpenRouter(id=self.model_id),
            description=final_prompt,
            tools=[],
            knowledge=None,
            search_knowledge=False,
            debug_mode=True,
            telemetry=False,
        )

    def run_sync(self, final_prompt: str, message: str) -> str:
        try:
            agent = self.create_agent(final_prompt)
            result = agent.run(message)
            return result.content or "I could not generate a response."
        except Exception as e:
            errors_logger.error(f"AgnoClient sync error: {e}", exc_info=True)
            raise

    async def run_async(self, final_prompt: str, message: str) -> str:
        import asyncio
        loop = asyncio.get_event_loop()

        try:
            return await loop.run_in_executor(
                None,
                lambda: self.run_sync(final_prompt, message),
            )
        except Exception as e:
            errors_logger.error(f"AgnoClient async error: {e}", exc_info=True)
            raise
