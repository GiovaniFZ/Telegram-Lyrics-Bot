import asyncio

from commands import start
from adapters.mock_bot_service import MockBotService
from adapters.mock_os_service import MockOSService
from types import SimpleNamespace
from commands import donation_command

def test_donation_command():
    bot = MockBotService()
    os_service = MockOSService()
    update = object()
    
    asyncio.run(donation_command(bot, os_service, update, None))

    message = bot.messages[0]
    assert message.update is update
    assert "value-USDT_KEY" in message.text
    assert "value-BTC_KEY" in message.text
    assert message.parse_mode == "Markdown"
    assert message.disable_web_page_preview is True
    assert bot.sent_messages["msg"] == message.text
    assert bot.parse_modes["parse_mode"] == "Markdown"