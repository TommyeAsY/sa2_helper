from discord.ext import commands

from config.errors_logs import errors_logger
from config.events_logs import events_logger
from config.messages_logs import messages_logger


def register_command_handlers(bot):
    @bot.event
    async def on_command(ctx: commands.Context) -> None:
        events_logger.info(
            f"Command executed: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}"
        )

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """
        Handles the exceptions from the users side.
        
        The responds with different amount of emojis are intentional.
        
        Args:
            ctx (commands.Context): The context of the command invocation,
            including message, author, and channel.
            error (commands.CommandError): The error raised during command
            execution.
        
        Returns:
            None (NoneType): This function sends a warning message when user
            misused the command and does not return a value.
        """
        errors_logger.error(
            f"Error in command {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}: {error}",
            exc_info=True
        )

        if isinstance(error, commands.CommandNotFound):
            reply = ":x: I didn't recognize your. Try again or use !help"
        elif isinstance(error, commands.CheckFailure):
            reply = ":x: :x: I didn't recognize your. Try again or use !help"
        else:
            reply = f"⚠️ Error: {error}"
        await ctx.send(reply)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
