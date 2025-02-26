from pydantic import BaseModel
from typing import Optional, List

class LoginRequest(BaseModel):
    login: str
    senha: str

###########   USER  ##############
class BuscaUsuario(BaseModel):
    nome: Optional[str] = None
    cargo_id: Optional[int] = None

class InputUsuario(BaseModel):
    matricula: int
    nome: str
    usuario: str
    senha: str
    turma: str
    permissao: str
    cargo_id: int

class UpdateUsuario(BaseModel):
    matricula: int
    nome: str
    usuario: str
    senha: str
    turma: str
    permissao: str
    cargo_id: int


###########  PRODUTO  ############

class BuscaProduto(BaseModel):
    nome: Optional[str] = None
    categoria_id: Optional[int] = None

class InputProduto(BaseModel):
    nome: str
    categoria: str
    tamanho: str
    preco: float
    preco_socio: str
    quantidade: int
    image_url: bytes

class UpdateProduto(BaseModel):
    codigo: int
    nome: str
    categoria: str
    tamanho: str
    preco: float
    preco_socio: str
    quantidade: int
    image_url: str
    image: Optional[bytes] = None


################ Vendas #####################

class BuscaVendas(BaseModel):
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    cpf: Optional[str] = None

class ProdutoVenda(BaseModel):
    codigo_produto: int
    quantidade: int
    valor_produto: float
    tamanho: str
    nome_produto: str

class InputVendas(BaseModel):
    matricula: int
    nome_cliente: str
    cpf_cliente: str
    turma: Optional[str] = None
    socio: bool
    data_venda: str
    forma_pagamento: str
    obs: Optional[str]
    valor_pago: float
    produtos: List[ProdutoVenda]
    troco: float
