from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session

from backend.db_utils import get_db_session
from backend.schemas import CreaUtenteAzienda, CreaUtentePrivato, UtentePrivatoOutput, UtenteAziendaOutput, \
    UtenteAutenticato, Token
from backend.security_utils import ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, autentica_utente, get_current_user
from backend.services.utenti import crea_utente_privato, crea_utente_azienda

router = APIRouter(
    prefix="/utente",
    tags=["utente"]
)

@router.post(
    "/crea_utente_privato",
    response_model=UtentePrivatoOutput,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "example1": {
                            "summary": "Esempio di creazione di un utente privato",
                            "value": jsonable_encoder({
                                "nome": "Mario",
                                "cognome":"Rossi",
                                "mail": "mariorossi@dominio.it",
                                "password": "1234abc"
                            })
                        }
                    }
                }
            }
        }
    }
)
def nuovo_utente_privato(utente_privato: CreaUtentePrivato,
                              session: Annotated[Session, Depends(get_db_session)]):

    try:
        utente_creato = crea_utente_privato( utente_privato, session = session )

        return utente_creato

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Si è verificato un errore interno.")


@router.post(
    "/crea_utente_azienda",
    response_model=UtenteAziendaOutput,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "example1": {
                            "summary": "Esempio di creazione di un utente privato",
                            "value": jsonable_encoder({
                                "ragione_sociale": "Pinco Pallino S.p.A.",
                                "partita_iva": "IT1234567890",
                                "mail": "info@pincopallino.it",
                                "password": "44321pallino"
                            })
                        }
                    }
                }
            }
        }
    }
)
def nuovo_utente_azienda(utente_azienda: CreaUtenteAzienda,
                              session: Annotated[Session, Depends(get_db_session)]):

    try:
        utente_creato = crea_utente_azienda( utente_azienda, session = session )

        return utente_creato

    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Utente esiste già")
    except Exception as e:
        session.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Si è verificato un errore interno.")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db_session)]) -> Token:

    utente = autentica_utente(session, form_data.username, form_data.password)
    if not utente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": utente.mail}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UtenteAutenticato)
async def read_users_me(
    current_user: Annotated[UtenteAutenticato, Depends(get_current_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[UtenteAutenticato, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.mail}]