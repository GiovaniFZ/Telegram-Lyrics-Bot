import asyncio
import subprocess
import sys
from types import SimpleNamespace

import pytest

from adapters.mock_bot_service import MockBotService, MockUser
from commands.donation import donation_command
from commands.search import search_button_handler, start_search

def test_search_records_keyboard_and_callback():
    bot = MockBotService()
    response = SimpleNamespace(
        status_code=200,
        json=lambda: {"results": [{"artist": "Artist", "title": "Song"}]},
    )
    requester = SimpleNamespace(request=lambda url: response)
    context = SimpleNamespace(args=["Song"], user_data={})
    update = SimpleNamespace(callback_query=SimpleNamespace(data="0"))

    asyncio.run(start_search(bot, requester, update, context))

    message = bot.messages[0]
    button = message.reply_markup[0][0]
    assert message.text == "Results found:"
    assert button == {"btn_title": "Artist - Song", "callback_data": "0"}
    assert bot.edited_messages[0][0] is message

    requester.request = lambda url: SimpleNamespace(
        status_code=200, json=lambda: {"data": {"lyrics": "Example lyrics"}}
    )
    asyncio.run(search_button_handler(bot, requester, update, context))

    assert bot.answered_callbacks == [update]
    assert bot.callback_messages == [
        (update, "Loading, just a moment please..."),
        (update, "Example lyrics"),
    ]
    assert "callbacks" not in context.user_data


def test_mock_user_and_missing_callback_data():
    bot = MockBotService()
    update = SimpleNamespace(callback_query=None)
    user = MockUser(id=123, first_name="Test <User>", last_name="Example", update=update)

    assert user.mention_html() == (
        '<a href="tg://user?id=123">Test &lt;User&gt; Example</a>'
    )
    assert user.mention_html("Name & more") == (
        '<a href="tg://user?id=123">Name &amp; more</a>'
    )
    assert bot.get_user(update).update is update

    with pytest.raises(ValueError, match="callback query"):
        asyncio.run(bot.answer_callback_query(update))
    with pytest.raises(ValueError, match="callback query"):
        asyncio.run(bot.edit_callback_message(update, "text"))


def test_mock_and_start_do_not_require_infrastructure_dependencies():
    code = """
import asyncio
from adapters.mock_bot_service import MockBotService
from commands.start import start

bot = MockBotService()
asyncio.run(start(bot, object(), None))
assert '<a href="tg://user?id=1">mock user</a>' in bot.messages[0].text
"""
    subprocess.run([sys.executable, "-S", "-c", code], check=True)
