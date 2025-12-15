from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.calculator import CalculatorTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.website import WebsiteTools
from agno.tools.youtube import YouTubeTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.api import CustomApiTools


def ask_rag(message: str, model: str, prompt: str) -> str:
    """
    Get a RAG response by mentioning.

    Args:
        message (str): user's text message.
        model (str): the model for the RAG-query.
        prompt (str): the internal prompt.

    Returns:
        str: the response from LLM.
    """
    agent = Agent(
        model=OpenRouter(id=model),
        description=prompt,
        tools=[
            CalculatorTools(),
            WikipediaTools(all=True),
            WebsiteTools(),
            YouTubeTools(all=True),
            DuckDuckGoTools(all=True),
            Newspaper4kTools(),
            CustomApiTools(all=True)
        ],
        debug_mode=True)

    return agent.run(message).content