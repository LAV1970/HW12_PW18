# models/contact.py
from pydantic import BaseModel
from datetime import datetime


class Contact(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    birthday: datetime
