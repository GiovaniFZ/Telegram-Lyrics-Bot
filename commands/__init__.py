from .start import start
from .help import help_command
from .donation import donation_command
from .search import search_button_handler, start_search
from .source import source_code_command

__all__ = [
    "ARTIST",
    "SONG",
    "cancel",
    "donation_command",
    "help_command",
    "receive_artist",
    "receive_song",
    "search_button_handler",
    "source_code_command",
    "start",
    "start_lyrics",
    "start_search",
]


def __getattr__(name):
    if name in {"ARTIST", "SONG", "cancel", "receive_artist", "receive_song", "start_lyrics"}:
        from .lyrics_lookup import receive_info

        return getattr(receive_info, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")