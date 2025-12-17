from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal
from sqlmodel import Field, SQLModel
import uuid

class CreaConto(BaseModel):
    saldo_iniziale: Decimal = Field(
        default=Decimal('0.00'),
        decimal_places=2,
        ge=0,
        description="Saldo iniziale deve essere >= 0")
        #schema_extra={"example": '100.01'})
    uuid_utente: uuid.UUID = Field(
        description="Codice del cliente a cui il conto andrà collegato")
        #schema_extra={"example": 1})

class ChiusuraContoRequest(BaseModel):
    uuid_conto: uuid.UUID

class ContoOutput(SQLModel):
    uuid_conto: uuid.UUID
    data_apertura: date
    data_chiusura: date | None
    saldo: Decimal

class ContoInput(ContoOutput):
    numero_conto: int

class CreaUtentePrivato(BaseModel):
    nome: str = Field(
        description="Nome del cliente",
        schema_extra={"example": "Mario"}
    )
    cognome: str = Field(
        description="Cognome del cliente",
        schema_extra={"example": "Rossi"}
    )
    mail: EmailStr
    password: str
    tipo: str = Field(default="privato")

    class Config:
        from_attributes = True

class CreaUtenteAzienda(BaseModel):
    partita_iva: str
    ragione_sociale: str
    mail: EmailStr
    password: str
    tipo: str = Field(default="azienda")

    class Config:
        from_attributes = True

class UtentePrivatoOutput(SQLModel):
    uuid_utente: uuid.UUID
    nome: str
    cognome: str
    mail: EmailStr


class UtenteAziendaOutput(SQLModel):
    uuid_utente: uuid.UUID
    ragione_sociale: str
    partita_iva: str
    mail: EmailStr


class UtenteAutenticato(SQLModel): #per autenticazione
    uuid_utente: uuid.UUID
    nome: str | None
    cognome: str | None
    ragione_sociale: str | None
    partita_iva: str | None
    mail: EmailStr
    disabled: bool | None

#da rimettere sul valore di ritorno della funzione seleziona_utente_da_mail in caso di problemi (l'ho tolto perché non mi piaceva)
class UtenteInput(UtenteAutenticato):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class NuovoBonificoInput(SQLModel):
    beneficiario: EmailStr
    data_esecuzione: date
    importo: Decimal
    descrizione: str

class NuovoPagamentoInput(SQLModel):
    beneficiario: EmailStr
    importo: Decimal
    descrizione: str

class NuovoPagamentoOutput(NuovoPagamentoInput):
    uuid_transazione: uuid.UUID

class NuovoBonificoOutput(NuovoBonificoInput):
    uuid_transazione: uuid.UUID

class NuovoDepositoInput(SQLModel):
    importo: Decimal
    descrizione: str

class NuovoDepositoOutput(NuovoDepositoInput):
    uuid_transazione: uuid.UUID

class SaldoContoOutput(SQLModel):
    saldo: Decimal = Field(ge=0)

class CausaleResponse(BaseModel):
    descrizione: str

class TransazioneResponse(BaseModel):
    uuid_transazione: uuid.UUID
    data: date
    importo: Decimal
    data_esecuzione: date | None

class MovimentoResponse(BaseModel):
    uuid_movimento: uuid.UUID
    numero_conto: int
    segno: str
    descrizione: str | None

    causale: CausaleResponse

    transazione: TransazioneResponse

class MovimentoDettaglioResponse(SQLModel):
    uuid_transazione: uuid.UUID
    data_transazione: date
    importo_transazione: Decimal
    descrizione_movimento: str | None
    segno: str
    controparte: str | None
    nome_causale: str