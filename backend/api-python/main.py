from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(title="Incentive API - OAuth ML")

# =========================
# CONFIGURAÇÕES (Render ENV)
# =========================
CLIENT_ID = os.getenv("ML_CLIENT_ID")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ML_REDIRECT_URI")

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {"status": "ok"}

# =========================
# PASSO 1 — GERAR URL OAUTH
# =========================
@app.get("/ml/auth")
def ml_auth():
    auth_url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    return {"auth_url": auth_url}

# =========================
# PASSO 2 — TROCAR CODE POR TOKEN
# =========================
@app.get("/ml/callback")
def ml_callback(code: str):
    response = requests.post(
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

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()
