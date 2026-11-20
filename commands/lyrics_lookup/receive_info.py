from telegram.ext import ConversationHandler

from services.bot_service import BotService
from services.requester_service import Requester
from commands.lyrics_lookup.fetch_lyrics import get_lyrics_with_url

ARTIST, SONG = range(2)

async def start_lyrics(
    bot_service: BotService,
    update,
    _context
) -> int:
    """Start a lyrics lookup conversation.""",

    await bot_service.send_message(update, "Artist Name:")
    return ARTIST


async def receive_artist(
    bot_service: BotService,
    update,
    context
) -> int:
    """Store the artist and ask for the song name."""
    context.user_data["artist_name"] = update.message.text.strip()
    await bot_service.send_message(update, "Song Name:")
    return SONG


async def receive_song(
    bot_service: BotService,
    requester: Requester,
    update,
    context,
) -> int:
    """Fetch and send the lyrics for the provided artist and song."""
    loading_message = await bot_service.send_message(
        update, "Loading, just a moment please..."
    )
    artist_name = context.user_data.get("artist_name", "").strip()
    song_name = update.message.text.strip()
    full_url = f"https://test-0k.onrender.com/lyrics/?artist={artist_name}&song={song_name}/"
    lyrics = await get_lyrics_with_url(requester, full_url)
    await bot_service.edit_message(loading_message, lyrics)
    context.user_data.pop("artist_name", None)
    return ConversationHandler.END


async def cancel(
    bot_service: BotService,
    update,
    context,
) -> int:
    """Cancel the current lyrics lookup."""
    context.user_data.pop("artist_name", None)
    await bot_service.send_message(update, "Lyrics search canceled.")
    return ConversationHandler.END