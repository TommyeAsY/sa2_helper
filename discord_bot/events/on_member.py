import discord

from config.events_logs import events_logger


def register_member_handlers(bot):
    @bot.event
    async def on_member_join(member: discord.Member) -> None:
        events_logger.info(
            f"Member joined: {member} in server {member.guild.name} (id={member.guild.id})"
        )

    @bot.event
    async def on_member_remove(member: discord.Member) -> None:
        events_logger.info(
            f"Member left: {member} from server {member.guild.name} (id={member.guild.id})"
        )
