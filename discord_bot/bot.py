import discord
from discord.ext import commands

import discord_bot.events.on_ready
from discord_bot.commands.hello import register_hello
from discord_bot.commands.models import register_model_commands
from discord_bot.commands.ping import register_ping
from discord_bot.events.on_command import register_command_handlers
from discord_bot.events.on_error import register_error_handlers
from discord_bot.events.on_guild import register_guild_handlers
from discord_bot.events.on_member import register_member_handlers
from discord_bot.events.on_message import register_on_message_handler
from discord_bot.permissions import register_permission_checks
from utils.help import CustomHelp


def create_bot():
    intents = discord.Intents.all()
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=CustomHelp()
    )

    discord_bot.events.on_ready.register_on_ready_handlers(bot)

    register_guild_handlers(bot)
    register_member_handlers(bot)
    register_command_handlers(bot)
    register_error_handlers(bot)

    register_permission_checks(bot)

    register_ping(bot)
    register_hello(bot)

    register_on_message_handler(bot)

    register_model_commands(bot)

    return bot
