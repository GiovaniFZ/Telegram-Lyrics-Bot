from services import OSService

class MockOSService(OSService):
    def getEnv(self, key):
        return f"value-{key}"