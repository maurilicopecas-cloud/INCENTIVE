from fastapi import FastAPI, Query
import requests

app = FastAPI()


# Rota básica só para saber se a API está rodando
@app.get("/")
def home():
    return {"status": "API INCENTIVE rodando"}


# Rota de teste simples (sem token, pública)
@app.get("/teste-ml")
def teste_ml():
    url = "https://api.mercadolibre.com/sites/MLB"
    response = requests.get(url, timeout=10)
    return response.json()


# Rota de busca de produtos (SEM token por enquanto)
@app.get("/produtos/mercadolivre")
def produtos_mercadolivre(q: str = Query(...), limit: int = 5):

    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "q": q,
        "limit": limit
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    produtos = []

    for item in data.get("results", []):
        produtos.append({
            "ml_item_id": item.get("id"),
            "titulo": item.get("title"),
            "preco": item.get("price"),
            "status": item.get("status"),
            "thumbnail": item.get("thumbnail")
        })

    return {
        "fonte": "Mercado Livre",
        "total": limit,
        "produtos": produtos
    }
