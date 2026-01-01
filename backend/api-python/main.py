from fastapi import FastAPI, HTTPException, Query
import os
import requests
import secrets
import hashlib
import base64

app = FastAPI(title="Incentive API")

# ======================================================
# CONFIGURAÇÕES (via Environment Variables no Render)
# ======================================================

ML_CLIENT_ID = os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.getenv(
    "ML_REDIRECT_URI",
    "https://testevaidarcerto.com.br/redirect"
)

# ======================================================
# PKCE + STATE (memória simples – depois vira banco)
# ======================================================

OAUTH_MEMORY = {}

def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier: str):
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# 1️⃣ INICIAR AUTH (gera URL Mercado Livre)
# ======================================================

@app.get("/ml/auth")
def ml_auth():

    state = secrets.token_urlsafe(32)
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # salva tudo em memória
    OAUTH_MEMORY[state] = {
        "code_verifier": code_verifier
    }

    auth_url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={ML_CLIENT_ID}"
        f"&redirect_uri={ML_REDIRECT_URI}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={state}"
    )

    return {"auth_url": auth_url}

# ======================================================
# 2️⃣ CALLBACK (troca CODE por TOKEN)
# ======================================================

@app.get("/ml/callback")
def ml_callback(
    code: str = Query(...),
    state: str = Query(...)
):

    if state not in OAUTH_MEMORY:
        raise HTTPException(status_code=400, detail="Invalid state")

    code_verifier = OAUTH_MEMORY[state]["code_verifier"]

    token_response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": ML_CLIENT_ID,
            "client_secret": ML_CLIENT_SECRET,
            "code": code,
            "redirect_uri": ML_REDIRECT_URI,
            "code_verifier": code_verifier
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=10
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=token_response.status_code,
            detail=token_response.text
        )

    token_data = token_response.json()

    return {
        "message": "OAuth concluído com sucesso",
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "user_id": token_data.get("user_id"),
        "expires_in": token_data.get("expires_in")
    }
