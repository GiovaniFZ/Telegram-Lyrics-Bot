from services.bot_service import BotService, ReplyMarkup

async def start(bot_service: BotService, update, _context) -> None:
    """Send a message when the command /start is issued."""
    user = bot_service.get_user(update)
    await bot_service.send_message(
        update,
        rf"Hi {user.mention_html()}, welcome to Lyrics bot! Use /help to see how to get lyrics.",
        parse_mode="HTML",
        reply_markup=ReplyMarkup.FORCE_REPLY,
    )
