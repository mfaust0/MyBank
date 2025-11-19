import uuid
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import select, Session
from fastapi import APIRouter
from backend.db_utils import engine, get_db_session
from backend.models import Conto
from backend.schemas import ContoOutput, CreaConto, UtenteAutenticato, ChiusuraContoRequest, SaldoContoOutput
from backend.security_utils import get_current_user
from backend.services.conti import aggiungi_conto, chiusura_conto, ottieni_saldo

router = APIRouter(
    prefix="/conto",
    tags=["conto"]
)

@router.post(
    "/apri_conto",
    response_model=ContoOutput,
    status_code=status.HTTP_201_CREATED)
async def apri_conto(conto: CreaConto, session: Annotated[Session, Depends(get_db_session)]):
        try:
            conto_aperto = aggiungi_conto(conto, session)
            print(f"DEBUG Type: {type(conto_aperto.uuid_conto)}")
            print(f"DEBUG Value: {conto_aperto.uuid_conto!r}")
            return conto_aperto

        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(ve)
            )

        except IntegrityError as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Impossibile creare il conto perché esiste già")

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Si è verificato un errore interno.")

@router.patch(
    "/chiudi_conto/",
    response_model=ContoOutput,
    status_code=status.HTTP_200_OK,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "example1": {
                            "summary": "Esempio di chiusura conto",
                            "value": jsonable_encoder({
                                "uuid_conto": "123e4567-e89b-42d3-a456-426655440000"
                            })
                        }
                    }
                }
            }
        }
    })
async def chiudi_conto(
        dati_richiesti: ChiusuraContoRequest,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):

        try:
            conto_chiuso = chiusura_conto(dati_richiesti.uuid_conto, session)

            return conto_chiuso

        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(ve)
            )

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Si è verificato un errore interno.")

@router.get(
    "/saldo",
    response_model=SaldoContoOutput,
    status_code=status.HTTP_200_OK
)
async def get_saldo(
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        saldo = ottieni_saldo(session, current_user)
        return saldo

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Si è verificato un errore interno.")

'''
@router.get("/{numero_conto}")
async def trova_conto(numero_conto: int):
    try:
        return seleziona_conto(numero_conto)
    except SQLAlchemyError as sae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Errore nella richiesta al database"
        )

@router.get("/conti_aperti/")
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

@router.get("/lista_conti/")
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
'''