from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.routes import conti, utenti, transazioni
from backend.db_utils import create_db_if_not_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_if_not_exists()
    yield
    print("Chiusura dell'applicazione...")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conti.router)
app.include_router(utenti.router)
app.include_router(transazioni.router)




