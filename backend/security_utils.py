from datetime import datetime, timezone, timedelta
from typing import Annotated
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from starlette import status

from backend.db_utils import get_db_session
from backend.schemas import UtenteAutenticato, TokenData
from backend.services.utenti import seleziona_utente_da_mail

SECRET_KEY = "b460ca13ed809925ced5d0869c9e8a54ac9aa9a81031520c35f0033a49176798"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/utente/token")

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def autentica_utente(session: Session, mail: str, password: str):
    user = seleziona_utente_da_mail(mail, session)
    if user is None:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_db_session)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    utente = seleziona_utente_da_mail(token_data.username, session)
    if utente is None:
        raise credentials_exception
    return utente


async def get_current_active_user(
    current_user: Annotated[UtenteAutenticato, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user