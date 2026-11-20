from services.bot_service import BotService


async def source_code_command(
    bot_service: BotService,
    update,
    _context,
) -> None:
    await bot_service.send_message(
        update,
        "*The source code for SongLyricsBot is available on *"
        "[Github](https://github.com/GiovaniFZ/Telegram-Lyrics-Bot).\n"
        "Any contibutions are welcome! If you want to contribute, "
        "please fork the repository and submit a pull request.",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
