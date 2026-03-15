from config.errors_logs import errors_logger


def register_error_handlers(bot):
    @bot.event
    async def on_error(event, *args, **kwargs):
        errors_logger.exception(f"Unhandled error in event {event}", exc_info=True)
