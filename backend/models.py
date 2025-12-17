from typing import Optional
import uuid

from sqlalchemy import CheckConstraint, Column, String
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from datetime import date
from decimal import Decimal

class Utente(SQLModel, table=True):
    id_utente: int | None = Field(default=None, primary_key=True)
    uuid_utente: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True
    )
    mail: EmailStr = Field(unique=True)
    password: str
    tipo: str = Field(index=True)  # 'privato' o 'azienda'
    nome: str | None = Field(default=None)
    cognome: str | None = Field(default=None)
    partita_iva: str | None = Field(default=None)
    ragione_sociale: str | None = Field(default=None)
    disabled: bool = Field(default=False)

    conto: Optional["Conto"] = Relationship(back_populates="utente")


class Conto(SQLModel, table=True):
    numero_conto: int | None = Field(default=None, primary_key=True)
    uuid_conto: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True
    )
    data_apertura: date
    data_chiusura: date | None = Field(default=None)
    saldo: Decimal = Field(
        default=Decimal('0.00'),
        decimal_places=2)
    id_utente: int = Field(foreign_key="utente.id_utente", unique=True)

    utente: Utente = Relationship(back_populates="conto")
    movimenti: list["Movimento"] = Relationship(back_populates="conto")  # lista movimenti di un conto


class Transazione(SQLModel, table=True):
    id_transazione: int | None = Field(default=None, primary_key=True)
    uuid_transazione: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True
    )
    data: date
    importo: Decimal = Field(default=0, decimal_places=2)

    data_esecuzione: date | None = Field(default=None)

    movimenti: list["Movimento"] = Relationship(back_populates="transazione", cascade_delete=True)


class Segno(str, Enum):
    POSITIVO = "+"
    NEGATIVO = "-"


class Causale(SQLModel, table=True):
    id_causale: int | None = Field(default=None, primary_key=True)
    descrizione: str

    movimenti: list["Movimento"] = Relationship(back_populates="causale")


class Movimento(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("segno IN ('+', '-')", name="check_segno"),
    )
    uuid_movimento: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True
    )
    id_movimento: int | None = Field(default=None, primary_key=True)
    id_transazione: int | None = Field(foreign_key="transazione.id_transazione", ondelete="CASCADE")
    numero_conto: int = Field(foreign_key="conto.numero_conto")
    codice_causale: int = Field(foreign_key="causale.id_causale")
    segno: Segno = Field(sa_column=Column(String(1), nullable=False))
    descrizione: str | None = Field(default=None)

    conto: Conto = Relationship(back_populates="movimenti")  # istanza conto relativa a un movimento
    transazione: Transazione = Relationship(back_populates="movimenti")
    causale: Causale = Relationship(back_populates="movimenti")