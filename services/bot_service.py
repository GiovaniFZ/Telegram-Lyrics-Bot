from abc import ABC, abstractmethod
from enum import Enum

class ReplyMarkup(Enum):
    FORCE_REPLY = "FORCE_REPLY"
    INLINE_KEYBOARD_MARKUP = "INLINE_KEYBOARD_MARKUP"

class BotService(ABC):
    @abstractmethod
    async def send_message(
        self,
        update,
        msg: str,
        *,
        parse_mode: str | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ):
        pass

    @abstractmethod
    async def edit_message(
        self,
        message,
        msg: str,
        *,
        reply_markup: ReplyMarkup | object | None = None,
    ):
        pass

    @abstractmethod
    async def edit_callback_message(self, update, msg: str):
        pass

    @abstractmethod
    async def answer_callback_query(self, update) -> bool:
        pass

    @abstractmethod
    def get_user(self, update):
        pass