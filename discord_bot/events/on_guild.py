import discord

from config.events_logs import events_logger


def register_guild_handlers(bot):
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
                f"{channel.name} ({channel.type}) | send: {perms.send_messages}, "
                f"read: {perms.read_messages}, visibility: {visibility}"
            )
        events_logger.info(
            f"Channels in {guild.name}:\n" + "\n".join(channels_info)
        )

        members_info = []
        for member in guild.members:
            roles = [role.name for role in member.roles if role.name != "@everyone"]
            members_info.append(
                f"{member} (id={member.id}) | nick: {member.display_name}, "
                f"status: {member.status}, roles: {roles}"
            )

        events_logger.info(f"Members in {guild.name}:\n" + "\n".join(members_info))

    @bot.event
    async def on_guild_remove(guild: discord.Guild) -> None:
        events_logger.info(f"Removed from server: {guild.name} (id={guild.id})")
