import uuid

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.models import Utente
from backend.schemas import CreaUtentePrivato, CreaUtenteAzienda, UtenteInput, UtenteAutenticato


def chk_utente_esistente(uuid_utente: uuid.UUID, session: Session) -> bool:
    try:
        query = select(Utente).where(Utente.uuid_utente == uuid_utente)
        utente = session.exec(query).one_or_none()

        if utente is not None:
            return True

        return False

    except Exception as e:
        session.rollback()
        raise e

def chk_mail_esistente(email: str, session: Session) -> bool:
    try:
        query = select(Utente).where(Utente.mail == email)
        mail = session.exec(query).one_or_none()

        if mail is not None:
            return True
        else:
            return False
    except Exception as e:
        raise e

def crea_utente_privato(utente: CreaUtentePrivato, session: Session) -> Utente:
    from backend.security_utils import get_password_hash

    if chk_mail_esistente(utente.mail, session):
        raise ValueError("Mail già esistente!")

    try:
        nuovo_utente = Utente(
            mail = utente.mail,
            password = get_password_hash(utente.password),
            nome = utente.nome,
            cognome = utente.cognome,
            tipo = "privato",
            partita_iva = None,
            ragione_sociale = None
        )
        session.add(nuovo_utente)
        session.commit()

        return nuovo_utente

    except Exception as e:
        session.rollback()
        raise e

def crea_utente_azienda(utente: CreaUtenteAzienda, session: Session) -> Utente:
    from backend.security_utils import get_password_hash

    if chk_mail_esistente(utente.mail, session):
        raise ValueError("Mail già esistente!")

    try:
        nuovo_utente = Utente(
            mail = utente.mail,
            password = get_password_hash(utente.password),
            nome = None,
            cognome = None,
            tipo = "azienda",
            ragione_sociale = utente.ragione_sociale,
            partita_iva = utente.partita_iva
        )
        session.add(nuovo_utente)
        session.commit()

        return nuovo_utente


    except Exception as e:
        session.rollback()
        raise e

def seleziona_utente_da_mail(mail: str, session: Session) -> UtenteAutenticato | None:
    try:
        query = select(Utente).where(Utente.mail == mail)
        utente = session.exec(query).one_or_none()
        if utente is not None:
            return UtenteInput.model_validate(utente)
        else:
            return None

    except Exception as e:
        session.rollback()
        raise e

def get_id_utente(utente: UtenteAutenticato, session: Session) -> int | None:
    try:
        query_utente = select(Utente).where(Utente.uuid_utente == utente.uuid_utente)
        result = session.exec(query_utente).one_or_none()
        if result is not None:
            return result.id_utente
        else:
            return None
    except Exception as e:
        raise e

def get_user_id_from_uuid(uuid_utente: uuid.UUID, session: Session) -> int | None:
    try:
        query = select(Utente).where(Utente.uuid_utente == uuid_utente)
        result = session.exec(query).one_or_none()
        if result is not None:
            return result.id_utente
        else:
            return None
    except Exception as e:
        session.rollback()
        raise e