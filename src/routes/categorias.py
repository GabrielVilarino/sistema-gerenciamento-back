from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.pool.pool import get_db
from src.pool.models import Categorias

router = APIRouter()

@router.get("/categorias")
async def categorias(db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar todos os categorias.
    """
    try:
        # Realiza a consulta
        query = select(Categorias)
        
        result = await db.execute(query)
        categorias = result.scalars().all()
        
        if not categorias:
            raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada.")
        
        categorias_data = [
            {
                "id": cargo.id,
                "nome": cargo.nome,
            }
            for cargo in categorias
        ]

        return {
            "detail": "sucesso",
            "categorias": categorias_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar categorias")