import logging
from functools import partial
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

from telegram import ForceReply, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from adapters import TelegramBotService
from services import BotService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ARTIST, SONG = range(2)


async def start(
    bot_service: BotService,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Send a message when the command /start is issued."""
    user = bot_service.get_user(update)
    await bot_service.send_message(
        update,
        rf"Hi {user.mention_html()}, welcome to Lyrics bot! Use /help to see how to get lyrics.",
        parse_mode="HTML",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(
    bot_service: BotService,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
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


async def start_lyrics(
    bot_service: BotService,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Start a lyrics lookup conversation.""",

    await bot_service.send_message(update, "Artist Name:")
    return ARTIST


async def receive_artist(
    bot_service: BotService,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Store the artist and ask for the song name."""
    context.user_data["artist_name"] = update.message.text.strip()
    await bot_service.send_message(update, "Song Name:")
    return SONG

async def receive_song(
    bot_service: BotService,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Fetch and send the lyrics for the provided artist and song."""
    loading_message = await bot_service.send_message(update, "Loading, just a moment please...")
    artist_name = context.user_data.get("artist_name", "").strip()
    song_name = update.message.text.strip()
    url_base = "https://www.letras.mus.br/"
    full_url = f"{url_base}{artist_name}/{song_name}/"
    lyrics = await get_lyrics_with_url(full_url)
    await bot_service.edit_message(loading_message, lyrics)
    context.user_data.pop("artist_name", None)
    return ConversationHandler.END

async def get_lyrics_with_url(full_url: str) -> str:
    response = requests.get(full_url)
    if response.status_code == 200:
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        div_class = soup.find('div', class_='lyric-original')
        if div_class is not None:
            lyrics_text = div_class.get_text(separator="\n", strip=True)
            return lyrics_text
    return "Oops! The lyrics for this song was not found. Please check the artist and song name and try again."


async def cancel(
    bot_service: BotService,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel the current lyrics lookup."""
    context.user_data.pop("artist_name", None)
    await bot_service.send_message(update, "Lyrics search canceled.")
    return ConversationHandler.END

async def start_search(
    bot_service: BotService,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Search for lyrics using the provided query."""
    if not context.args:
        await bot_service.send_message(update, "Usage: /search <query>\nExample: /search Coldplay")
        return
    
    query = " ".join(context.args)
    
    loading_message = await bot_service.send_message(update, "Loading, just a moment please...")
    
    try:
        full_url = f"https://serpapi.com/search?engine=google&q=site:letras.mus.br+{query}"
        payload = {"api_key": os.getenv("SERPAPI_KEY")}
        response = requests.get(full_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "organic_results" in data and data["organic_results"]:
                top_results = data["organic_results"][:4]
                keyboard = []
                search_links = []

                for result in top_results:
                    title = result.get("title", "No title")
                    link = result.get("link")
                    callback_index = str(len(search_links))
                    keyboard.append([InlineKeyboardButton(title, callback_data=callback_index)])
                    search_links.append(link)

                if not search_links:
                    await bot_service.edit_message(loading_message, "No valid lyric links were found for your query.")
                    return

                context.user_data["search_links"] = search_links
                reply_markup = InlineKeyboardMarkup(keyboard)
                await bot_service.edit_message(loading_message, "Results found:", reply_markup=reply_markup)
            else:
                await bot_service.edit_message(loading_message, "No results found for your query.")
        else:
            await bot_service.edit_message(loading_message, "Error searching for lyrics. Please try again later.")
    except Exception as e:
        logger.error(f"Search error: {e}")
        await bot_service.edit_message(loading_message, "An error occurred while searching. Please try again later.")
        
async def search_button_handler(
    bot_service: BotService,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    if query is None:
        raise ValueError("The update does not contain a callback query.")

    await bot_service.answer_callback_query(update)
    await bot_service.edit_callback_message(update, "Loading, just a moment please...")

    search_links = context.user_data.get("search_links", [])
    try:
        chosenIndex = int(query.data)
    except (TypeError, ValueError):
        await bot_service.edit_callback_message(update, "Invalid selection. Please run /search again.")
        return

    if chosenIndex < 0 or chosenIndex >= len(search_links):
        await bot_service.edit_callback_message(update, "This selection is no longer valid. Please run /search again.")
        return

    url = search_links[chosenIndex]
    lyrics = await get_lyrics_with_url(url)
    context.user_data.pop("search_links", None)
    await bot_service.edit_callback_message(update, lyrics)
    
async def donation_command(
    bot_service: BotService,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
):
    await bot_service.send_message(
        update,
        "*Any help is welcome to help in Song Lyrics Bot development! Here is how you can donate:*\n\n"
        "• [Buy me a coffee](https://buymeacoffee.com/akaidk)\n"
        "• [Livepix](https://livepix.gg/akaidk)\n"
        f"*• USDT/ETH*: `{os.getenv("USDT_KEY")}`\n"
        f"*• BTC*: `{os.getenv("BTC_KEY")}`\n\n"
        "*For any other methods, please contact me at @akaidk.*"
        ,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
    return

async def source_code_command(
    bot_service: BotService,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
):
    await bot_service.send_message(
        update,
        "*The source code for SongLyricsBot is available on *"
        "[Github](https://github.com/GiovaniFZ/Telegram-Lyrics-Bot).\n"
        "Any contibutions are welcome! If you want to contribute, please fork the repository and submit a pull request.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


def main() -> None:
    """Start the bot."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    bot_service = TelegramBotService()

    application.add_handler(CommandHandler("start", partial(start, bot_service)))
    application.add_handler(CommandHandler("help", partial(help_command, bot_service)))
    application.add_handler(CommandHandler("donation", partial(donation_command, bot_service)))
    application.add_handler(CommandHandler("source", partial(source_code_command, bot_service)))
    application.add_handler(CommandHandler("search", partial(start_search, bot_service), filters=None))
    application.add_handler(CallbackQueryHandler(partial(search_button_handler, bot_service)))

    lyrics_conversation = ConversationHandler(
        entry_points=[CommandHandler("lyrics", partial(start_lyrics, bot_service))],
        states={
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, partial(receive_artist, bot_service))],
            SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, partial(receive_song, bot_service))],
        },
        fallbacks=[CommandHandler("cancel", partial(cancel, bot_service))],
    )
    
    application.add_handler(lyrics_conversation)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()