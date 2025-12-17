import uuid
from datetime import date
from http.client import HTTPException
from selectors import SelectSelector

from sqlmodel import Session, select
from backend.models import Conto
from backend.schemas import CreaConto, ContoOutput, SaldoContoOutput, UtenteAutenticato
from backend.services.utenti import chk_utente_esistente, get_user_id_from_uuid, get_id_utente


def get_conto(numero_conto: int, session: Session) -> Conto | None:
    try:
        query = select(Conto).where(Conto.numero_conto == numero_conto)
        result = session.exec(query).one_or_none()
        if result is None:
            return None
        else:
            return result

    except Exception as e:
        raise e

def check_conto_attivo(conto: Conto) -> bool:
    if conto.data_chiusura is not None:
        return False

    return True


def aggiungi_conto(conto: CreaConto, session: Session, utente_corrente: UtenteAutenticato) -> Conto:
    try:
        id_utente = get_user_id_from_uuid(conto.uuid_utente, session)
        id_utente_loggato = get_user_id_from_uuid(utente_corrente.uuid_utente, session)
        if id_utente_loggato != id_utente:
            raise ValueError("Utente non autorizzato!")

        if id_utente is None:
            raise ValueError("L'utente non esiste!")

        query = select(Conto).where(Conto.id_utente == id_utente)
        result = session.exec(query).one_or_none()
        if result is not None:
            raise ValueError("Conto già esistente!")

        conto_da_aprire = Conto(
            saldo=conto.saldo_iniziale,
            data_apertura=date.today(),
            id_utente=id_utente
        )
        session.add(conto_da_aprire)
        session.commit()
        return conto_da_aprire

    except Exception as e:
        session.rollback()
        raise e

def seleziona_conto(uuid_conto: uuid.UUID, session: Session) -> Conto | None:
    try:
        statement = select(Conto).where(Conto.uuid_conto == uuid_conto)
        result = session.exec(statement)
        conto = result.one_or_none()
        print(conto.uuid_conto)
        if conto is None:
            return None
        else:
            return conto

    except Exception as e:
        print("Errore durante la selezione del conto" + str(e))

def chiusura_conto(uuid_conto: uuid.UUID, session: Session, utente_corrente: UtenteAutenticato) -> Conto:
    try:
        conto_da_chiudere = seleziona_conto(uuid_conto, session)
        id_utente = conto_da_chiudere.id_utente

        if not id_utente == get_user_id_from_uuid(utente_corrente.uuid_utente, session):
            raise ValueError("Il conto non esiste o non può essere chiuso!")
        if conto_da_chiudere is not None:
            conto_da_chiudere.data_chiusura = date.today()
            session.commit()
        else:
            raise ValueError("Il conto non esiste!")
        return conto_da_chiudere

    except Exception as e:
        session.rollback()
        raise e

def get_numero_conto(id_utente: int, session: Session) -> int | None:
    try:
        statement = select(Conto).where(Conto.id_utente == id_utente)
        result = session.exec(statement).one_or_none()
        if result is not None:
            return result.numero_conto
        else:
            return None
    except Exception as e:
        raise e

def ottieni_saldo(session: Session, utente_corrente: UtenteAutenticato) -> SaldoContoOutput:
    try:
        id_utente = get_id_utente(utente_corrente, session)
        numero_conto = get_numero_conto(id_utente, session)
        conto = get_conto(numero_conto, session)

        if conto is not None:
            return SaldoContoOutput(
                saldo = conto.saldo
            )
        else:
            raise ValueError("Il conto non esiste!")

    except Exception as e:
        print(f"Errore: {e}")
        raise e

def get_conto_utente(session: Session, utente_corrente: UtenteAutenticato) -> ContoOutput:
    try:
        id_utente = get_id_utente(utente_corrente, session)
        query = select(Conto).where(Conto.id_utente == id_utente)
        result = session.exec(query).one_or_none()
        if result is not None:
            return ContoOutput(
                uuid_conto = result.uuid_conto,
                data_apertura = result.data_apertura,
                data_chiusura = result.data_chiusura,
                saldo = result.saldo
            )
        else:
            raise ValueError("Utente non ha un conto associato!")

    except Exception as e:
        print(f"Errore: {e}")
        raise e
