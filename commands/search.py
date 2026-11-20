import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services import OSService, Requester

from commands.lyrics_lookup.fetch_lyrics import get_lyrics_with_url
from services.bot_service import BotService

logger = logging.getLogger(__name__)


async def start_search(
    bot_service: BotService,
    os_service: OSService,
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
    
    is_available = False

    if (is_available):
        try:
            full_url = (
                "https://serpapi.com/search"
                f"?engine=google&q=site:letras.mus.br+{query}"
            )
            payload = {"api_key": os_service.getEnv("SERPAPI_KEY")}
            response = requester.request(full_url, json=payload)

            if response.status_code != 200:
                await bot_service.edit_message(
                    loading_message,
                    "Error searching for lyrics. Please try again later.",
                )
                return

            data = response.json()
            organic_results = data.get("organic_results", [])
            if not organic_results:
                await bot_service.edit_message(
                    loading_message, "No results found for your query."
                )
                return

            keyboard = []
            search_links = []
            for result in organic_results[:4]:
                title = result.get("title", "No title")
                link = result.get("link")
                if not link:
                    continue

                callback_index = str(len(search_links))
                keyboard.append(
                    [InlineKeyboardButton(title, callback_data=callback_index)]
                )
                search_links.append(link)

            if not search_links:
                await bot_service.edit_message(
                    loading_message,
                    "No valid lyric links were found for your query.",
                )
                return

            context.user_data["search_links"] = search_links
            reply_markup = InlineKeyboardMarkup(keyboard)
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

    search_links = context.user_data.get("search_links", [])
    try:
        chosen_index = int(query.data)
    except (TypeError, ValueError):
        await bot_service.edit_callback_message(
            update, "Invalid selection. Please run /search again."
        )
        return

    if chosen_index < 0 or chosen_index >= len(search_links):
        await bot_service.edit_callback_message(
            update,
            "This selection is no longer valid. Please run /search again.",
        )
        return

    url = search_links[chosen_index]
    lyrics = await get_lyrics_with_url(requester, url)
    context.user_data.pop("search_links", None)
    await bot_service.edit_callback_message(update, lyrics)
