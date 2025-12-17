from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from fastapi import APIRouter
from backend.db_utils import get_db_session
from backend.schemas import ContoOutput, CreaConto, UtenteAutenticato, ChiusuraContoRequest, SaldoContoOutput
from backend.security_utils import get_current_user
from backend.services.conti import aggiungi_conto, chiusura_conto, ottieni_saldo, get_conto_utente

router = APIRouter(
    prefix="/conto",
    tags=["conto"]
)

@router.post(
    "/apri_conto",
    response_model=ContoOutput,
    responses={
                400: {"description":"Conto esistente!"},
                201: {
                    "description": "Dati del conto",
                    "content": {
                        "application/json": {
                            "example":
                                {"uuid_conto": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                 "data_apertura": "2026-01-15",
                                 "data_chiusura": "None",
                                 "saldo": "50.00",
                                }
                        }
                    },
                },
            },
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "example1": {
                            "summary": "Esempio di apertura di un conto",
                            "value": jsonable_encoder({
                                "saldo_iniziale": "500.00",
                                "uuid_utente": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                            })
                        }
                    }
                }
            }
        }
    }
)
async def apri_conto(conto: CreaConto, session: Annotated[Session, Depends(get_db_session)], current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
        try:
            conto_aperto = aggiungi_conto(conto, session, current_user)
            print(f"DEBUG Type: {type(conto_aperto.uuid_conto)}")
            print(f"DEBUG Value: {conto_aperto.uuid_conto!r}")
            return conto_aperto

        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
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
    responses={
        404: {"description": "Il conto non esiste!"},
        200: {
            "description": "Dati del conto chiuso",
            "content": {
                "application/json": {
                    "example":
                        {"uuid_conto": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                         "data_apertura": "2026-01-15",
                         "data_chiusura": "2026-01-20",
                         "saldo": "0",
                         }
                }
            },
        },
    },
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
            conto_chiuso = chiusura_conto(dati_richiesti.uuid_conto, session, current_user)

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
    responses={
            404: {"description": "Il conto non esiste!"},
            200: {
                "description": "Saldo del conto",
                "content": {
                    "application/json": {
                        "example":
                            {"saldo": "500.56"
                             }
                    }
                },
            },
        },
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

@router.get("/conto",
            response_model=ContoOutput,
            responses={
                404: {"description": "Utente non ha un conto!"},
                200: {
                    "description": "Dati del conto dell'utente",
                    "content": {
                        "application/json": {
                            "example":
                                {"uuid_conto": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                 "data_apertura": "2026-01-15",
                                 "data_chiusura": "2026-01-20",
                                 "saldo": "0",
                                 }
                        }
                    },
                },
            },
            status_code=status.HTTP_200_OK)
async def get_conto(
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        conto = get_conto_utente(session, current_user)
        return conto
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
