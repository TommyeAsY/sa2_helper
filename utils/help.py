import discord
from discord.ext import commands
from typing import Mapping, List, Optional

from .permissions import config, is_allowed


class CustomHelp(commands.HelpCommand):
    """
    A custom implementation of the HelpCommand class.

    This class overrides the default help command behavior to:
    - Display only the commands allowed for the current server.
    - Provide detailed help for a specific command if it is permitted.
    - Send responses as embeds for better readability.

    Attributes
    ----------
    context : commands.Context
        The context of the command invocation, automatically set by the bot.
    """

    async def send_bot_help(
        self,
        mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ) -> None:
        """
        Build and send an embed listing all available commands for the current server.

        Args:
            mapping (Mapping[Optional[commands.Cog], List[commands.Command]]): 
                A dictionary where the key is a cog (or None) and the value is a list of commands.

        Returns:
            None (NoneType): Sends an embed message to the channel, does not return a value.
        """
        ctx = self.context
        guild_id = str(ctx.guild.id)
        allowed = config.get(guild_id, {}).get("allowed_commands", [])

        embed = discord.Embed(
            title="Currently available commands",
            color=discord.Color.dark_purple()
        )
        for cog, commands_list in mapping.items():
            filtered = [cmd for cmd in commands_list if cmd.name in allowed]
            if filtered:
                embed.add_field(
                    name=cog.qualified_name if cog else "No category",
                    value=", ".join([cmd.name for cmd in filtered]),
                    inline=False
                )
        await ctx.send(embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        """
        Build and send an embed with information about a specific command.

        Args:
            command (commands.Command): The command for which help should be displayed.

        Returns:
            None (NoneType): Sends an embed or an error message to the channel, does not return a value.
        """
        ctx = self.context
        if is_allowed(ctx, command.name):
            embed = discord.Embed(
                title=f"!{command.name}",
                description=command.help or "No description",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(":x: :x: :x: I didn't recognize your command. Try again or use !help")
