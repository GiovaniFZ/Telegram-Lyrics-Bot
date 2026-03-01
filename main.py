import logging
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, welcome to Lyrics bot!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Not available yet")


async def getLyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    url_base = "https://www.letras.mus.br/"
    full_url = f"{url_base}{update.message.text}" 
    response = requests.get(full_url)
    if response.status_code == 200:
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        div_class = soup.find('div', class_='lyric-original')
        if div_class is not None:
            lyrics_text = div_class.get_text(separator="\n", strip=True)
            await update.message.reply_text(lyrics_text)
        else:
            await update.message.reply_text("Lyrics not found.")
    else:
        await update.message.reply_text("Error fetching lyrics.")


def main() -> None:
    """Start the bot."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, getLyrics))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()