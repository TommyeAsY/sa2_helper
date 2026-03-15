from discord.ext import commands

from config.messages_logs import messages_logger


def register_ping(bot):
    @bot.command(help="Test query")
    async def ping(ctx: commands.Context) -> None:
        """
        Responds with 'pong' when the user calls the !ping command.
        
        The command is meant to be restricted for the intentional servers, so
        it shall work only during tests.
        
        Args:
            ctx (commands.Context): The context of the command invocation,
            including message, author, and channel.
        
        Returns:
            None (NoneType): This function sends a test message to the channel
            and does not return a value.
        """
        reply = "pong"
        await ctx.send(reply)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
