from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import select, Session, func, case

from backend.db_utils import engine, get_db_session
from backend.models import *
from backend.schemas import MovimentoResponse, NuovoBonificoOutput, NuovoBonificoInput, UtenteAutenticato, \
    NuovoDepositoOutput, NuovoDepositoInput, NuovoPagamentoOutput, NuovoPagamentoInput, MovimentoDettaglioResponse
from backend.security_utils import get_current_user
from backend.services.transazioni import crea_bonifico, crea_deposito, get_transazioni, cancella_bonifico

router = APIRouter(
    prefix="/transazione",
    tags=["transazione"]
)

@router.post("/nuovo_bonifico",
             response_model=NuovoBonificoOutput,
             responses={
                400: {"description": "Conto non abilitato!"},
                201: {
                    "description": "Dati del bonifico",
                    "content": {
                        "application/json": {
                            "example":
                                {"uuid_transazione": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                 "beneficiario": "mario.rossi@dominio.it",
                                 "data_esecuzione": "2026-01-15",
                                 "importo": "50.00",
                                 "descrizione": "saldo fattura"
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
                                     "summary": "Esempio di creazione di un nuovo bonifico",
                                     "value": jsonable_encoder({
                                         "beneficiario": "mario.rossi@dominio.com",
                                         "data_esecuzione": "2026-02-17",
                                         "importo": "5",
                                         "descrizione": "saldo fattura"
                                     })
                                 }
                             }
                         }
                     }
                 }
             }
             )
async def nuovo_bonifico(
        dati_pagamento: NuovoBonificoInput,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        nuova_transazione = crea_bonifico(dati_pagamento, session, current_user)

        return nuova_transazione

    except ValueError as ve:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Transazione esistente")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Si è verificato un errore interno.")

@router.post("/nuovo_deposito",
            response_model=NuovoDepositoOutput,
            responses={
                400: {"description": "Conto non abilitato!"},
                201: {
                     "description": "Dati del deposito",
                     "content": {
                         "application/json": {
                             "example":
                                 {"uuid_transazione": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                  "importo": "450.00",
                                  "descrizione": "versato contanti"
                                  }
                         }
                     },
                 },
             },
             openapi_extra={
                 "requestBody": {
                     "content": {
                         "application/json": {
                             "examples": {
                                 "example1": {
                                     "summary": "Esempio di creazione di un nuovo deposito",
                                     "value": jsonable_encoder({
                                         "importo": "5",
                                         "descrizione": "saldo fattura"
                                     })
                                 }
                             }
                         }
                     }
                 }
             },
            status_code=status.HTTP_201_CREATED)
async def nuovo_deposito(
        dati_deposito: NuovoDepositoInput,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):

    try:
        nuova_transazione = crea_deposito(dati_deposito, session, current_user)

        return nuova_transazione

    except ValueError as ve:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Conto non abilitato!")
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Transazione esistente")
    except Exception as e:
        session.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Si è verificato un errore interno.")

@router.get("/movimenti",
            response_model=list[MovimentoDettaglioResponse],
            responses={
                400: {"description": "Conto non trovato"},
                200: {
                    "description": "Lista movimenti",
                    "content": {
                        "application/json": {
                            "example":[
                                    {"uuid_transazione": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                     "data_transazione":"2025-12-25",
                                     "importo_transazione":"50.04",
                                     "descrizione_movimento": "saldo fattura 853",
                                     "segno": "-",
                                     "controparte": "Giuseppe Verdi",
                                     "nome_causale": "BONIFICO IN USCITA"
                                     },
                                    {"uuid_transazione": "6cd23x12-9834-1295-n4fc-7f634j34kdc5",
                                     "data_transazione":"2025-10-03",
                                     "importo_transazione":"100",
                                     "descrizione_movimento": "saldo consulenza",
                                     "segno": "+",
                                     "controparte": "Elena Bianchi",
                                     "nome_causale": "BONIFICO IN ENTRATA"
                                     }
                            ]
                        }
                    },
                },
            },
            status_code=status.HTTP_200_OK)
async def movimenti(
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        movimenti = get_transazioni(session, current_user)

        return movimenti

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Si è verificato un errore interno.")

@router.delete("/annulla_bonifico/{uuid_transazione}",
               response_model=uuid.UUID,
               responses={
                   400: {"description": "Transazione non annullabile!"},
                   200: {
                       "description": "Uuid della transazione annullata",
                       "content": {
                           "application/json": {
                               "example":
                                   {"uuid_transazione": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                                    }
                           }
                       },
                   },
               },
               openapi_extra={
                   "requestBody": {
                       "content": {
                           "application/json": {
                               "examples": {
                                   "example1": {
                                       "summary": "Esempio di annullamento di una transazione",
                                       "value": jsonable_encoder({
                                           "uuid_transazione": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                                       })
                                   }
                               }
                           }
                       }
                   }
               },
               status_code=status.HTTP_200_OK
            )
async def annulla_bonifico(
        uuid_transazione: uuid.UUID,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):

        try:
            transazione = cancella_bonifico(uuid_transazione, session, current_user)

            return transazione

        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )

        except Exception as e:
            session.rollback()
            print(f"ERRORE ENDPOINT: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Si è verificato un errore interno.")
