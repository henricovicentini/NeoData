from flask_login import UserMixin
from .db import db
from datetime import datetime


class User(UserMixin, db.Model):
    """Tabela de usuários para autenticação."""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documentos = db.relationship(
        "Documentos",
        back_populates="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Documentos(db.Model):
    """Metadados dos arquivos enviados pelo usuário."""
    __tablename__ = "documentos"

    id = db.Column(db.Integer, primary_key=True)
    nome_documento = db.Column(db.String(200), nullable=False)
    caminho = db.Column(db.String(500), nullable=True)  # caminho físico do arquivo
    tamanho_kb = db.Column(db.Float, nullable=True)     # tamanho em KB
    linhas = db.Column(db.Integer, nullable=True)       # quantidade de linhas
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="documentos")

    raw_records = db.relationship(
        "RawRecord",
        back_populates="documento",
        lazy=True,
        cascade="all, delete-orphan"
    )
    clean_records = db.relationship(
        "CleanRecord",
        back_populates="documento",
        lazy=True,
        cascade="all, delete-orphan"
    )


class RawRecord(db.Model):
    """Tabela para armazenar dados brutos (pré-limpeza)."""
    __tablename__ = "raw_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_id = db.Column(db.Integer, db.ForeignKey("documentos.id"), nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documento = db.relationship("Documentos", back_populates="raw_records")


class CleanRecord(db.Model):
    """Tabela para armazenar dados limpos (pós-limpeza)."""
    __tablename__ = "clean_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_id = db.Column(db.Integer, db.ForeignKey("documentos.id"), nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documento = db.relationship("Documentos", back_populates="clean_records")
