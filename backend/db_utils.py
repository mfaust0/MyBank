from pathlib import Path
from typing import AsyncGenerator, Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session, select

from backend.models import Causale

BASE_DIR = Path(__file__).parent
sqlite_file_name = BASE_DIR / "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

def create_db_if_not_exists():
    db_file = Path(sqlite_file_name)
    if not db_file.is_file():
        print("Database non trovato. Creazione di un nuovo database e delle tabelle...")
        SQLModel.metadata.create_all(engine)
        with SessionLocal() as session:
            popola_causali(session)

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def popola_causali(session: Session):
    bonifico_in_ingresso = Causale(descrizione="BONIFICO IN INGRESSO")
    bonifico_in_uscita = Causale(descrizione="BONIFICO IN USCITA")
    pagamento = Causale(descrizione="PAGAMENTO_BANCOMAT")
    incasso = Causale(descrizione="INCASSO GENERICO")
    interessi = Causale(descrizione="ACCREDITO INTERESSI")
    commissioni = Causale(descrizione="COMMISSIONI")
    deposito = Causale(descrizione="DEPOSITO")

    check_exist = session.exec(select(Causale).limit(1)).first()
    if check_exist is None:
        session.add(bonifico_in_ingresso)
        session.add(bonifico_in_uscita)
        session.add(pagamento)
        session.add(incasso)
        session.add(interessi)
        session.add(commissioni)
        session.add(deposito)
        session.commit()