import os 
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.help import CustomHelp
from utils.permissions import is_allowed


intents = discord.Intents.default()
intents.message_content = True

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


# @bot.before_invoke
# async def before_any_command(ctx):
#     await ctx.channel.trigger_typing()

@bot.before_invoke
async def before_any_command(ctx):
    async with ctx.typing():
        pass

@bot.before_invoke
async def check_allowed(ctx):
    if not is_allowed(ctx, ctx.command.name):
        raise commands.CheckFailure()

@bot.command(help="Test query")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(help="Just a greeting")
async def hello(ctx):
    await ctx.send("Hello!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(":x: I didn't recognize your. Try again or use !help")

    elif isinstance(error, commands.CheckFailure):
        await ctx.send(":x: :x: I didn't recognize your. Try again or use !help")

    else:
        await ctx.send(f"⚠️ Error: {error}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        if message.guild is None:
            await message.channel.send("I apologize, but I currently don't talk in DMs.")
#       elif message.guild and message.guild.id == 1449773237595537601:
#           rag_response = ask_rag(message.author, message, ID_MODEL, PROMPT)
#           rag_response = ask_rag(message.content, ID_MODEL, PROMPT)
#           await message.channel.send(rag_response)
        else:
            await message.channel.send("👋 Why, hello there.")

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)

