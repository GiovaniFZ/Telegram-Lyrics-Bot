import requests
from services.requester_service import Requester


class HttpRequester(Requester):
    def request(self, full_url: str, json: object | None = None) -> object:
        if json is None:
            return requests.get(full_url)
        return requests.get(full_url, json=json)