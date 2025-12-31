from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from database import engine, SessionLocal, Base
from models.ml_token import MLToken
from ml import get_app_token

# ======================================================
# APP
# ======================================================

app = FastAPI(title="Incentive API")

# ======================================================
# BANCO – cria tabelas automaticamente
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
# HEADERS PADRÃO
# ======================================================

HEADERS_PUBLIC = {
    "User-Agent": "IncentiveApp/1.0 (contact: dev@incentive.com)",
    "Accept": "application/json"
}

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# TESTE MERCADO LIVRE – SITE (USA TOKEN)
# ======================================================

@app.get("/ml/sites")
def get_sites(db: Session = Depends(get_db)):
    token = get_app_token()

    response = requests.get(
        "https://api.mercadolibre.com/sites/MLB",
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": HEADERS_PUBLIC["User-Agent"],
            "Accept": "application/json"
        },
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()

# ======================================================
# SELLER → TÍTULO, PREÇO E TODAS AS IMAGENS
# ENDPOINT OFICIAL DO MERCADO LIVRE (EXIGE TOKEN)
# ======================================================

@app.get("/ml/seller/{seller_id}")
def get_seller_items(seller_id: int):

    token = get_app_token()

    # 1️⃣ Busca anúncios do seller (ENDPOINT CORRETO)
    search_response = requests.get(
        f"https://api.mercadolibre.com/users/{seller_id}/items/search",
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": HEADERS_PUBLIC["User-Agent"],
            "Accept": "application/json"
        },
        timeout=10
    )

    if search_response.status_code != 200:
        raise HTTPException(
            status_code=search_response.status_code,
            detail=search_response.text
        )

    search_data = search_response.json()
    items = []

    # Esse endpoint retorna apenas IDs
    for item_id in search_data.get("results", []):

        item_response = requests.get(
            f"https://api.mercadolibre.com/items/{item_id}",
            headers=HEADERS_PUBLIC,
            timeout=10
        )

        if item_response.status_code != 200:
            continue

        item_data = item_response.json()

        images = [
            pic.get("secure_url")
            for pic in item_data.get("pictures", [])
        ]

        items.append({
            "item_id": item_id,
            "title": item_data.get("title"),
            "price": item_data.get("price"),
            "images": images
        })

    return {
        "seller_id": seller_id,
        "total_items": len(items),
        "items": items
    }
