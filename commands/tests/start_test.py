import asyncio

from commands import start
from adapters.mock_bot_service import MockBotService
from services.bot_service import ReplyMarkup

def test_start_command():
    mock_bot_service = MockBotService()
    update = object()

    asyncio.run(start(bot_service=mock_bot_service, update=update, _context=None))

    assert len(mock_bot_service.messages) == 1
    message = mock_bot_service.messages[0]
    assert message.update is update
    assert message.text == (
        'Hi <a href="tg://user?id=1">mock user</a>, '
        "welcome to Lyrics bot! Use /help to see how to get lyrics."
    )
    assert message.parse_mode == "HTML"
    assert message.reply_markup == ReplyMarkup.FORCE_REPLY