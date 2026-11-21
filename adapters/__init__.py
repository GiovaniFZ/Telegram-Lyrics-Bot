__all__ = ["HttpRequester", "TelegramBotService"]


def __getattr__(name):
    if name == "HttpRequester":
        from .http_requester import HttpRequester

        return HttpRequester
    if name == "TelegramBotService":
        from .telegram_bot_service import TelegramBotService

        return TelegramBotService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
