from services.requester_service import Requester


async def get_lyrics_with_url(requester: Requester, full_url: str) -> str:
    response = requester.request(full_url)
    if response.status_code == 200:
        response_json = response.json()
        lyrics_data = response_json["data"]
        lyrics = lyrics_data["lyrics"]
        if lyrics is not None:
            return lyrics

    return (
        "Oops! The lyrics for this song was not found. "
        "Please check the artist and song name and try again."
    )