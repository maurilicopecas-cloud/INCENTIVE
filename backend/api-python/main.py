from fastapi import FastAPI, HTTPException, Request
import requests
import os

app = FastAPI(title="Incentive API")

# ===============================
# CONFIGURAÇÕES (ENV VARS)
# ===============================

CLIENT_ID = os.getenv("ML_CLIENT_ID")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
REDIRECT_URI = "https://testevaidarcerto.com.br/redirect"

# ===============================
# HEALTH
# ===============================

@app.get("/")
def health():
    return {"status": "ok"}

# ===============================
# PASSO 1 — REDIRECT PARA O MELI
# ===============================

@app.get("/ml/auth")
def ml_auth():
    url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return {"auth_url": url}

# ===============================
# PASSO 2 — CALLBACK (CODE)
# ===============================

@app.get("/ml/callback")
def ml_callback(code: str):
    token_response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        timeout=10
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=token_response.status_code,
            detail=token_response.text
        )

    return token_response.json()

# ===============================
# TESTE SELLER (COM TOKEN FIXO)
# ===============================

@app.get("/ml/seller/{seller_id}")
def seller_items(seller_id: int):
    ACCESS_TOKEN = os.getenv("ML_ACCESS_TOKEN")

    r = requests.get(
        "https://api.mercadolibre.com/sites/MLB/search",
        params={"seller_id": seller_id, "limit": 20},
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        },
        timeout=10
    )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    items = []
    for item in r.json().get("results", []):
        items.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "price": item.get("price"),
            "thumbnail": item.get("thumbnail")
        })

    return {
        "seller_id": seller_id,
        "total": len(items),
        "items": items
    }
