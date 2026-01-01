from fastapi import FastAPI, HTTPException, Query
import requests
import secrets
import base64
import hashlib
import os

app = FastAPI(title="Incentive API")

# =========================
# CONFIGURAÇÕES
# =========================

ML_CLIENT_ID = "2290751302100143"
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
REDIRECT_URI = "https://testevaidarcerto.com.br/redirect"

# Em produção isso deveria ir para banco ou cache
OAUTH_TEMP_STORAGE = {}

# =========================
# HEALTH
# =========================

@app.get("/")
def health():
    return {"status": "ok"}

# =========================
# PASSO 1 — GERAR AUTH URL
# =========================

@app.get("/ml/auth")
def ml_auth():

    code_verifier = secrets.token_urlsafe(64)

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode("utf-8")

    state = secrets.token_urlsafe(32)

    # guardar temporariamente
    OAUTH_TEMP_STORAGE[state] = {
        "code_verifier": code_verifier
    }

    auth_url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={ML_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={state}"
    )

    return {
        "auth_url": auth_url
    }

# =========================
# PASSO 2 — CALLBACK
# =========================

@app.get("/ml/callback")
def ml_callback(
    code: str = Query(...),
    state: str = Query(...)
):

    if state not in OAUTH_TEMP_STORAGE:
        raise HTTPException(status_code=400, detail="Invalid state")

    code_verifier = OAUTH_TEMP_STORAGE[state]["code_verifier"]

    token_response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "authorization_code",
            "client_id": ML_CLIENT_ID,
            "client_secret": ML_CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier
        },
        timeout=10
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=token_response.status_code,
            detail=token_response.text
        )

    return token_response.json()
