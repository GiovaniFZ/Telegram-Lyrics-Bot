from services.os_service import OSService
import os


class RealOSService(OSService):
    def getEnv(self, key: str) -> str | None:
        return os.getenv(key)