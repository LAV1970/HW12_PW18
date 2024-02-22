from ast import Dict
import fastapi
from collections import UserDict, UserList
from http import HTTPStatus
from jwt import PyJWTError
from mysqlx import Column
from psycopg2 import Date
import statistics
from sqlalchemy import Integer, String
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from api.api import get_db

# Add the missing import statement
from fastapi.security import OAuth2PasswordRequestForm

import db
from models import Contact
from db import Base, SessionLocal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, Session, sessionmaker

DATABASE_URL = "postgresql://lomakin:QwertY_12345@localhost/test12"

Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Создайте экземпляр класса `OAuth2PasswordBearer` для обработки токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Contact(Base):

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)
    birthday = Column(Date)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class ContactValidator(BaseModel):
    name: str
    phone: str
    email: str


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


def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, "your-secret-key", algorithm="HS256")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(UserDict).filter(UserList.username == username).first()


def verify_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = verify_user(db, form_data.username, form_data.password)
    if db_user:
        access_token_data = {"sub": db_user.username}
        access_token = create_jwt_token(access_token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db_user = get_user(db, username)
    if db_user is None:
        raise credentials_exception
    return db_user


# Создайте класс для хранения данных пользователя
class User(BaseModel):
    username: str


# Создайте функцию для создания JWT токена:
def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    credentials_exception = HTTPException(
        status_code=statistics.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"sub": username}
    except JWTError:
        raise credentials_exception
    return token_data


@app.post("/contacts/", response_model=ContactValidator)
def create_contact(
    contact: ContactValidator,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):
    existing_contact = db.query(Contact).filter(Contact.email == contact.email).first()
    if existing_contact:
        # Если пользователь с таким email уже существует, возвращаем ошибку 409
        raise HTTPException(
            status_code=HTTPStatus.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


if __name__ == "__main__":
    import uvicorn

    uvicorn.main(app, host="127.0.0.1", port=8000, reload=True)
