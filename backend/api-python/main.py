from fastapi import FastAPI, HTTPException
import requests

from ml import get_app_token

app = FastAPI(title="Incentive API")

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# TESTE REAL API MERCADO LIVRE
# ======================================================

@app.get("/ml/test/site")
def test_ml_site():
    """
    Testa:
    - geração de token
    - autenticação
    - chamada real à API do Mercado Livre
    """

    try:
        token = get_app_token()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar token ML: {str(e)}"
        )

    response = requests.get(
        "https://api.mercadolibre.com/sites/MLB",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return {
        "message": "API Mercado Livre OK",
        "data": response.json()
    }
