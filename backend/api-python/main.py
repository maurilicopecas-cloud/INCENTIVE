from fastapi import FastAPI, HTTPException
import requests
import os
from urllib.parse import urlencode

app = FastAPI(title="Incentive API - Mercado Livre")

# ======================================================
# CONFIG
# ======================================================

ML_CLIENT_ID = os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")

ML_AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

# armazenamento simples (depois vira banco)
SELLER_TOKENS = {}

# ======================================================
# HEALTH
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# 1️⃣ LOGIN OAUTH
# ======================================================

@app.get("/ml/oauth/login")
def ml_oauth_login():
    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": ML_REDIRECT_URI
    }
    url = f"{ML_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": url}

# ======================================================
# 2️⃣ CALLBACK
# ======================================================

@app.get("/ml/oauth/callback")
def ml_oauth_callback(code: str):
    payload = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI
    }

    response = requests.post(ML_TOKEN_URL, data=payload, timeout=10)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=response.text
        )

    data = response.json()

    seller_id = data["user_id"]
    SELLER_TOKENS[seller_id] = data

    return {
        "message": "Seller autorizado com sucesso",
        "seller_id": seller_id
    }

# ======================================================
# 3️⃣ ITENS DO SELLER (COM TOKEN)
# ======================================================

@app.get("/ml/seller/{seller_id}")
def get_seller_items(seller_id: int):
    token_data = SELLER_TOKENS.get(seller_id)

    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Seller não autorizado. Faça OAuth primeiro."
        )

    access_token = token_data["access_token"]

    search = requests.get(
        "https://api.mercadolibre.com/sites/MLB/search",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            "seller_id": seller_id,
            "limit": 20
        },
        timeout=10
    )

    if search.status_code != 200:
        raise HTTPException(
            status_code=search.status_code,
            detail=search.text
        )

    results = search.json().get("results", [])
    items = []

    for item in results:
        item_id = item["id"]

        item_resp = requests.get(
            f"https://api.mercadolibre.com/items/{item_id}",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )

        if item_resp.status_code != 200:
            continue

        item_data = item_resp.json()

        images = [
            pic.get("secure_url")
            for pic in item_data.get("pictures", [])
        ]

        items.append({
            "item_id": item_id,
            "title": item_data.get("title"),
            "price": item_data.get("price"),
            "images": images
        })

    return {
        "seller_id": seller_id,
        "total_items": len(items),
        "items": items
    }
