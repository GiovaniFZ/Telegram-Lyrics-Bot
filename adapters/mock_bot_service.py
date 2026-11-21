from dataclasses import dataclass
from html import escape

from services import BotService
from services.bot_service import ReplyMarkup


@dataclass
class MockUser:
    def __init__(self, id: int, first_name: str, last_name:str, update: object):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.update = update

    def mention_html(self, name: str | None = None) -> str:
        full_name = " ".join(part for part in (self.first_name, self.last_name) if part)
        return f'<a href="tg://user?id={self.id}">{escape(name or full_name)}</a>'


@dataclass
class MockMessage:
    update: object
    text: str
    parse_mode: str | None = None
    disable_web_page_preview: bool | None = None
    reply_markup: ReplyMarkup | object | None = None


class MockBotService(BotService):
    def __init__(self):
        self.sent_messages = {}
        self.parse_modes = {}
        self.update = ()
        self.messages: list[MockMessage] = []
        self.edited_messages: list[tuple[MockMessage, str, object]] = []
        self.callback_messages: list[tuple[object, str]] = []
        self.answered_callbacks: list[object] = []
        self.inline_markups = {}
        self.inline_keyboard_buttons: list[object] = []

    async def send_message(
        self,
        update,
        msg: str,
        *,
        parse_mode: str | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> MockMessage:
        self.sent_messages["msg"] = msg
        self.parse_modes["parse_mode"] = parse_mode
        self.update = update
        message = MockMessage(
            update, msg, parse_mode, disable_web_page_preview, reply_markup
        )
        self.messages.append(message)
        return message

    async def edit_message(
        self,
        message: MockMessage,
        msg: str,
        *,
        reply_markup: ReplyMarkup | object | None = None,
    ) -> MockMessage:
        self.edited_messages.append((message, msg, reply_markup))
        message.text = msg
        message.reply_markup = reply_markup
        return message

    async def edit_callback_message(self, update, msg: str) -> MockMessage:
        if update.callback_query is None:
            raise ValueError("The update does not contain a callback query.")
        self.callback_messages.append((update, msg))
        return MockMessage(update, msg)

    async def answer_callback_query(self, update) -> bool:
        if update.callback_query is None:
            raise ValueError("The update does not contain a callback query.")
        self.answered_callbacks.append(update)
        return True

    def get_inline_markup(self, keyboard: list):
        self.inline_markups["keyboard"] = keyboard
        return keyboard

    def get_inline_keyboard_button(
        self, btn_title: str, callback_data: str | object | None
    ):
        button = {
            "btn_title": btn_title,
            "callback_data": callback_data
        }
        self.inline_keyboard_buttons.append(button)
        return button

    def get_user(self, update):
        user = MockUser(id=1, first_name="mock", last_name="user", update=update)
        return user