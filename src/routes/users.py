from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from src.models import BuscaUsuario, InputUsuario, UpdateUsuario
from src.pool.pool import get_db
from src.pool.models import Usuarios, Cargos

router = APIRouter()

@router.get("/user")
async def user(matricula: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar um usuário.
    """
    try:
        
        query = select(Usuarios).where(Usuarios.matricula == matricula)
        result = await db.execute(query)
        usuario = result.fetchone()[0]
        
        usuario_data = {
            "matricula": usuario.matricula,
            "nome": usuario.nome,
            "usuario": usuario.usuario,
            "senha": usuario.senha,
            "turma": usuario.turma,
            "permissao": usuario.permissao,
            "cargo_id": usuario.cargo_id
        }

        return {
            "detail": "Usuário encontrado.",
            "usuario": usuario_data
            }

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar usuário")

@router.post("/users")
async def usuarios(params: BuscaUsuario | None = None, db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar usuários.
    """
    try:
        # Realiza a consulta
        query = select(Usuarios, Cargos.nome.label("cargo_nome")).join(Cargos, Usuarios.cargo_id == Cargos.id)
        
        if params:
            if params.nome:
                query = query.where(Usuarios.nome.ilike(f"{params.nome}%"))
            if params.cargo_id:
                query = query.where(Usuarios.cargo_id == params.cargo_id)
        
        result = await db.execute(query)
        usuarios = result.fetchall()
        
        if not usuarios:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado.")
        
        usuarios_data = [
            {
                "matricula": usuario[0].matricula,
                "nome": usuario[0].nome,
                "usuario": usuario[0].usuario,
                "turma": usuario[0].turma,
                "permissao": usuario[0].permissao,
                "cargo": usuario[1],
            }
            for usuario in usuarios
        ]

        return {
            "detail": "sucesso",
            "usuarios": usuarios_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar o usuários")


@router.post("/add-user")
async def add_user(params: InputUsuario, db: AsyncSession = Depends(get_db)):
    """
    Rota para adicionar usuário.
    """
    try:
        
        new_user = Usuarios(
            matricula=params.matricula,
            nome=params.nome,
            usuario=params.usuario,
            senha=params.senha,
            turma=params.turma,
            permissao=params.permissao,
            cargo_id=params.cargo_id
        )

        db.add(new_user)
        await db.commit()

        return {"detail": "Usuário adicionado com sucesso"}

    except HTTPException as e:
        print(f"Erro ao atualizar usuário: {e}")
        raise e
    except Exception as e:
        print(f"Erro ao adicionar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao adicionar usuário")
    

@router.put("/update-user")
async def update_user(params: UpdateUsuario, db: AsyncSession = Depends(get_db)):
    """
    Rota para atualizar usuário.
    """
    try:
        query = update(Usuarios).where(Usuarios.matricula == params.matricula).values(nome=params.nome,
                                                                                      usuario=params.usuario,
                                                                                      senha=params.senha,
                                                                                      turma=params.turma,
                                                                                      permissao=params.permissao,
                                                                                      cargo_id=params.cargo_id)

        
        result = await db.execute(query)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        await db.commit()

        return {"detail": "Usuário atualizado com sucesso"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar usuário")
    

@router.delete("/delete-user")
async def delete_user(matricula: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para deletar usuário.
    """
    try:
        
        delete_query = delete(Usuarios).where(Usuarios.matricula == matricula)
        await db.execute(delete_query)
        await db.commit()

        return {"detail": "Usuário excluído com sucesso."}

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar usuário")