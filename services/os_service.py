from abc import ABC, abstractmethod

class OSService(ABC):
    @abstractmethod
    def getEnv(self, key: str) -> str | None:
        pass