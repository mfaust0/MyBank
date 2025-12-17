import uuid
from datetime import date
from typing import List

from sqlalchemy import func, join, update
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from backend.models import Transazione, Movimento, Segno, Conto, Utente, Causale
from backend.schemas import NuovoBonificoInput, UtenteAutenticato, NuovoBonificoOutput, NuovoDepositoInput, \
    NuovoDepositoOutput, MovimentoDettaglioResponse
from backend.services.conti import check_conto_attivo, get_numero_conto, get_conto
from backend.services.utenti import get_id_utente, seleziona_utente_da_mail, chk_mail_esistente

def crea_bonifico(dati_pagamento: NuovoBonificoInput, session: Session, utente_corrente: UtenteAutenticato) -> NuovoBonificoOutput:
    try:

        if not chk_mail_esistente(str(dati_pagamento.beneficiario), session):
            raise ValueError("Il beneficiario non esiste!")

        id_debitore = get_id_utente(utente_corrente, session)
        nr_conto_debitore = get_numero_conto(id_debitore, session)
        utente_beneficiario = seleziona_utente_da_mail(str(dati_pagamento.beneficiario), session)
        id_beneficiario = get_id_utente(utente_beneficiario, session)
        nr_conto_beneficiario = get_numero_conto(id_beneficiario, session)

        if not nr_conto_debitore or not nr_conto_beneficiario:
            raise ValueError("Il conto non esiste!")
        if not check_conto_attivo(get_conto(nr_conto_debitore, session)):
            raise ValueError("Il tuo conto non è abilitato!")
        if not check_conto_attivo(get_conto(nr_conto_beneficiario, session)):
            raise ValueError("Il conto del beneficiario non è abilitato!")

        if dati_pagamento.beneficiario == utente_corrente.mail:
            raise ValueError("Non puoi inviare un bonifico a te stesso!")

        if dati_pagamento.data_esecuzione < date.today():
            raise ValueError("Data non valida!")

        if dati_pagamento.importo <= 1:
            raise ValueError("Inserisci un importo > 1")

        dati_bonifico = Transazione(
            data=date.today(),
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

            if dati_deposito.importo <= 0:
                raise ValueError("Inserisci un importo > 0")

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

def get_transazioni(session: Session, utente_corrente: UtenteAutenticato) -> List[MovimentoDettaglioResponse]:
    try:
        id_utente = get_id_utente(utente_corrente, session)
        numero_conto = get_numero_conto(id_utente, session)

        if numero_conto is None:
            raise ValueError("Il conto non esiste o non è stato trovato!")

        stmt = select(Movimento).join(Transazione).where(
            Movimento.numero_conto == numero_conto
        ).options(
            selectinload(Movimento.transazione),
            selectinload(Movimento.conto),
            selectinload(Movimento.causale)
        ).order_by(
            Transazione.data.desc()
        )

        movimenti_target = session.exec(stmt).all()
        risultati_finali = []

        cache_controparti = {}

        for movimento_target in movimenti_target:

            nome_causale = "N/D"
            if movimento_target.causale:
                nome_causale = movimento_target.causale.descrizione

            segno_target = movimento_target.segno

            transazione_uuid = movimento_target.transazione.uuid_transazione
            nome_controparte = cache_controparti.get(transazione_uuid)

            if not nome_controparte:
                stmt_controparte = select(Conto).join(Movimento).join(Utente).where(
                    Movimento.id_transazione == movimento_target.id_transazione,
                    Movimento.numero_conto != numero_conto
                )

                conto_controparte = session.exec(stmt_controparte).first()

                if conto_controparte and conto_controparte.utente:
                    user_controparte = conto_controparte.utente
                    if user_controparte.tipo == 'privato':
                        nome_controparte = f"{user_controparte.nome} {user_controparte.cognome}"
                    elif user_controparte.tipo == 'azienda':
                        nome_controparte = user_controparte.ragione_sociale

                cache_controparti[transazione_uuid] = nome_controparte

            if movimento_target.transazione.data_esecuzione is not None:
                data = movimento_target.transazione.data_esecuzione
            else:
                data = movimento_target.transazione.data

            risultati_finali.append({
                'uuid_transazione': movimento_target.transazione.uuid_transazione,
                'data_transazione': data,
                'importo_transazione': movimento_target.transazione.importo,
                'descrizione_movimento': movimento_target.descrizione,
                'segno': segno_target,
                'controparte': nome_controparte,
                'nome_causale': nome_causale
            })

        return risultati_finali

    except Exception as e:
        print(f"Errore in get_transazioni: {e}")
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
            transazione = session.exec(
                select(Transazione).where(Transazione.id_transazione == id_transazione)).one_or_none()


            if not verifica_utente_transazione(session, utente_corrente, uuid_transazione):
                raise ValueError("La transazione non esiste o non sei autorizzato ad annullarla!")

            if transazione is not None:
                countBonifico = session.exec(
                    select(func.count(Movimento.id_movimento)).where(Movimento.id_transazione == id_transazione,
                                                                     Movimento.codice_causale == 2)).one()
                if countBonifico == 0:
                    raise ValueError("Non è una disposizione!")
                if transazione.data_esecuzione and transazione.data_esecuzione < date.today():
                    raise ValueError("Transazione già eseguita!")

                movimenti_transazione: list[Movimento] = session.exec(
                    select(Movimento).where(Movimento.id_transazione == id_transazione)
                ).all()

                if len(movimenti_transazione) != 2:
                    raise ValueError("La transazione non ha due movimenti associati")

                for movimento in movimenti_transazione:
                    delta = 0
                    if movimento.segno == Segno.NEGATIVO:
                        delta = transazione.importo
                    elif movimento.segno == Segno.POSITIVO:
                        delta = -transazione.importo
                    else:
                        continue

                    session.exec(
                        update(Conto)
                        .where(Conto.numero_conto == movimento.numero_conto)
                        .values(saldo=Conto.saldo+delta))

                uuid = transazione.uuid_transazione
                session.delete(transazione)
                session.commit()

                return uuid
            else:
                raise ValueError("La transazione non esiste!")
        except Exception as e:
            session.rollback()
            print(f"Errore durante annullamento bonifico: {e}")
            raise e


def verifica_utente_transazione(session: Session, utente_corrente: UtenteAutenticato, uuid_transazione: uuid.UUID) -> bool:
    id_transazione = get_id_transazione_from_uuid(uuid_transazione, session)
    statement = select(Transazione).join(Movimento).join(Conto).where(
        Transazione.id_transazione == id_transazione,
        Conto.id_utente == get_id_utente(utente_corrente, session),
        Movimento.segno == "-"
    )
    result = session.exec(statement).one_or_none()

    if result is not None:
        return True
    else:
        return False