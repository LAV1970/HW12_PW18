# models/contact.py
from pydantic import BaseModel
from datetime import datetime


class ContactValidator(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    birthday: datetime
