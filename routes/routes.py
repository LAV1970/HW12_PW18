# routes.py
import cloudinary
from ast import Dict
from fastapi import Depends, HTTPException, APIRouter, File, UploadFile
from flask import app
from sqlalchemy.orm import Session
import db
from models.contact import Contact, User  # Импортируйте User
from main import pwd_context  # Импортируйте pwd_context
from jose import JWTError
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from db import get_db, SessionLocal
from http import HTTPStatus
from decouple import config
import smtplib
from email.mime.text import MIMEText


cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
)
router = APIRouter()

SECRET_KEY = config(
    "SECRET_KEY", default="your-secret-key"
)  # используем переменную окружения

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Функция для создания JWT токена
def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# Функция для проверки и декодирования JWT токена
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
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
@router.get("/users/me", response_model=Contact)
async def read_users_me(current_user: Contact = Depends(get_current_user)):
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def verify_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        access_token_data = {"sub": user.username}
        access_token = create_jwt_token(access_token_data)
        return {"access_token": access_token}
    return None


# Endpoint for user authentication
@app.post("/token", response_model=dict)
def create_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    tokens = verify_user(db, form_data.username, form_data.password)
    if tokens:
        return tokens
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid credentials"
    )


# Function to decode and verify JWT token
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token")


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
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


@app.post("/contacts/", response_model=Contact)
def create_contact(
    contact: Contact,
    db: Session = Depends(get_db),  # Используйте функцию get_db
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


# Dependency to get the current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return decode_jwt_token(token)


# Protected endpoint that requires authentication
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


def send_verification_email(email, verification_link):
    # Настройки почтового сервера
    smtp_server = "smtp.yourprovider.com"
    smtp_port = 587
    smtp_username = "your_username"
    smtp_password = "your_password"
    # Формируем сообщение
    subject = "Подтверждение регистрации"
    body = f"Для подтверждения регистрации перейдите по ссылке: {verification_link}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "your_email@example.com"
    msg["To"] = email

    # Подключаемся к почтовому серверу и отправляем сообщение
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail("your_email@example.com", [email], msg.as_string())


@router.get("/verify-email/{verification_token}")
def verify_email(verification_token: str, db: Session = Depends(get_db)):
    try:
        # Декодируем токен
        payload = decode_jwt_token(verification_token)
        username = payload.get("sub")

        # Находим пользователя в базе данных
        user = db.query(User).filter(User.username == username).first()

        # Проверяем, существует ли пользователь и не верифицирован ли он уже
        if user and not user.is_verified:
            # Устанавливаем статус верификации пользователя
            user.is_verified = True
            db.commit()

            return {"message": "Email successfully verified"}
        else:
            # Если пользователь не найден или уже верифицирован, возвращаем ошибку
            raise HTTPException(status_code=400, detail="Invalid verification token")

    except HTTPException as e:
        # Обрабатываем возможные исключения, например, если токен неверен
        return {"message": f"Error verifying email: {str(e)}"}


# Настройки почтового сервера
smtp_server = config("SMTP_SERVER")
smtp_port = config("SMTP_PORT", default=587, cast=int)
smtp_username = config("SMTP_USERNAME")
smtp_password = config("SMTP_PASSWORD")

# ...


def send_verification_email(email, verification_link):
    # Формируем сообщение
    subject = "Подтверждение регистрации"
    body = f"Для подтверждения регистрации перейдите по ссылке: {verification_link}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "your_email@example.com"
    msg["To"] = email

    # Подключаемся к почтовому серверу и отправляем сообщение
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail("your_email@example.com", [email], msg.as_string())


@router.post("/users/me/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Обработка загрузки файла на Cloudinary
    result = cloudinary.uploader.upload(file.file)
    avatar_url = result["secure_url"]

    # Обновление ссылки на аватар в базе данных
    current_user.avatar_url = avatar_url
    db.commit()

    return {"message": "Avatar updated successfully", "avatar_url": avatar_url}
