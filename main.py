import logging
from functools import partial
from dotenv import load_dotenv
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from adapters import HttpRequester, TelegramBotService
from adapters.real_os_service import RealOSService
from commands import (
    cancel,
    donation_command,
    help_command,
    receive_artist,
    receive_song,
    search_button_handler,
    source_code_command,
    start,
    start_lyrics,
    start_search,
)
from commands.lyrics_lookup.receive_info import ARTIST, SONG

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    bot_service = TelegramBotService()
    os_service = RealOSService()
    requester = HttpRequester()

    application.add_handler(CommandHandler("start", partial(start, bot_service)))
    application.add_handler(CommandHandler("help", partial(help_command, bot_service)))
    application.add_handler(CommandHandler("donation", partial(donation_command, bot_service, os_service)))
    application.add_handler(CommandHandler("source", partial(source_code_command, bot_service)))
    application.add_handler(
        CommandHandler(
            "search",
            partial(start_search, bot_service, os_service, requester),
            filters=None,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            partial(search_button_handler, bot_service, requester)
        )
    )

    lyrics_conversation = ConversationHandler(
        entry_points=[CommandHandler("lyrics", partial(start_lyrics, bot_service))],
        states={
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, partial(receive_artist, bot_service))],
            SONG: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    partial(receive_song, bot_service, requester),
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", partial(cancel, bot_service))],
    )
    
    application.add_handler(lyrics_conversation)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()