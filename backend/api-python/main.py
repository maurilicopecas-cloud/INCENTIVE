import os
import secrets
import hashlib
import base64
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Incentive API - Mercado Livre OAuth PKCE")

# ================== CONFIG ==================
ML_CLIENT_ID = os.environ.get("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.environ.get("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.environ.get("ML_REDIRECT_URI")

if not ML_CLIENT_ID or not ML_CLIENT_SECRET or not ML_REDIRECT_URI:
    raise Exception("Variáveis ML_CLIENT_ID, ML_CLIENT_SECRET e ML_REDIRECT_URI são obrigatórias")

# ================== STORAGE TEMP ==================
# Em produção → banco / redis
OAUTH_STORE = {}

# ================== HELPERS ==================
def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(verifier: str):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

# ================== HEALTH ==================
@app.get("/")
def health():
    return {"status": "ok"}

# ================== AUTH ==================
@app.get("/ml/auth")
def ml_auth():
    state = secrets.token_urlsafe(32)
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    OAUTH_STORE[state] = {
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

# ================== CALLBACK ==================
@app.get("/ml/callback")
def ml_callback(code: str = None, state: str = None):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    if state not in OAUTH_STORE:
        raise HTTPException(status_code=400, detail="Invalid state")

    code_verifier = OAUTH_STORE[state]["code_verifier"]
    OAUTH_STORE.pop(state, None)

    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI,
        "code_verifier": code_verifier
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data=data,
        headers=headers,
        timeout=15
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
