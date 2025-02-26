from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from src.models import BuscaProduto
from src.pool.pool import get_db
from src.pool.models import Produtos, Categorias
from src.google_utils.utils import upload_to_google_drive, delete_from_google_drive

router = APIRouter()

@router.post("/add-produto")
async def add_produto(
    nome: str = Form(...),
    categoria_id: str = Form(...),
    tamanho: str = Form(...),
    preco: float = Form(...),
    preco_socio: float = Form(...),
    quantidade: int = Form(...),
    imagem: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Rota para adicionar produto.
    """
    try:
        imagem_bytes = await imagem.read()

        image_url = upload_to_google_drive(imagem.filename, imagem_bytes, imagem.content_type)
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Erro ao fazer upload da imagem")
        
        new_produto = Produtos(
            nome = nome,
            tamanho = tamanho,
            preco = preco,
            preco_socio = preco_socio,
            quantidade = quantidade,
            image_url = image_url,
            categoria_id = int(categoria_id)
        )

        db.add(new_produto)
        await db.commit()

        return {"detail": "Produto adicionado com sucesso"}

    except HTTPException as e:
        print(f"Erro ao atualizar produto: {e}")
        raise e
    except Exception as e:
        print(f"Erro ao adicionar produto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao adicionar produto")
    

@router.post("/produtos")
async def produtos(params: BuscaProduto | None = None, db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar produtos.
    """
    try:
        # Realiza a consulta
        query = select(Produtos, Categorias.nome.label("categoria_nome")).join(Categorias, Produtos.categoria_id == Categorias.id)
        
        if params:
            if params.nome:
                query = query.where(Produtos.nome.ilike(f"{params.nome}%"))
            if params.categoria_id:
                query = query.where(Produtos.categoria_id == params.categoria_id)
        
        result = await db.execute(query)
        produtos = result.fetchall()
        
        if not produtos:
            raise HTTPException(status_code=404, detail="Nenhum produto encontrado.")
        
        produtos_data = [
            {
                "codigo": produto[0].codigo,
                "nome": produto[0].nome,
                "tamanho": produto[0].tamanho,
                "preco": produto[0].preco,
                "preco_socio": produto[0].preco_socio,
                "quantidade": produto[0].quantidade,
                "image_url": produto[0].image_url,
                "categoria": produto[1],
            }
            for produto in produtos
        ]

        return {
            "detail": "sucesso",
            "produtos": produtos_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos")
    

@router.get("/produto")
async def produto(codigo: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar um produto.
    """
    try:
        
        query = select(Produtos).where(Produtos.codigo == codigo)
        result = await db.execute(query)
        produto = result.fetchone()[0]
        
        produto_data = {
            "codigo": produto.codigo,
            "nome": produto.nome,
            "tamanho": produto.tamanho,
            "preco": produto.preco,
            "preco_socio": produto.preco_socio,
            "quantidade": produto.quantidade,
            "image_url": produto.image_url,
            "categoria_id": produto.categoria_id
        }

        return {
            "detail": "Produto encontrado.",
            "produto": produto_data
            }

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produto")
    

@router.put("/update-produto")
async def update_produto(
    codigo: int = Form(...),
    nome: str = Form(...),
    categoria_id: str = Form(...),
    tamanho: str = Form(...),
    preco: float = Form(...),
    preco_socio: float = Form(...),
    quantidade: int = Form(...),
    imagem_url: str = Form(...),
    imagem: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Rota para atualizar produto.
    """
    try:

        query = update(Produtos).where(Produtos.codigo == codigo).values(nome=nome,
                                                                                categoria_id=int(categoria_id),
                                                                                tamanho=tamanho,
                                                                                preco=preco,
                                                                                preco_socio=preco_socio,
                                                                                quantidade=quantidade)

        if imagem:
            
            ## Realizar Exclução e Inclusão da nova imagem
            id_imagem = imagem_url.split("=")[-1]
            
            imagem_bytes = await imagem.read()

            image_url = upload_to_google_drive(imagem.filename, imagem_bytes, imagem.content_type, id_imagem)
            
            if not image_url:
                raise HTTPException(status_code=500, detail="Erro ao fazer upload da imagem")

            query = update(Produtos).where(Produtos.codigo == codigo).values(nome=nome,
                                                                                    categoria_id=int(categoria_id),
                                                                                    tamanho=tamanho,
                                                                                    preco=preco,
                                                                                    preco_socio=preco_socio,
                                                                                    quantidade=quantidade,
                                                                                    image_url=image_url)

        
        result = await db.execute(query)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        await db.commit()

        return {"detail": "Produto atualizado com sucesso"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto")
    

@router.delete("/delete-produto")
async def delete_produto(codigo: int, imagem_url: str, db: AsyncSession = Depends(get_db)):
    """
    Rota para deletar produto.
    """
    try:

        id_imagem = imagem_url.split("=")[-1]

        response_delete = delete_from_google_drive(id_imagem)

        if not response_delete:
            raise HTTPException(status_code=400, detail="Erro ao deletar imagem do produto")
        
        delete_query = delete(Produtos).where(Produtos.codigo == codigo)

        await db.execute(delete_query)
        await db.commit()

        return {"detail": "Produto excluído com sucesso."}

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao deletar produto: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar produto")