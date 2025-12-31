import os
import time
import requests

ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

_client_id = os.getenv("ML_CLIENT_ID")
_client_secret = os.getenv("ML_CLIENT_SECRET")

_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def get_app_token() -> str:
    """
    Gera token de aplicação (client_credentials)
    com cache automático
    """
    now = time.time()

    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    response = requests.post(
        ML_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": _client_id,
            "client_secret": _client_secret,
        },
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"] - 60

    return data["access_token"]
