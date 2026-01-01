from fastapi import FastAPI, HTTPException
import os
import secrets
import hashlib
import base64
import requests

app = FastAPI(title="Incentive API")

# ===============================
# CONFIG (Render Environment)
# ===============================

ML_CLIENT_ID = os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = "https://testevaidarcerto.com.br/redirect"

# memória simples (depois vira banco)
PKCE_STORE = {}

# ===============================
# HEALTH
# ===============================

@app.get("/")
def health():
    return {"status": "ok"}

# ===============================
# STEP 1 – GERAR AUTH URL (PKCE)
# ===============================

@app.get("/ml/auth")
def ml_auth():

    code_verifier = secrets.token_urlsafe(64)

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().replace("=", "")

    state = secrets.token_urlsafe(16)

    PKCE_STORE[state] = code_verifier

    auth_url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={ML_CLIENT_ID}"
        f"&redirect_uri={ML_REDIRECT_URI}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={state}"
    )

    return {
        "auth_url": auth_url
    }

# ===============================
# STEP 2 – CALLBACK (TOKEN)
# ===============================

@app.get("/ml/callback")
def ml_callback(code: str, state: str):

    code_verifier = PKCE_STORE.get(state)

    if not code_verifier:
        raise HTTPException(status_code=400, detail="Invalid state")

    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": ML_CLIENT_ID,
            "client_secret": ML_CLIENT_SECRET,
            "code": code,
            "redirect_uri": ML_REDIRECT_URI,
            "code_verifier": code_verifier
        },
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()
