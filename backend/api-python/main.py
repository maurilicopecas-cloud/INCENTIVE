from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(title="Incentive API")

# ==========================
# CONFIGURAÇÕES
# ==========================

CLIENT_ID = os.getenv("ML_CLIENT_ID")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
REDIRECT_URI = "https://testevaidarcerto.com.br/redirect"

ML_AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

# ==========================
# HEALTH CHECK
# ==========================

@app.get("/")
def health():
    return {"status": "ok"}

# ==========================
# 1️⃣ INICIAR OAUTH
# ==========================

@app.get("/ml/auth")
def ml_auth():
    auth_url = (
        f"{ML_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return {"auth_url": auth_url}

# ==========================
# 2️⃣ CALLBACK (REDIRECT)
# ==========================

@app.get("/ml/callback")
def ml_callback(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(ML_TOKEN_URL, data=data, timeout=10)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()

# ==========================
# 3️⃣ TESTE SELLER (COM TOKEN)
# ==========================

@app.get("/ml/seller/{seller_id}")
def get_seller_items(seller_id: int, access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    search = requests.get(
        "https://api.mercadolibre.com/sites/MLB/search",
        params={"seller_id": seller_id, "limit": 50},
        headers=headers,
        timeout=10
    )

    if search.status_code != 200:
        raise HTTPException(
            status_code=search.status_code,
            detail=search.text
        )

    items = []

    for item in search.json().get("results", []):
        item_id = item["id"]

        item_detail = requests.get(
            f"https://api.mercadolibre.com/items/{item_id}",
            headers=headers,
            timeout=10
        )

        if item_detail.status_code != 200:
            continue

        data = item_detail.json()

        images = [p["secure_url"] for p in data.get("pictures", [])]

        items.append({
            "id": item_id,
            "title": data.get("title"),
            "price": data.get("price"),
            "images": images
        })

    return {
        "seller_id": seller_id,
        "total": len(items),
        "items": items
    }
