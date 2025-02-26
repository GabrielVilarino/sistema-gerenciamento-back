from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.pool.pool import get_db
from src.pool.models import Cargos

router = APIRouter()

@router.get("/cargos")
async def cargos(db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar todos os cargos.
    """
    try:
        # Realiza a consulta
        query = select(Cargos)
        
        result = await db.execute(query)
        cargos = result.scalars().all()
        
        if not cargos:
            raise HTTPException(status_code=404, detail="Nenhum cargo encontrado.")
        
        cargos_data = [
            {
                "id": cargo.id,
                "nome": cargo.nome,
            }
            for cargo in cargos
        ]

        return {
            "detail": "sucesso",
            "cargos": cargos_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar cargos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar cargos")

