# models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, BigInteger, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum as PyEnum


Base = declarative_base()


class Usuarios(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "public"}

    matricula = Column(BigInteger, primary_key=True)
    nome = Column(String(255), nullable=False)
    usuario = Column(String(50), nullable=False)
    senha = Column(String(30), nullable=False)
    turma = Column(String(50), nullable=False)
    permissao = Column(String(20), nullable=False)

    cargo_id = Column(Integer, ForeignKey("public.cargos.id"), nullable=False)

    cargo = relationship("Cargos", back_populates="usuarios")
    vendas = relationship("Vendas", back_populates="usuario")

class Cargos(Base):
    __tablename__ = "cargos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)

    usuarios = relationship("Usuarios", back_populates="cargo")

class Produtos(Base):
    __tablename__ = "produtos"
    __table_args__ = {"schema": "public"}

    codigo = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    tamanho = Column(String(3), nullable=False)
    preco = Column(Float, nullable=False)
    preco_socio = Column(Float, nullable=False)
    disponivel = Column(Boolean, nullable=False)
    image_url = Column(String(255), nullable=False)

    categoria_id = Column(Integer, ForeignKey("public.categorias.id"), nullable=False)

    categoria = relationship("Categorias", back_populates="produtos")
    vendas = relationship("Vendas", back_populates="produto")


class Categorias(Base):
    __tablename__ = "categorias"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)

    produtos = relationship("Produtos", back_populates="categoria")


class Vendas(Base):
    __tablename__ = "vendas"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    matricula = Column(BigInteger, ForeignKey("public.usuarios.matricula"), nullable=False)
    nome_cliente = Column(String(255), nullable=False)
    cpf_cliente = Column(String(13), nullable=False)
    turma = Column(String(10), nullable=True)
    socio = Column(Boolean, nullable=False)
    codigo_produto = Column(Integer, ForeignKey("public.produtos.codigo"), nullable=False)
    data_venda = Column(Date, nullable=False)
    forma_pagamento = Column(String(15), nullable=False)
    obs = Column(String(255), nullable=True)
    valor_pago = Column(Float(10,2), nullable=False)
    valor_produto = Column(Float(10,2), nullable=False)
    troco = Column(Float(10,2), nullable=True)
    quantidade = Column(Integer, nullable=False)
    tamanho = Column(String, nullable=False)

    produto = relationship("Produtos", back_populates="vendas")
    usuario = relationship("Usuarios", back_populates="vendas")
