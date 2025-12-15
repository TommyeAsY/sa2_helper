import discord
from discord.ext import commands

from .permissions import config, is_allowed


class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
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

    async def send_command_help(self, command):
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
