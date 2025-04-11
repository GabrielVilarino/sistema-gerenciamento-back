from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from src.models import InputVendas
from src.pool.pool import get_db
from src.pool.models import Vendas, Produtos, Usuarios
from src.models import BuscaVendas
from datetime import datetime
import pandas as pd
import io

router = APIRouter()

@router.post("/add-venda")
async def add_venda(params: InputVendas, db: AsyncSession = Depends(get_db)):
    """
    Rota para adicionar venda.
    """
    data_venda = datetime.strptime(params.data_venda, "%Y-%m-%d").date()

    try:

        for produto in params.produtos:

            query_produto = select(Produtos).filter(
                Produtos.nome == produto.nome_produto,
                Produtos.tamanho == produto.tamanho
            )
            result_produto = await db.execute(query_produto)
            estoque_produto = result_produto.scalar_one_or_none()
            
            if estoque_produto is None:
                raise HTTPException(status_code=404, detail=f"Produto {produto.nome_produto} com o tamanho: {produto.tamanho} não encontrado.")
            
            # if estoque_produto.quantidade < produto.quantidade:
            #     raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o produto {estoque_produto.nome} no tamanho: {produto.tamanho}, quantidade atual: {estoque_produto.quantidade}.")
                
            new_venda = Vendas(
                matricula=params.matricula,
                nome_cliente = params.nome_cliente,
                turma=params.turma,
                socio=params.socio,
                codigo_produto=produto.codigo_produto,
                data_venda=data_venda,
                forma_pagamento=params.forma_pagamento,
                obs=params.obs,
                valor_produto=produto.valor_produto,
                troco=params.troco,
                quantidade=produto.quantidade,
                valor_pago=params.valor_pago,
                tamanho=produto.tamanho
            )
            db.add(new_venda)

            # estoque_produto.quantidade -= produto.quantidade

            # db.add(estoque_produto)
        

        await db.commit()

        return {"detail": "Venda realizada com sucesso"}


    except HTTPException as e:
        print(f"Erro ao adicionar venda: {e}")
        raise e
    except Exception as e:
        print(f"Erro ao adicionar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro ao adicionar venda")
    

@router.post("/vendas")
async def vendas(params: BuscaVendas | None = None, db: AsyncSession = Depends(get_db)):
    """
    Rota para buscar vendas.
    """
    try:
        # Realiza a consulta
        query = select(
            Vendas,
            Produtos.nome.label("produto_nome"),
            Usuarios.nome.label("usuario_nome")
        ).join(Produtos, Vendas.codigo_produto == Produtos.codigo) \
         .join(Usuarios, Vendas.matricula == Usuarios.matricula)

        if params:
            if params.data_inicio:
                data_inicio = datetime.strptime(params.data_inicio, "%Y-%m-%d").date()
                query = query.where(Vendas.data_venda >= cast(data_inicio, Date))
            if params.data_fim:
                data_fim = datetime.strptime(params.data_fim, "%Y-%m-%d").date()
                query = query.where(Vendas.data_venda <= cast(data_fim, Date))
            if params.cpf:
                query = query.where(Vendas.cpf_cliente == params.cpf)
        
        result = await db.execute(query)
        vendas = result.fetchall()
        
        if not vendas:
            raise HTTPException(status_code=404, detail="Não há vendas cadastradas para o filtro")
        
        vendas_data = [
            {
                "id": venda[0].id,
                "matricula": venda[0].matricula,
                "usuario_nome": venda[2],
                "nome_cliente": venda[0].nome_cliente,
                "turma": venda[0].turma,
                "socio": venda[0].socio,
                "codigo_produto": venda[0].codigo_produto,
                "produto_nome": venda[1],
                "data_venda": venda[0].data_venda.strftime("%Y-%m-%d"),
                "forma_pagamento": venda[0].forma_pagamento,
                "obs": venda[0].obs,
                "valor_pago": venda[0].valor_pago,
                "valor_produto": venda[0].valor_produto,
                "troco": venda[0].troco,
                "quantidade": venda[0].quantidade,
                "tamanho": venda[0].tamanho
            }
            for venda in vendas
        ]

        return {
            "detail": "sucesso",
            "vendas": vendas_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao buscar vendas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar vendas")
    

@router.delete("/delete-venda")
async def delete_venda(id_venda: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para deletar uma venda e atualizar a quantidade do produto.
    """
    try:
        query_venda = select(Vendas).where(Vendas.id == id_venda)
        result = await db.execute(query_venda)
        venda = result.scalar_one_or_none()

        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada.")

        delete_query = delete(Vendas).where(Vendas.id == id_venda)
        await db.execute(delete_query)
        await db.commit()

        return {"detail": "Venda excluída com sucesso."}

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao deletar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar venda")


@router.post("/exportar-planilha")
async def exportar_planilha(dados: list[dict]):
    """
    Rota para gerar e baixar uma planilha a partir de uma lista de objetos JSON.
    """
    try:
        if not dados:
            raise HTTPException(status_code=400, detail="A lista de dados está vazia.")

        df = pd.DataFrame(dados)
        
        df = df.rename(columns={"usuario_nome": "vendedor", "nome_cliente": "cliente",
                                "produto_nome": "nome do produto", "data_venda": "data da venda", "forma_pagamento": "forma de pagamento",
                                "valor_pago": "valor pago", "valor_produto": "valor do produto"})
        
        df = df.drop(columns=["codigo_produto", "id"])

        df["socio"] = df["socio"].apply(lambda x: "Sim" if x else "Não")

        df = df.sort_values(by=["data da venda"], ascending=[False])

        df = df[['matricula', 'vendedor', 'cliente', 'turma', 'socio', 'nome do produto',
                 'tamanho', 'quantidade', 'data da venda', 'forma de pagamento', 'obs', 'valor pago', 'valor do produto',
                 'troco']]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dados")

        output.seek(0)
        headers = {
            "Content-Disposition": "attachment; filename=relatorio.xlsx",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }

        return Response(content=output.getvalue(), headers=headers, media_type=headers["Content-Type"])

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(f"Erro ao gerar planilha: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar a planilha")