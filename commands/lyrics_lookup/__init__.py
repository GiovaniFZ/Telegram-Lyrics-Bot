from .fetch_lyrics import get_lyrics_with_url

__all__ = [
    "ARTIST",
    "SONG",
    "cancel",
    "get_lyrics_with_url",
    "receive_artist",
    "receive_song",
    "start_lyrics",
]


def __getattr__(name):
    if name in {"ARTIST", "SONG", "cancel", "receive_artist", "receive_song", "start_lyrics"}:
        from . import receive_info

        return getattr(receive_info, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")