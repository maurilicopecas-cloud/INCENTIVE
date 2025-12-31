from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(
    title="Incentive API",
    description="Consulta pública de produtos por seller no Mercado Livre",
    version="1.0.0"
)

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# PRODUTOS POR SELLER (SEM AUTH)
# ======================================================

@app.get("/ml/seller/{seller_id}")
def get_seller_items(seller_id: int):
    response = requests.get(
        "https://api.mercadolibre.com/sites/MLB/search",
        params={
            "seller_id": seller_id,
            "limit": 50
        },
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    data = response.json()

    items = []
    for item in data.get("results", []):
        items.append({
            "item_id": item.get("id"),
            "title": item.get("title"),
            "price": item.get("price"),
            "thumbnail": item.get("thumbnail"),
            "permalink": item.get("permalink"),
            "condition": item.get("condition"),
            "available_quantity": item.get("available_quantity")
        })

    return {
        "seller_id": seller_id,
        "total_items": len(items),
        "items": items
    }
