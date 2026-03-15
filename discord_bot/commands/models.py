import discord
from discord.ext import commands

from config.messages_logs import messages_logger
from discord_bot.events import on_ready
from services.agno_client import AgnoClient


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

        embed = discord.Embed(
            title="Available models",
            color=discord.Color.purple()
        )

        for m in models:
            clean_id = m.model_id.replace(":free", "")
            embed.add_field(
                name=f"{m.index}. {m.name}",
                value=f"ID: `{clean_id}`\nContext: **{m.context_length}**",
                inline=False
            )

        await ctx.send(embed=embed)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: [EMBED] models list sent")

    @bot.command(name="switch", help=r"Switch model: !switch {index}")
    async def switch_cmd(ctx: commands.Context, index: int):
        if on_ready.model_registry.switch_model(index):
            current = on_ready.model_registry.get_current_model()
            if on_ready.rag_agent is not None:
                on_ready.rag_agent.model_id = current.model_id
                on_ready.rag_agent.client = AgnoClient(current.model_id)
    
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
