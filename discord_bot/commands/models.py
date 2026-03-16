import discord
from discord.ext import commands

from config.messages_logs import messages_logger
from discord_bot.events import on_ready


def register_model_commands(bot):

    @bot.command(name="model", help="Show current model")
    async def model_cmd(ctx: commands.Context):
        m = on_ready.model_registry.get_current_model()
        if not m:
            reply = "The model isn't loaded."
            await ctx.send(reply)
            messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
            return

        clean_id = m.model_id.replace(":free", "")
        reply = (
            f"**Current model:**\n"
            f"Name: {m.name}\n"
            f"ID: `{clean_id}`\n"
            f"Context length: {m.context_length}"
        )
        await ctx.send(reply)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")

    @bot.command(name="models", help="Show available models")
    async def models_cmd(ctx: commands.Context):
        models = on_ready.model_registry.get_models()
        if not models:
            reply = "Models aren't loaded."
            await ctx.send(reply)
            messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
            return

        lines = []
        for m in models:
            clean_id = m.model_id.replace(":free", "")
            line = f"{m.index}. {m.name} — `{clean_id}` (context: {m.context_length})"
            lines.append(line)

        header = "**Available models:**\n"
        current_chunk = header
        chunks = []

        for line in lines:
            if len(current_chunk) + len(line) + 1 > 1900:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk)

        for chunk in chunks:
            await ctx.send(chunk)

        messages_logger.info(
            f"[{ctx.guild}] #{ctx.channel} [BOT]: models list sent in {len(chunks)} chunk(s)"
        )

    @bot.command(name="switch", help=r"Switch model: !switch {index}")
    async def switch_cmd(ctx: commands.Context, index: int):
        if on_ready.model_registry.switch_model(index):
            current = on_ready.model_registry.get_current_model()
            if on_ready.rag_agent is not None:
                on_ready.rag_agent.switch_model(current.model_id)

            clean_id = current.model_id.replace(":free", "")
            reply = (
                f"Model switched to **{current.name}**\n"
                f"ID: `{clean_id}`\n"
                f"Context: **{current.context_length}**"
            )
            await ctx.send(reply)
            messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
        else:
            reply = "Model's index is invalid."
            await ctx.send(reply)
            messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")

    @bot.command(name="refresh_models", help="Refresh available models.")
    async def refresh_cmd(ctx: commands.Context):
        on_ready.model_registry.fetch_models()
        reply = "Model's list has been updated."
        await ctx.send(reply)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
