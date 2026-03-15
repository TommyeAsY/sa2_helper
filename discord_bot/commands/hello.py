from discord.ext import commands

from config.messages_logs import messages_logger


def register_hello(bot):
    @bot.command(help="Just a greeting")
    async def hello(ctx: commands.Context) -> None:
        """
        Sends a friendly greeting when the user calls the !hello command.
        
        Args:
            ctx (commands.Context): The context of the command invocation,
            including message, author, and channel.
        
        Returns:
            None (NoneType): This function sends a greeting message to the
            channel and does not return a value.
        """
        reply = "Hello!"
        await ctx.send(reply)
        messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")
