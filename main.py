import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from cfg.errors_logs import errors_logger
from cfg.events_logs import events_logger
from cfg.messages_logs import messages_logger
from utils.help import CustomHelp
from utils.permissions import is_allowed
from rag.agent import ask_rag


intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=CustomHelp()
)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or sys.exit("Error: variable DISCORD_TOKEN is missing.")
# API_KEY = os.getenv("OPENAI_API_KEY") or sys.exit("Error: variable OPENAI_API_KEY is missing.")
# ID_MODEL = os.getenv("ID_MODEL") or sys.exit("Error: variable ID_MODEL is missing.")
# PROMPT = os.getenv("LLM_PROMPT") or sys.exit("Error: variable LLM_PROMPT is missing.")

events_logger = logging.getLogger("discord_bot.events")
messages_logger = logging.getLogger("discord_bot.messages")
errors_logger = logging.getLogger("discord_bot.errors")


@bot.event
async def on_ready() -> None:
    events_logger.info(
        f"Bot connected as {bot.user}, servers: {len(bot.guilds)}, latency: {bot.latency:.3f}s"
    )
    for guild in bot.guilds:
        channels_info = []
        for channel in guild.channels:
            perms = channel.permissions_for(guild.me)
            visibility = "VISIBLE" if perms.view_channel else "HIDDEN"
            channels_info.append(
                f"{channel.name} ({channel.type}) | send: {perms.send_messages}, read: {perms.read_messages}, visibility: {visibility}"
            )

        events_logger.info(
            f"Server: {guild.name} (id={guild.id}), channels:\n" + "\n".join(channels_info)
        )
        members_info = []
        for member in guild.members:
            roles = [role.name for role in member.roles if role.name != "@everyone"]
            owner = member == guild.owner
            admin = member.guild_permissions.administrator
            if admin:
                roles.append("ADMIN")
            if owner:
                roles.append("OWNER")
            info = f"{member} (id={member.id}) | nick: {member.display_name}, status: {member.status}, roles: {roles}"
            members_info.append(info)

        events_logger.info(f"Members in {guild.name}:\n" + "\n".join(members_info))

@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    events_logger.info(
        f"Joined new server: {guild.name} (id={guild.id}), members: {guild.member_count}"
    )
    channels_info = []
    for channel in guild.channels:
        perms = channel.permissions_for(guild.me)
        visibility = "VISIBLE" if perms.view_channel else "HIDDEN"
        channels_info.append(
            f"{channel.name} ({channel.type}) | send: {perms.send_messages}, read: {perms.read_messages}, visibility: {visibility}"
        )

    events_logger.info(
        f"Channels in {guild.name}:\n" + "\n".join(channels_info)
    )
    members_info = []
    for member in guild.members:
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        members_info.append(
            f"{member} (id={member.id}) | nick: {member.display_name}, status: {member.status}, roles: {roles}"
        )

    events_logger.info(f"Members in {guild.name}:\n" + "\n".join(members_info))


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    events_logger.info(f"Removed from server: {guild.name} (id={guild.id})")

@bot.event
async def on_member_join(member: discord.Member) -> None:
    events_logger.info(f"Member joined: {member} in server {member.guild.name} (id={member.guild.id})")

@bot.event
async def on_member_remove(member: discord.Member) -> None:
    events_logger.info(f"Member left: {member} from server {member.guild.name} (id={member.guild.id})")

@bot.event
async def on_command(ctx: commands.Context) -> None:
    events_logger.info(f"Command executed: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}")

# @bot.before_invoke     -----> None of these two work and I will maybe figure it out in the future. Or not.
# async def before_any_command(ctx):
#     await ctx.channel.trigger_typing()

# @bot.before_invoke
# async def before_any_command(ctx):
#     async with ctx.typing():
#         pass

@bot.before_invoke
async def check_allowed(ctx: commands.Context) -> None:
    """
    Checks if the input command allowed on the current server before execution.
    
    Args:
        ctx (commands.Context): The context of the command invocation, including message, author, and channel.
    
    Returns:
        None (NoneType): This function does not return a value.
    """
    if not is_allowed(ctx, ctx.command.name):
        raise commands.CheckFailure()

@bot.command(help="Test query")
async def ping(ctx: commands.Context) -> None:
    """
    Responds with 'pong' when the user calls the !ping command.
    The command is meant to be restricted for the intentional servers, so it shall work only during tests.
    
    Args:
        ctx (commands.Context): The context of the command invocation, including message, author, and channel.
    
    Returns:
        None (NoneType): This function sends a test message to the channel and does not return a value.
    """
    reply = "pong"
    await ctx.send(reply)
    messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")

@bot.command(help="Just a greeting")
async def hello(ctx: commands.Context) -> None:
    """
    Sends a friendly greeting when the user calls the !hello command.
    
    Args:
        ctx (commands.Context): The context of the command invocation, including message, author, and channel.
    
    Returns:
        None (NoneType): This function sends a greeting message to the channel and does not return a value.
    """
    reply = "Hello!"
    await ctx.send(reply)
    messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    Handles the exceptions from the users side.
    The responds with different amount of emojis are intentional.
    
    Args:
        ctx (commands.Context): The context of the command invocation, including message, author, and channel.
        error (commands.CommandError): The error raised during command execution.
    
    Returns:
        None (NoneType): This function sends a warning message when user misused the command and does not return a value.
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
        reply = "f⚠️ Error: {error}"
    await ctx.send(reply)
    messages_logger.info(f"[{ctx.guild}] #{ctx.channel} [BOT]: {reply}")

@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Handles any of the input messages from users that's not a preset command that can be called with prefix.
    Currently warns user about not communicating in case of DM attempt.
    Main purpose of that is to allow the bot to send RAG-requests if the intentional conditions are meant.
    Also in case if the bot mentions itself, it ignores it.

    Args:
        message (discord.Message): input message from the user.
    
    Returns:
        None (NoneType): This function sends a message and does not return a value.
    """
    if message.author == bot.user:
        return
    if message.guild is None:
        messages_logger.info(f"[DM] {message.author}: {message.content}")
        reply = "I apologize, but I currently don't talk in DMs."
        await message.channel.send(reply)
        messages_logger.info(f"[DM][BOT]: {reply}")
    else:
        messages_logger.info(f"[{message.guild}] #{message.channel} {message.author}: {message.content}")
    if bot.user.mentioned_in(message):
#        if message.guild and message.guild.id == 1449773237595537601:
#            rag_response = ask_rag(message.author, message, ID_MODEL, PROMPT)
#            rag_response = ask_rag(message.content, ID_MODEL, PROMPT)
#            await message.channel.send(rag_response)
#        else:
        reply = "👋 Why, hello there."
        await message.channel.send(reply)
        messages_logger.info(f"[{message.guild}] #{message.channel} [BOT]: {reply}")
    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    errors_logger.exception(f"Unhandled error in event {event}", exc_info=True)


bot.run(DISCORD_TOKEN)
