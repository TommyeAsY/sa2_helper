from json import load


with open("cfg/servers.json", encoding="utf-8") as f:
    config = load(f)

def is_allowed(ctx, command_name: str) -> bool:
    guild_id = str(ctx.guild.id)
    allowed = config.get(guild_id, {}).get("allowed_commands", [])
    return command_name in allowed
