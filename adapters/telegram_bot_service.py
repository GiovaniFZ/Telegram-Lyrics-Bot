from telegram import ForceReply, InlineKeyboardMarkup, Message, Update, User, InlineKeyboardButton

from services.bot_service import BotService, ReplyMarkup

class TelegramBotService(BotService):
    
    def __get_telegram_reply_markup(self, reply_markup: ReplyMarkup | object | None):
        if reply_markup == ReplyMarkup.FORCE_REPLY:
            return ForceReply()
        if reply_markup == ReplyMarkup.INLINE_KEYBOARD_MARKUP:
            return InlineKeyboardMarkup([])
        if isinstance(reply_markup, (ForceReply, InlineKeyboardMarkup)):
            return reply_markup
        return None
    
    async def send_message(
        self,
        update: Update,
        msg: str,
        *,
        parse_mode: str | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        message = update.effective_message
        if message is None:
            raise ValueError("The update does not contain a message.")

        return await message.reply_text(
            msg,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=self.__get_telegram_reply_markup(reply_markup),
        )

    async def edit_message(
        self,
        message: Message,
        msg: str,
        *,
        reply_markup: ReplyMarkup | InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        return await message.edit_text(msg, reply_markup=self.__get_telegram_reply_markup(reply_markup))

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
    
    def get_inline_markup(self, keyboard: list) -> None:
        return InlineKeyboardMarkup(keyboard)
    
    def get_inline_keyboard_button(self, btn_title: str, callback_data: str | object | None) -> None:
        return InlineKeyboardButton(btn_title, callback_data=callback_data)

    def get_user(self, update: Update) -> User:
        user = update.effective_user
        if user is None:
            raise ValueError("The update does not contain an effective user.")

        return user