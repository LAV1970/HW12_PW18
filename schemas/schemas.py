from pydantic import BaseModel
from typing import Optional


class ContactBase(BaseModel):
    name: str
    phone: str
    email: str
    birthday: Optional[str]


class ContactCreate(ContactBase):
    pass


class MainContactSchema(ContactBase):
    id: int

    class Config:
        orm_mode = True
