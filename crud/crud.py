import datetime
from sqlalchemy.orm import Session
from models import Contact


def create_contact(db: Session, contact_data: dict):
    # Извлекаем данные из словаря
    name = contact_data.get("name")
    phone = contact_data.get("phone")
    email = contact_data.get("email")
    birthday = contact_data.get("birthday")

    # Создаем объект Contact, включая дату рождения
    contact = Contact(name=name, phone=phone, email=email, birthday=birthday)

    # Добавляем контакт в сессию и сохраняем изменения
    db.add(contact)
    db.commit()

    # Обновляем объект, чтобы иметь актуальные значения из базы данных
    db.refresh(contact)

    return contact


def get_contacts_by_query(db: Session, query: str):
    # Используем метод ilike для регистронезависимого поиска
    return (
        db.query(Contact)
        .filter(
            (Contact.name.ilike(f"%{query}%"))
            | (Contact.phone.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%"))
        )
        .all()
    )


def get_all_contacts(db: Session):
    # Возвращаем все контакты
    return db.query(Contact).all()


def get_upcoming_birthdays(db: Session, start_date: datetime, end_date: datetime):
    # Используем метод filter для поиска контактов с днями рождения в заданном диапазоне
    return (
        db.query(Contact)
        .filter((Contact.birthday >= start_date) & (Contact.birthday <= end_date))
        .all()
    )
