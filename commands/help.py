from services.bot_service import BotService

async def help_command(
    bot_service: BotService,
    update,
    _context,
) -> None:
    """Send a message when the command /help is issued."""
    await bot_service.send_message(
        update,
        "*Commands:*\n"
    "/lyrics - Get lyrics for a specific song\n"
        "/search <query> - Search for lyrics using a query (e.g., artist or song name)\n"
        "/cancel - Cancel a current operation. Use this command during a lyrics lookup conversation to stop the process.\n"
        "/source - Get the source code\n"
        "/donation - Support the development\n\n",
        parse_mode="Markdown"
    )