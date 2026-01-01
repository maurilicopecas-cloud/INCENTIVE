from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Incentive API")

# ======================================================
# CONFIG
# ======================================================

ML_SELLER_TOKEN = "APP_USR-1585555766651492-010111-a531bce693f41e10d3a418a3dba04f19-185186788"

HEADERS = {
    "Authorization": f"Bearer {ML_SELLER_TOKEN}"
}

# ======================================================
# HEALTH
# ======================================================

@app.get("/")
def health():
    return {"status": "ok"}

# ======================================================
# BUSCAR ITENS DO SELLER
# ======================================================

@app.get("/ml/seller/{seller_id}")
def get_seller_items(seller_id: int):

    search_response = requests.get(
        "https://api.mercadolibre.com/sites/MLB/search",
        params={
            "seller_id": seller_id,
            "limit": 50
        },
        headers=HEADERS,
        timeout=15
    )

    if search_response.status_code != 200:
        raise HTTPException(
            status_code=search_response.status_code,
            detail=search_response.text
        )

    search_data = search_response.json()
    items = []

    for item in search_data.get("results", []):
        item_id = item.get("id")

        item_response = requests.get(
            f"https://api.mercadolibre.com/items/{item_id}",
            headers=HEADERS,
            timeout=15
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
