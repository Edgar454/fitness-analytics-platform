class LyftaAuthConnector:
    """
    Auth Lyfta officielle (API publique documentée) : simple clé API statique,
    pas de cycle OAuth à gérer contrairement à Google Health.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"}