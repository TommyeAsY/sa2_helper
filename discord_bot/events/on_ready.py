import asyncio

from config.events_logs import events_logger
from config.settings import settings
from core.document_index import KnowledgeIndex
from core.parsers.discord_parser import DiscordGuildParser
from core.rag_agent import RAGAgent
from services.model_registry import ModelRegistry


model_registry = ModelRegistry()
knowledge_index: KnowledgeIndex | None = None
rag_agent: RAGAgent | None = None
bot_initialized: bool = False
init_started: bool = False


def register_on_ready_handlers(bot):
    @bot.event
    async def on_ready() -> None:
        global knowledge_index, init_started

        events_logger.info(
            f"Bot connected as {bot.user}, servers: {len(bot.guilds)}, latency: {bot.latency:.3f}s"
        )

        if init_started:
            print("Bot reconnected, initialization already in progress or done.")
            return

        print("\n=== Bot connected. Starting background init ===")

        real_guild_ids = {guild.id for guild in bot.guilds}
        allowed_guilds = settings.allowed_guilds
        active_guilds = real_guild_ids & allowed_guilds

        knowledge_index = KnowledgeIndex(list(active_guilds))

        init_started = True
        asyncio.create_task(initialize_rag(bot, active_guilds))


async def initialize_rag(bot, active_guilds):
    global rag_agent, bot_initialized, knowledge_index

    try:
        print("\n=== Background RAG initialization ===")

        model_registry.fetch_models()
        current_model = model_registry.get_current_model()

        for guild in bot.guilds:
            if guild.id in active_guilds:
                print(f"Parsing server: {guild.name}")
                parser = DiscordGuildParser(guild.id)
                count = await parser.parse(guild)
                print(f"Saved {count} messages")

        print("Loading knowledge index...")
        await knowledge_index.load()

        rag_agent = RAGAgent(
            model_id=current_model.model_id,
            prompt=settings.prompt,
        )

        bot_initialized = True
        print("\n=== Initialization complete! RAG is fully ready. ===\n")

    except Exception as e:
        print("INIT ERROR:", e)
