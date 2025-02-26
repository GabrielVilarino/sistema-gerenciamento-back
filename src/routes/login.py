from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import LoginRequest
from src.pool.pool import get_db
from src.pool.models import Usuarios

router = APIRouter()

@router.post("/login")
async def login(usuario: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Rota para autenticação de usuário pelo usuário e senha.
    """
    try:
        # Realiza a consulta
        query = select(Usuarios).where(
            Usuarios.usuario == usuario.login,
            Usuarios.senha == usuario.senha
        )
        result = await db.execute(query)
        usuario = result.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário ou Senha incorretos.")
        
        usuario_data = usuario[0]

        primeiro_nome = usuario_data.nome.split(" ")[0]

        return {
            "detail": "sucesso",
            "matricula": usuario_data.matricula,
            "nome": primeiro_nome,
            "permissao": usuario_data.permissao
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar o usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar o usuário")

