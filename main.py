from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from typing import List
from datetime import datetime, timedelta
from models import Contact
import crud
from db import Base, SessionLocal
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

DATABASE_URL = "postgresql://lomakin:QwertY_12345@localhost/test12"

Base = declarative_base()


class Contact(Base):

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)
    birthday = Column(Date)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Функция для создания JWT токена
def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, "your-secret-key", algorithm="HS256")


# Функция для проверки и декодирования JWT токена
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Зависимость для извлечения и проверки токена
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return decode_jwt_token(token)


# Ручка для получения текущего пользователя (аутентификация)
@app.get("/users/me", response_model=Contact)
async def read_users_me(current_user: Contact = Depends(get_current_user)):
    return current_user


# Остальные ручки остаются без изменений

if __name__ == "__main__":
    import uvicorn

    uvicorn.main(app, host="127.0.0.1", port=8000, reload=True)
