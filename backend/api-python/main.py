from fastapi import FastAPI
import requests
from ml import get_app_token

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/ml/sites")
def get_sites():
    token = get_app_token()

    response = requests.get(
        "https://api.mercadolibre.com/sites/MLB",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()
