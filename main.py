import logging
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

from telegram import ForceReply, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ARTIST, SONG = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, welcome to Lyrics bot! Use /help to see how to get lyrics.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Commands:\n/lyrics - Get lyrics for a specific song\n/search <query> - Search for lyrics using a query (e.g., artist or song name)\n/cancel - Cancel the current lyrics lookup. Use this command during a lyrics lookup conversation to stop the process.")


async def start_lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start a lyrics lookup conversation."""
    await update.message.reply_text("Artist Name:")
    return ARTIST


async def receive_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the artist and ask for the song name."""
    context.user_data["artist_name"] = update.message.text.strip()
    await update.message.reply_text("Song Name:")
    return SONG

async def receive_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fetch and send the lyrics for the provided artist and song."""
    artist_name = context.user_data.get("artist_name", "").strip()
    song_name = update.message.text.strip()
    url_base = "https://www.letras.mus.br/"
    full_url = f"{url_base}{artist_name}/{song_name}/"
    lyrics = await get_lyrics_with_url(full_url)
    await update.message.reply_text(lyrics)
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current lyrics lookup."""
    context.user_data.pop("artist_name", None)
    await update.message.reply_text("Lyrics search canceled.")
    return ConversationHandler.END

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search for lyrics using the provided query."""
    if not context.args:
        await update.message.reply_text("Usage: /search <query>\nExample: /search Coldplay")
        return
    
    query = " ".join(context.args)
    
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
                    await update.message.reply_text("No valid lyric links were found for your query.")
                    return

                context.user_data["search_links"] = search_links
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Results found:", reply_markup=reply_markup)
            else:
                await update.message.reply_text("No results found for your query.")
        else:
            await update.message.reply_text("Error searching for lyrics. Please try again later.")
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("An error occurred while searching. Please try again later.")
        
async def search_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    search_links = context.user_data.get("search_links", [])
    try:
        chosenIndex = int(query.data)
    except (TypeError, ValueError):
        await query.edit_message_text("Invalid selection. Please run /search again.")
        return

    if chosenIndex < 0 or chosenIndex >= len(search_links):
        await query.edit_message_text("This selection is no longer valid. Please run /search again.")
        return

    url = search_links[chosenIndex]
    lyrics = await get_lyrics_with_url(url)
    context.user_data.pop("search_links", None)
    await query.edit_message_text(lyrics)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", start_search, filters=None))
    application.add_handler(CallbackQueryHandler(search_button_handler))

    lyrics_conversation = ConversationHandler(
        entry_points=[CommandHandler("lyrics", start_lyrics)],
        states={
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_artist)],
            SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_song)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(lyrics_conversation)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()