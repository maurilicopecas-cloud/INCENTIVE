from database import engine
from models import ml_token, ml_user, ml_item
from database import Base

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from database import engine, SessionLocal
from models import Base, MercadoLivreToken
from ml import get_app_token

# ======================================================
# APP
# ======================================================

app = FastAPI(title="Incentive API")

# ======================================================
# BANCO – cria tabelas automaticamente no deploy
# ======================================================

Base.metadata.create_all(bind=engine)

# ======================================================
# DEPENDÊNCIA DE SESSÃO DO BANCO
# ======================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# TESTE MERCADO LIVRE (SITE)
# ======================================================

@app.get("/ml/sites")
def get_sites(db: Session = Depends(get_db)):
    """
    Endpoint de teste para validar:
    - token
    - autenticação
    - conexão com ML
    """

    token = get_app_token(db)

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

    return response.json()
