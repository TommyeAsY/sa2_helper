from rag.parsing_knowledge import parse_guild


class DiscordGuildParser:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id

    async def parse(self, guild):
        return await parse_guild(guild)
