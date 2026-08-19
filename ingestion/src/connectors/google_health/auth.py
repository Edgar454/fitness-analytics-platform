import time
import httpx

TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleAuthConnector:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    async def get_access_token(self) -> str:
        if self._access_token is None or time.time() >= self._expires_at:
            await self._refresh_access_token()
        return self._access_token

    async def _refresh_access_token(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
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
        self._expires_at = time.time() + payload["expires_in"] - 60