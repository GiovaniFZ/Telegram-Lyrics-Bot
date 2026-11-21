import logging
from services import BotService, Requester

from commands.lyrics_lookup.fetch_lyrics import get_lyrics_with_url

logger = logging.getLogger(__name__)


async def start_search(
    bot_service: BotService,
    requester: Requester,
    update,
    context,
) -> None:
    """Search for lyrics using the provided query."""
    if not context.args:
        await bot_service.send_message(
            update,
            "Usage: /search <query>\nExample: /search Coldplay",
        )
        return

    query = " ".join(context.args)
    loading_message = await bot_service.send_message(
        update, "Loading, just a moment please..."
    )
    
    is_available = True

    if (is_available):
        try:
            full_url = f"https://test-0k.onrender.com/suggestion?q={query}&limit=4"
            response = requester.request(full_url)

            if response.status_code != 200:
                await bot_service.edit_message(
                    loading_message,
                    "Error searching for lyrics. Please try again later.",
                )
                print(response.json())
                return

            data = response.json()
            organic_results = data.get("results", [])
            if not organic_results:
                await bot_service.edit_message(
                    loading_message, "No results found for your query."
                )
                return

            keyboard = []
            callbacks = []
            for result in organic_results[:4]:
                title = result.get("title", "No title")
                artist = result.get("artist")
                btn_title = f"{artist} - {title}"
        
                callback_index = str(len(callbacks))
                keyboard.append(
                    [bot_service.get_inline_keyboard_button(btn_title, callback_data=callback_index)]
                )
                callbacks.append({
                    "artist": artist,
                    "title": title
                })

            context.user_data["callbacks"] = callbacks
            reply_markup = bot_service.get_inline_markup(keyboard)
            await bot_service.edit_message(
                loading_message,
                "Results found:",
                reply_markup=reply_markup,
            )
        except Exception as error:
            logger.error("Search error: %s", error)
            await bot_service.edit_message(
                loading_message,
                "An error occurred while searching. Please try again later.",
            )
    else:
        await bot_service.send_message(update, "Search service unavailable for now. Come back later!")


async def search_button_handler(
    bot_service: BotService,
    requester: Requester,
    update,
    context,
) -> None:
    query = update.callback_query
    if query is None:
        raise ValueError("The update does not contain a callback query.")

    await bot_service.answer_callback_query(update)
    await bot_service.edit_callback_message(
        update, "Loading, just a moment please..."
    )

    callbacks: list = context.user_data.get("callbacks", [])
    try:
        chosen_index = int(query.data)
    except (TypeError, ValueError):
        await bot_service.edit_callback_message(
            update, "Invalid selection. Please run /search again."
        )
        return

    chosen_data = callbacks[chosen_index]
    chosen_artist = chosen_data.get("artist")
    chosen_song = chosen_data.get("title")
    full_url = f"https://test-0k.onrender.com/lyrics/?artist={chosen_artist}&song={chosen_song}/"
    lyrics = await get_lyrics_with_url(requester, full_url)
    context.user_data.pop("callbacks", None)
    await bot_service.edit_callback_message(update, lyrics)
