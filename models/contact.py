# models/contact.py
from pydantic import BaseModel
from datetime import datetime


class Contact(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    birthday: datetime


def my_function(param1, param2):
    """
    Описание функции.

    :param param1: Описание параметра 1.
    :param param2: Описание параметра 2.
    :return: Описание возвращаемого значения.
    """
    # Тело функции
    pass
