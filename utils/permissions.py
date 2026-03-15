import json


with open("config/servers.json", encoding="utf-8") as f:
    config = json.load(f)

def is_allowed(ctx, command_name: str) -> bool:
    """
    Checks if the command is allowed on the current server.
    
    Args:
        command_name (str): the input command.

    Returns:
        bool: the result.
    """
    guild_id = str(ctx.guild.id)
    allowed = config.get(guild_id, {}).get("allowed_commands", [])

    return command_name in allowed
