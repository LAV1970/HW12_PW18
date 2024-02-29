from http import HTTPStatus
import json
from decouple import config  # добавим библиотеку для работы с переменными окружения
from fastapi import FastAPI, Depends, HTTPException, Request, applications
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, Integer, String, Date
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from api.api import Contact, create_contact, get_db
import db
from db import SessionLocal
from models.contact import Contact
from datetime import datetime
from fastapi import FastAPI
from routes import router as routes_router
from fastapi import FastAPI, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import aioredis
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from routes.routes import create_jwt_token, verify_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Настройки для Redis
REDIS_URL = "redis://localhost:6379"
redis = aioredis.from_url(REDIS_URL)


def get_remote_address(request: Request) -> str:
    return request.client.host


# Включите CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost"
    ],  # Уточните доверенные источники, например, ["http://localhost"]
    allow_credentials=True,
    allow_methods=["*"],  # Разрешите все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешите все заголовки
)

DATABASE_URL = "postgresql://lomakin:QwertY_12345@localhost/test12"


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)  # поле аватар


# Создайте класс для хранения данных пользователя
class User(BaseModel):
    username: str


# Создайте RateLimiter
limiter = RateLimiter(key_func=get_remote_address)

# Добавьте RateLimiter в приложение
FastAPILimiter.init(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    # Здесь установите желаемые ограничения для создания контактов
    # Например, 5 запросов в секунду
    points=5,
    minutes=1,
)


async def get_current_user_from_cache(token: str = Depends(oauth2_scheme)) -> dict:
    user = await redis.get(token)
    if user:
        return json.loads(user)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Ручка для создания токена и кеширования пользователя в Redis
@app.post("/token", response_model=dict)
async def create_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = verify_user(db, form_data.username, form_data.password)
    if user:
        # Создаем JWT токен
        access_token_data = {"sub": user["username"]}
        access_token = create_jwt_token(access_token_data)

        # Кешируем пользователя в Redis
        await redis.set(
            access_token, json.dumps(user), expire=3600
        )  # Время жизни в секундах (в данном случае 1 час)

        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Добавьте маршрут из routes.py
app.include_router(routes_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
