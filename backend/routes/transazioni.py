from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import literal
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session, func, case

from backend.db_utils import engine, get_db_session
from backend.models import *
from backend.schemas import MovimentoResponse, NuovoBonificoOutput, NuovoBonificoInput, UtenteAutenticato, \
    NuovoDepositoOutput, NuovoDepositoInput
from backend.security_utils import get_current_user
from backend.services.conti import check_conto_attivo
from backend.services.transazioni import crea_bonifico, crea_deposito, get_transazioni, cancella_bonifico

router = APIRouter(
    prefix="/transazione",
    tags=["transazione"]
)

@router.post("/nuovo_bonifico",
             response_model=NuovoBonificoOutput,
             status_code=status.HTTP_201_CREATED)
async def nuovo_bonifico(
        dati_pagamento: NuovoBonificoInput,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        nuova_transazione = crea_bonifico(dati_pagamento, session, current_user)

        return nuova_transazione

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
            status_code=status.HTTP_201_CREATED)
async def nuovo_deposito(
        dati_deposito: NuovoDepositoInput,
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):

    try:
        nuova_transazione = crea_deposito(dati_deposito, session, current_user)

        return nuova_transazione

    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Transazione esistente")
    except Exception as e:
        session.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Si è verificato un errore interno.")


'''@router.get("/ottieni_saldo/{numero_conto}")
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
'''

@router.get("/movimenti",
            response_model=list[MovimentoResponse],
            status_code=status.HTTP_200_OK)
async def movimenti(
        session: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    try:
        movimenti = get_transazioni(session, current_user)

        return movimenti

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Si è verificato un errore interno.")

@router.delete("/annulla_bonifico/{uuid_transazione}",
               response_model=uuid.UUID,
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(ve)
            )

        except Exception as e:
            session.rollback()
            print(f"ERRORE ENDPOINT: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Si è verificato un errore interno.")
