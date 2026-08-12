from fatsecret import Fatsecret

class FatSecretAuthConnector:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str,
    ):
        self._client = Fatsecret(
            consumer_key,
            consumer_secret,
            session_token=(access_token, access_token_secret),
            auth="oauth1",
        )

    @property
    def client(self) -> Fatsecret:
        return self._client