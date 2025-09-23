from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from src.routes import login, users, cargos, produtos, categorias, vendas


app = FastAPI()

app.include_router(login.router)
app.include_router(users.router)
app.include_router(cargos.router)
app.include_router(produtos.router)
app.include_router(categorias.router)
app.include_router(vendas.router)

@app.get("/")
async def hpa():
    return 200
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)