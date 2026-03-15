from discord.ext import commands

from config.errors_logs import errors_logger
from utils.permissions import is_allowed


def register_permission_checks(bot):
    @bot.before_invoke
    async def check_allowed(ctx: commands.Context) -> None:
        """
        Checks if the input command allowed on the current server before execution.
        
        Args:
            ctx (commands.Context): The context of the command invocation, including
            message, author, and channel.
        
        Returns:
            None (NoneType): This function does not return a value.
        """
        if not is_allowed(ctx, ctx.command.name):
            errors_logger.warning(
                f"Permission denied for command {ctx.command} by {ctx.author} "
                f"in {ctx.guild}/{ctx.channel}"
            )
            raise commands.CheckFailure()
