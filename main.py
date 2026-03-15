from config.settings import settings
from discord_bot.bot import create_bot


bot = create_bot()

bot.run(settings.discord_token)