import asyncio

from config.events_logs import events_logger
from config.settings import settings
from core.document_index import KnowledgeIndex
from core.parsers.discord_parser import DiscordGuildParser
from core.rag_agent import RAGAgent
from services.model_registry import ModelRegistry


model_registry = ModelRegistry()
knowledge_index = None
rag_agent = None
bot_initialized = False


def register_on_ready_handlers(bot):
    @bot.event
    async def on_ready() -> None:
        global rag_agent, knowledge_index, bot_initialized

        events_logger.info(
            f"Bot connected as {bot.user}, servers: {len(bot.guilds)}, latency: {bot.latency:.3f}s"
        )
        print("\n=== Initializing bot ===")
        print("Loading model list...")
        model_registry.fetch_models()

        current_model = model_registry.get_current_model()
        rag_agent = RAGAgent(
            model_id=current_model.model_id,
            prompt=settings.prompt,
            knowledge=None
        )
        print(f"RAG agent created with model: {current_model.name}")

        real_guild_ids = {guild.id for guild in bot.guilds}
        allowed_guilds = settings.allowed_guilds
        active_guilds = real_guild_ids & allowed_guilds

        knowledge_index = KnowledgeIndex(active_guilds)

        asyncio.create_task(initialize_rag(bot, active_guilds))

        print("Bot is ready. Background initialization started.\n")


async def initialize_rag(bot, active_guilds):
    global rag_agent, bot_initialized

    print("\n=== Background RAG initialization ===")

    for guild in bot.guilds:
        if guild.id in active_guilds:
            print(f"Parsing server: {guild.name}")
            parser = DiscordGuildParser(guild.id)
            count = await parser.parse(guild)
            print(f"Saved {count} messages")

    print("Loading knowledge index...")
    await knowledge_index.load()

    rag_agent.knowledge = knowledge_index.index

    bot_initialized = True
    print("\n=== Initialization complete! RAG is fully ready. ===\n")


def register_on_guild_join_handler(bot):
    @bot.event
    async def on_guild_join(guild):
        guild_id = str(guild.id)

        if guild_id not in settings.servers:
            events_logger.warning(
                f"Bot was invited to unauthorized server: {guild.name} ({guild.id}). Leaving..."
            )
            print(f"[WARNING] Leaving unauthorized server: {guild.name} ({guild.id})")

            await guild.leave()

            events_logger.info(
                f"Bot has left unauthorized server: {guild.name} ({guild.id})"
            )
            print(f"[WARNING] Left server: {guild.name} ({guild.id})")
        else:
            events_logger.info(
                f"Bot joined authorized server: {guild.name} ({guild.id})"
            )
            print(f"[INFO] Joined authorized server: {guild.name} ({guild.id})")
