import requests

def buscar_produtos_ml(query: str, limit: int):
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "q": query,
        "limit": limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    produtos = []

    for item in data.get("results", []):
        produtos.append({
            "ml_item_id": item.get("id"),
            "titulo": item.get("title"),
            "preco": item.get("price"),
            "thumbnail": item.get("thumbnail"),
            "status": item.get("status")
        })

    return produtos
