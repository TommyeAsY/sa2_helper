import logging
import logging.handlers
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

messages_logger = logging.getLogger("discord_bot.messages")
messages_logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "messages.log"),
    maxBytes=32 * 1024 * 1024, #32 MB
    backupCount=10,
    encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
messages_logger.addHandler(handler)
