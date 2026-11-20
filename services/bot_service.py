from abc import ABC, abstractmethod

from telegram import ForceReply, InlineKeyboardMarkup, Message, Update, User


class BotService(ABC):
    @abstractmethod
    async def send_message(
        self,
        update: Update,
        msg: str,
        *,
        parse_mode: str | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: ForceReply | InlineKeyboardMarkup | None = None,
    ) -> Message:
        pass

    @abstractmethod
    async def edit_message(
        self,
        message: Message,
        msg: str,
        *,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        pass

    @abstractmethod
    async def edit_callback_message(self, update: Update, msg: str) -> Message | bool:
        pass

    @abstractmethod
    async def answer_callback_query(self, update: Update) -> bool:
        pass

    @abstractmethod
    def get_user(self, update: Update) -> User:
        pass