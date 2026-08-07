import time
import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleAuthConnector:
    """
    Gère uniquement le cycle de vie OAuth2 Google : échange du refresh_token
    contre un access_token, avec cache en mémoire jusqu'à expiration.
    Composé par les connectors Google Health — ne fait aucun appel métier lui-même.
    """

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def get_access_token(self) -> str:
        if self._access_token is None or time.time() >= self._expires_at:
            self._refresh_access_token()
        return self._access_token

    def _refresh_access_token(self) -> None:
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        self._access_token = payload["access_token"]
        # marge de sécurité de 60s pour éviter d'utiliser un token expiré de justesse
        self._expires_at = time.time() + payload["expires_in"] - 60