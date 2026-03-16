import discord

from config.errors_logs import errors_logger
from config.messages_logs import messages_logger
from config.settings import settings
from discord_bot.events import on_ready


def register_on_message_handler(bot):
    @bot.event
    async def on_message(message: discord.Message) -> None:
        """
        Handles any of the input messages from users that's not a preset
        command that can be called with prefix.

        Currently warns user about not communicating in case of DM attempt.

        Main purpose of that is to allow the bot to send RAG-requests if the
        intentional conditions are meant.
        
        Also in case if the bot mentions itself, it ignores it.
    
        Args:
            message (discord.Message): input message from the user.
        
        Returns:
            None (NoneType): This function sends a message and does not return
            a value.
        """
        if message.author == bot.user:
            return

        if message.guild is None:
            messages_logger.info(f"[DM] {message.author}: {message.content}")
            reply = "I apologize, but I currently don't talk in DMs."
            await message.channel.send(reply)
            messages_logger.info(f"[DM][BOT]: {reply}")
            return

        guild_id = str(message.guild.id)
        channel_id = message.channel.id
        server_cfg = settings.servers.get(guild_id)

        messages_logger.info(
            f"[{message.guild}] #{message.channel} {message.author}: {message.content}"
        )

        if server_cfg is None:
            return

        if message.content.startswith("!"):
            command_name = message.content.split()[0].lstrip("!")
            if server_cfg["allowed_commands"] == "all" or command_name in server_cfg["allowed_commands"]:
                await bot.process_commands(message)
            return

        allowed_channels = server_cfg["allowed_channels"]
        if allowed_channels != "all" and channel_id not in allowed_channels:
            return

        if bot.user.mentioned_in(message):

            if not on_ready.bot_initialized:
                reply = "Knowledge base is not ready yet. Please try again in a moment."
            else:
                try:
                    reply = await on_ready.rag_agent.answer(message.content)
                except Exception as e:
                    errors_logger.error(
                        f"RAG error in guild {message.guild}: {e}",
                        exc_info=True
                    )
                    reply = "⚠️ An internal error occurred while generating the answer."

            await message.channel.send(reply)
            messages_logger.info(
                f"[{message.guild}] #{message.channel} [BOT]: {reply}"
            )
