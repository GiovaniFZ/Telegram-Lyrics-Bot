from telegram import ForceReply, InlineKeyboardMarkup, Message, Update, User

from services import BotService


class TelegramBotService(BotService):
    async def send_message(
        self,
        update: Update,
        msg: str,
        *,
        parse_mode: str | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: ForceReply | InlineKeyboardMarkup | None = None,
    ) -> Message:
        message = update.effective_message
        if message is None:
            raise ValueError("The update does not contain a message.")

        return await message.reply_text(
            msg,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )

    async def edit_message(
        self,
        message: Message,
        msg: str,
        *,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        return await message.edit_text(msg, reply_markup=reply_markup)

    async def edit_callback_message(self, update: Update, msg: str) -> Message | bool:
        query = update.callback_query
        if query is None:
            raise ValueError("The update does not contain a callback query.")

        return await query.edit_message_text(msg)

    async def answer_callback_query(self, update: Update) -> bool:
        query = update.callback_query
        if query is None:
            raise ValueError("The update does not contain a callback query.")

        return await query.answer()

    def get_user(self, update: Update) -> User:
        user = update.effective_user
        if user is None:
            raise ValueError("The update does not contain an effective user.")

        return user