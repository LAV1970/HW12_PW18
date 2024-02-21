from pydantic import BaseModel
from typing import Optional


class ContactBase(BaseModel):
    name: str  # Имя контакта
    phone: str  # Номер телефона контакта
    email: str  # Email контакта
    birthday: Optional[str]  # День рождения контакта, необязательное поле


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int  # Идентификатор контакта

    class Config:
        orm_mode = True
