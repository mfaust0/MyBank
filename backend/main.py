from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from sqlalchemy import CheckConstraint, Column, String, literal
from enum import Enum
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Field, SQLModel, create_engine, select, Session, Relationship, func, case
from sqlalchemy.engine.result import ScalarResult

'''class Utente(SQLModel, table=True):
    id_utente: int | None = Field(default=None, primary_key=True)
    mail: EmailStr = Field(default=None, nullable=False)
    password: str = Field(default=None, nullable=False)'''

class Conto(SQLModel, table=True):
    numero_conto: int | None = Field(default=None, primary_key=True)
    intestatario: str
    data_apertura: date
    data_chiusura: date | None = Field(default=None)
    saldo_iniziale: Decimal = Field(default=0, decimal_places=2)

    movimenti: list["Movimento"] = Relationship(back_populates="conto") #lista movimenti di un conto

class Transazione(SQLModel, table=True):
    id_transazione: int | None = Field(default=None, primary_key=True)
    data: date
    importo: Decimal = Field(default=0, decimal_places=2)

    movimenti : list["Movimento"] = Relationship(back_populates="transazione")

class Segno(str, Enum):
    POSITIVO="+"
    NEGATIVO="-"

class Causale(SQLModel, table=True):
    id_causale: int | None = Field(default=None, primary_key=True)
    descrizione: str

    movimenti : list["Movimento"] = Relationship(back_populates="causale")

class Movimento(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("segno IN ('+', '-')", name="check_segno"),
    )

    id_movimento: int | None = Field(default=None, primary_key=True)
    id_transazione: int | None = Field(foreign_key="transazione.id_transazione")
    numero_conto: int = Field(foreign_key="conto.numero_conto")
    codice_causale: int = Field(foreign_key="causale.id_causale")
    segno: Segno = Field(sa_column=Column(String(1), nullable=False))
    descrizione: str | None = Field(default=None)

    conto : Conto = Relationship(back_populates="movimenti") #istanza conto relativa a un movimento
    transazione : Transazione = Relationship(back_populates="movimenti")
    causale: Causale = Relationship(back_populates="movimenti")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_if_not_exists():
    db_file = Path(sqlite_file_name)
    if not db_file.is_file():
        print("Database non trovato. Creazione di un nuovo database e delle tabelle...")
        SQLModel.metadata.create_all(engine)
    else:
        print("Database esistente. Nessuna azione di creazione delle tabelle.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_if_not_exists()
    popola_causali()
    yield # Qui l'applicazione gestisce le richieste
    print("Chiusura dell'applicazione...")

def popola_causali():
    bonifico_in_ingresso = Causale(descrizione="BONIFICO IN INGRESSO")
    bonifico_in_uscita = Causale(descrizione="BONIFICO IN USCITA")
    pagamento = Causale(descrizione="PAGAMENTO_BANCOMAT")
    incasso = Causale(descrizione="INCASSO GENERICO")
    interessi = Causale(descrizione="ACCREDITO INTERESSI")
    commissioni = Causale(descrizione="COMMISSIONI")

    with Session(engine) as session:
        check_exist = session.exec(select(Causale).limit(1)).first()
        if check_exist is None:
            session.add(bonifico_in_ingresso)
            session.add(bonifico_in_uscita)
            session.add(pagamento)
            session.add(incasso)
            session.add(interessi)
            session.add(commissioni)
            session.commit()

def seleziona_conto(numero_conto: int):
    with Session(engine) as session:
        statement = select(Conto).where(Conto.numero_conto == numero_conto)
        result = session.exec(statement)
        conto = result.one()
        return conto

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/apri_conto/")
async def apri_conto(saldo_iniziale: Decimal, intestatario: str):
    if saldo_iniziale < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il saldo iniziale deve essere >= 0"
        )
    if intestatario == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il nome dell'intestatario non può essere nullo"
        )
    with Session(engine) as session:
        try:
            query_controllo_intestatario = select(Conto).where(Conto.intestatario == intestatario)
            intestatario_esistente = session.exec(query_controllo_intestatario).first()

            if intestatario_esistente is not None:
                return {"message": "Impossibile aprire il conto perché esiste già altro conto con stesso intestatario"}

            conto_da_aprire = Conto(
                saldo_iniziale=saldo_iniziale,
                data_apertura=date.today(),
                intestatario=intestatario
            )
            session.add(conto_da_aprire)
            session.commit()
            session.refresh(conto_da_aprire)

            return {"message": "Il conto è stato aperto con successo!",
                    "numero conto:": conto_da_aprire.numero_conto}

        except SQLAlchemyError as sae:
            session.rollback()
            raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nell'inserimento dei dati nel database"
            )

@app.post("/chiudi_conto/{numero_conto: int}")
async def chiudi_conto(numero_conto: int):
    with Session(engine) as session:
        try:
            conto_da_chiudere = seleziona_conto(numero_conto)
            if conto_da_chiudere is not None:
                conto_da_chiudere.data_chiusura = date.today()
                session.add(conto_da_chiudere)
                session.commit()
                session.refresh(conto_da_chiudere)
                return {"message": "Il conto è stato chiuso con successo!",
                        "numero conto:": conto_da_chiudere.numero_conto,
                        "data_chiusura:": conto_da_chiudere.data_chiusura}
            else:
                return {"message": "il conto indicato non è stato trovato"}

        except SQLAlchemyError as sae:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nell'aggiornamento del database"
            )

@app.get("/trova_conto/{numero_conto}")
async def trova_conto(numero_conto: int):
    try:
        return seleziona_conto(numero_conto)
    except SQLAlchemyError as sae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Errore nella richiesta al database"
        )

@app.get("/conti_aperti/")
async def conti_aperti():
    with Session(engine) as session:
        try:
            statement = select(Conto).where(Conto.data_chiusura == None)
            result = session.exec(statement).all()
            return result
        except SQLAlchemyError as sae:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nella richiesta della lista dei conti aperti"
            )

@app.get("/lista_conti/")
async def lista_conti():
    with Session(engine) as session:
        try:
            statement = select(Conto)
            result = session.exec(statement).all()
            return result
        except SQLAlchemyError as sae:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nella richiesta della lista dei conti"
            )

'''Controlla se il conto è attivo o se è stato chiuso.
    Restituisce true se è attivo oppure false se è stato chiuso'''
def check_conto_attivo(numero_conto: int, session: Session):
        try:
            statement = select(Conto).where(Conto.numero_conto == numero_conto)
            result = session.exec(statement)
            conto = result.one()

            if conto.data_chiusura is not None:
                return False
            else:
                return True

        except SQLAlchemyError as sae:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nella selezione del conto"
            )

@app.post("/nuovo_bonifico/{conto_debitore}")
async def nuovo_bonifico(conto_debitore: int, conto_beneficiario: int, importo: Decimal, data: date, descrizione: str):
    with Session(engine) as session:
        check_attivo_debitore = check_conto_attivo(conto_debitore, session)
        check_attivo_beneficiario = check_conto_attivo(conto_beneficiario, session)

        if not check_attivo_debitore:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il tuo conto è chiuso! Non puoi effettuare bonifici!"
            )

        if not check_attivo_beneficiario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conto non abilitato!"
            )
        try:
            dati_bonifico = Transazione(
                data=data,
                importo=importo,
            )

            dati_movimento_uscita = Movimento(
                numero_conto = conto_debitore,
                transazione = dati_bonifico,
                codice_causale = 2,
                segno = Segno.NEGATIVO,
                descrizione = descrizione
            )
            dati_movimento_entrata = Movimento(
                numero_conto = conto_beneficiario,
                transazione = dati_bonifico,
                codice_causale = 1,
                segno = Segno.POSITIVO,
                descrizione = descrizione
            )

            session.add(dati_movimento_uscita)
            session.add(dati_movimento_entrata)
            session.commit()

            return {"message": "Bonifico inviato!"}

        except SQLAlchemyError as sae:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nell'invio del bonifico. Riprova!"
            )

@app.post("/nuovo_pagamento/{conto_debitore}")
async def nuovo_pagamento(conto_debitore: int, conto_beneficiario: int, importo: Decimal, descrizione: str):
    with Session(engine) as session:
        check_attivo_debitore = check_conto_attivo(conto_debitore, session)
        check_attivo_beneficiario = check_conto_attivo(conto_beneficiario, session)
        if not check_attivo_debitore:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il tuo conto è chiuso, non puoi effettuare pagamenti!"
            )

        if not check_attivo_beneficiario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conto non abilitato!"
            )

        try:
            dati_pagamento = Transazione(
                data=date.today(), #la data è fissata
                importo=importo,
            )

            dati_movimento_uscita = Movimento(
                numero_conto = conto_debitore,
                transazione = dati_pagamento,
                codice_causale = 3,
                segno = Segno.NEGATIVO,
                descrizione = descrizione
            )

            dati_movimento_entrata = Movimento(
                numero_conto = conto_beneficiario,
                transazione = dati_pagamento,
                codice_causale = 4,
                segno = Segno.POSITIVO,
                descrizione = descrizione
            )

            session.add(dati_movimento_uscita)
            session.add(dati_movimento_entrata)
            session.commit()

            return {"message": "Pagamento inviato!"}

        except SQLAlchemyError as sae:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nel pagamento. Riprova!"
            )

@app.get("/ottieni_saldo/{numero_conto}")
async def ottieni_saldo(numero_conto: int):
    with Session(engine) as session:
        try:
            conto = session.exec(select(Conto).where(Conto.numero_conto == numero_conto)).first()

            if conto is None:
                raise HTTPException(status_code=404, detail="Conto non trovato")

            saldo_iniziale = conto.saldo_iniziale

            statement_movimenti = (
                select(
                    func.coalesce(
                        func.sum(
                            case(
                                (Movimento.segno == literal("+"), Transazione.importo),  # type: ignore
                                (Movimento.segno == literal("-"), -Transazione.importo),  # type: ignore
                            )
                        ),
                        0
                    )
                )
                .select_from(Movimento)
                .join(Transazione, Movimento.id_transazione == Transazione.id_transazione)
                .where(Movimento.numero_conto == numero_conto)
            )

            result_movimenti = session.exec(statement_movimenti).one_or_none()
            saldo_movimenti = Decimal(result_movimenti)
            saldo_finale = saldo_iniziale + saldo_movimenti

            return {"saldo": float(saldo_finale)}

        except SQLAlchemyError as sae:
            print(f"️ ERRORE SQL SPECIFICO: {sae}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nel calcolo del saldo. Riprova!"
            )

@app.get("/lista_movimenti/{numero_conto}")
async def lista_movimenti(numero_conto: int):
    with Session(engine) as session:
        try:
            conto = session.exec(select(Conto).where(Conto.numero_conto == numero_conto)).first()

            if conto is None:
                raise HTTPException(status_code=404, detail="Conto non trovato")

            statement_lista_movimenti = select(Movimento,Transazione).where(Movimento.numero_conto == numero_conto)
            result = session.exec(statement_lista_movimenti).all()

            lista_movimenti_serializzata = []
            for movimento, transazione in result:
                record_combinato = {
                    "numero_conto": movimento.numero_conto,
                    "importo": str(movimento.segno) + str(transazione.importo),
                    "transazione_info": {
                        "descrizione": movimento.descrizione,
                        "data":transazione.data
                    }
                }
                lista_movimenti_serializzata.append(record_combinato)
            return lista_movimenti_serializzata
        except SQLAlchemyError as sae:
            print(f"️ ERRORE SQL SPECIFICO: {sae}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nel calcolo del saldo. Riprova!"
            )
        except Exception as e:
            # Aggiungi questo blocco per debuggare l'errore 500 esatto
            print(f"️ ERRORE GENERICO DI SERIALIZZAZIONE: {e}")
            raise HTTPException(status_code=500, detail=f"Errore interno del server: {e}")


@app.get("/annulla_bonifico/{id_transazione}")
async def annulla_bonifico(id_transazione: int):
    with Session(engine) as session:
        try:
            transazione = session.exec(select(Transazione).where(Transazione.id_transazione == id_transazione)).first()

            if transazione is None:
                raise HTTPException(status_code=404, detail="La transazione non esiste!")

            countBonifico = session.exec(
                select(func.count(Movimento.id_movimento)).where(Movimento.id_transazione == id_transazione,
                                                                 Movimento.codice_causale == 2)).one()
            if countBonifico == 0:
                raise HTTPException(status_code=404, detail="La transazione selezionata non è annullabile!")

            if transazione.data_esecuzione < date.today():
                raise HTTPException(status_code=404,
                                    detail="La transazione è già stata eseguita e non è annullabile dall'utente!")
            else:
                session.delete(transazione)
                session.commit()
                return {
                    "La disposizione di bonifico: " + transazione.id_transazione + " è stata annullata con successo!"}

        except SQLAlchemyError as sae:
            print(f"️ ERRORE SQL SPECIFICO: {sae}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nell'annullamento della transazione. Riprova!"
            )