import uuid
from datetime import date
from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from backend.models import Transazione, Movimento, Segno
from backend.schemas import NuovoBonificoInput, UtenteAutenticato, NuovoBonificoOutput, ContoInput, NuovoDepositoInput, \
    NuovoDepositoOutput, MovimentoResponse
from backend.services.conti import check_conto_attivo, get_numero_conto, get_conto
from backend.services.utenti import get_id_utente, seleziona_utente_da_mail


def crea_bonifico(dati_pagamento: NuovoBonificoInput, session: Session, utente_corrente: UtenteAutenticato) -> NuovoBonificoOutput:
    try:
        id_debitore = get_id_utente(utente_corrente, session)
        nr_conto_debitore = get_numero_conto(id_debitore, session)
        utente_beneficiario = seleziona_utente_da_mail(str(dati_pagamento.beneficiario), session)
        id_beneficiario = get_id_utente(utente_beneficiario, session)
        nr_conto_beneficiario = get_numero_conto(id_beneficiario, session)

        if not check_conto_attivo(get_conto(nr_conto_debitore, session)):
            raise ValueError("Conto non abilitato!")
        if not check_conto_attivo(get_conto(nr_conto_beneficiario, session)):
            raise ValueError("Conto non abilitato!")

        dati_bonifico = Transazione(
            data=dati_pagamento.data,
            importo=dati_pagamento.importo,
            data_esecuzione=dati_pagamento.data_esecuzione
        )

        dati_movimento_uscita = Movimento(
            numero_conto=nr_conto_debitore,
            transazione=dati_bonifico,
            codice_causale=2,
            segno=Segno.NEGATIVO,
            descrizione=dati_pagamento.descrizione
        )

        dati_movimento_entrata = Movimento(
            numero_conto=nr_conto_beneficiario,
            transazione=dati_bonifico,
            codice_causale=1,
            segno=Segno.POSITIVO,
            descrizione=dati_pagamento.descrizione
        )

        session.add(dati_movimento_uscita)
        session.add(dati_movimento_entrata)
        #prima del commit devo aggiornare il campo saldo del conto debitore e del conto beneficiario:
        conto_debitore = get_conto(nr_conto_debitore, session)
        conto_beneficiario = get_conto(nr_conto_beneficiario, session)

        if not conto_debitore or not conto_beneficiario:
            raise ValueError("Conto non esiste!")

        if conto_debitore.saldo < dati_pagamento.importo:
            raise ValueError("Fondi insufficienti sul conto debitore.")

        conto_debitore.saldo -= dati_pagamento.importo
        conto_beneficiario.saldo += dati_pagamento.importo

        session.commit()

        session.refresh(dati_bonifico)
        session.refresh(dati_movimento_entrata)
        session.refresh(dati_movimento_uscita)

        return NuovoBonificoOutput(
            uuid_transazione=dati_bonifico.uuid_transazione,
            data=dati_bonifico.data,
            importo=dati_bonifico.importo,
            data_esecuzione=dati_bonifico.data_esecuzione,
            descrizione=dati_movimento_entrata.descrizione,
            beneficiario=dati_pagamento.beneficiario
        )

    except Exception as e:
        session.rollback()
        print(f"Errore durante il commit: {e}")
        raise e

def crea_deposito(dati_deposito: NuovoDepositoInput, session: Session, utente_corrente: UtenteAutenticato) -> NuovoDepositoOutput:

        try:
            id_beneficiario = get_id_utente(utente_corrente, session)
            nr_conto_beneficiario = get_numero_conto(id_beneficiario, session)

            conto_beneficiario = get_conto(nr_conto_beneficiario, session)
            if not check_conto_attivo(conto_beneficiario):
                raise ValueError("Conto non abilitato!")

            tr_deposito = Transazione(
                data=date.today(),
                importo=dati_deposito.importo,
                data_esecuzione=None
            )

            dati_movimento_entrata = Movimento(
                numero_conto=nr_conto_beneficiario,
                transazione=tr_deposito,
                codice_causale=7,
                segno=Segno.POSITIVO,
                descrizione=dati_deposito.descrizione
            )
            session.add(dati_movimento_entrata)
            conto_beneficiario.saldo += dati_deposito.importo
            session.commit()

            return NuovoDepositoOutput(
                uuid_transazione=tr_deposito.uuid_transazione,
                data=tr_deposito.data,
                importo=tr_deposito.importo,
                descrizione=dati_movimento_entrata.descrizione
            )

        except Exception as e:
            session.rollback()
            print(f"Errore durante il commit: {e}")
            raise e

def get_transazioni(session: Session, utente_corrente: UtenteAutenticato) -> Sequence[Movimento]:

        try:
            id_utente = get_id_utente(utente_corrente, session)
            numero_conto = get_numero_conto(id_utente, session)
            conto = get_conto(numero_conto, session)

            if conto is not None:
                query = select(Movimento).where(Movimento.numero_conto == numero_conto).options(selectinload(Movimento.causale), selectinload(Movimento.transazione))
                movimenti = session.exec(query).all()
            else:
                raise ValueError("Il conto non esiste!")

            if not movimenti:
                return []

            return movimenti

        except Exception as e:
            print(f"Errore: {e}")
            raise e


def get_id_transazione_from_uuid(uuid_transazione: uuid.UUID, session: Session) -> int | None:
    try:
        query = select(Transazione).where(Transazione.uuid_transazione == uuid_transazione)
        transazione = session.exec(query).one_or_none()

        if transazione is not None:
            return transazione.id_transazione
        else:
            raise ValueError("La transazione non esiste!")

    except Exception as e:
        print(f"Errore: {e}")
        raise e


def cancella_bonifico(uuid_transazione: uuid.UUID, session: Session, utente_corrente: UtenteAutenticato) -> uuid.UUID:
        try:
            id_transazione = get_id_transazione_from_uuid(uuid_transazione, session)
            transazione = session.exec(select(Transazione).where(Transazione.id_transazione == id_transazione)).one_or_none()

            if transazione is not None:
                countBonifico = session.exec(
                    select(func.count(Movimento.id_movimento)).where(Movimento.id_transazione == id_transazione,
                                                                     Movimento.codice_causale == 2)).one()
                if countBonifico == 0:
                    raise ValueError("La transazione non è annullabile!")
                if transazione.data_esecuzione and transazione.data_esecuzione < date.today():
                    raise ValueError("La transazione è già stata eseguita!")

                uuid = transazione.uuid_transazione
                session.delete(transazione)
                session.commit()

                return uuid

            else:
                raise ValueError("La transazione non esiste!")
        except Exception as e:
            session.rollback()
            # STAMPA L'ERRORE ESATTO QUI!
            print(f"ERRORE DURANTE L'ANNULLAMENTO BONIFICO: {e}")
            raise e
        except Exception as e:
            print(f"Errore: {e}")
            raise e


'''query = select(Movimento).where(Movimento.numero_conto == numero_conto).options(
                    selectinload(Movimento.causale), selectinload(Movimento.transazione))
                movimenti = session.exec(query).all()

'''