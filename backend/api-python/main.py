import os
import secrets
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

app = FastAPI(title="Incentive API - ML OAuth")

# ======== CONFIGURAÇÃO DA APP ========
ML_CLIENT_ID = os.environ.get("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.environ.get("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.environ.get("ML_REDIRECT_URI")  # ex: https://incentive-api-uuug.onrender.com/ml/callback

if not ML_CLIENT_ID or not ML_CLIENT_SECRET or not ML_REDIRECT_URI:
    raise Exception("Você precisa setar ML_CLIENT_ID, ML_CLIENT_SECRET e ML_REDIRECT_URI nas variáveis de ambiente")

# ======== STORE STATE TEMP (em memória por enquanto) ========
# Em produção salve em DB ou cache
STATE_STORE = {}

@app.get("/")
def health():
    return {"status": "incentive-api ok"}

# ======== GERAR AUTORIZAÇÃO URL ========
@app.get("/ml/auth")
def ml_auth():
    # gera state único
    state = secrets.token_urlsafe(16)
    STATE_STORE[state] = True

    auth_url = (
        "https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code"
        f"&client_id={ML_CLIENT_ID}"
        f"&redirect_uri={ML_REDIRECT_URI}"
        f"&state={state}"
    )

    return {"auth_url": auth_url}

# ======== CALLBACK ========
@app.get("/ml/callback")
def ml_callback(code: str = None, state: str = None):
    # valida state
    if not state or state not in STATE_STORE:
        raise HTTPException(status_code=400, detail="Invalid state")

    # remove state para segurança
    STATE_STORE.pop(state, None)

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # trocando code por access_token
    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data=data,
        headers=headers
    )

    if token_response.status_code != 200:
        raise HTTPException(status_code=token_response.status_code, detail=token_response.text)

    token_data = token_response.json()

    # Opcional: salvar token_data no seu DB
    # Exemplo:
    # user_id = token_data.get("user_id")
    # salva token_data em tabela de tokens

    return token_data

# ======== EXEMPLO DE USO COM ACCESS TOKEN ========
@app.get("/ml/me")
def ml_me(access_token: str):
    # faz chamada com access_token
    response = requests.get(
        "https://api.mercadolibre.com/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
