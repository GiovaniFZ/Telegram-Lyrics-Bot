from abc import ABC, abstractmethod

class Requester(ABC):
    @abstractmethod
    def request(self, full_url: str, json: object | None = None) -> object:
        pass