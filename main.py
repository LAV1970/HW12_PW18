from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from typing import List
from datetime import datetime, timedelta
from models import Contact
import crud

DATABASE_URL = "sqlite:///./test.db"

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)
    birthday = Column(Date)


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ContactValidator(BaseModel):
    name: str
    phone: str
    email: str


# Ручка для создания нового контакта
@app.post("/contacts/", response_model=ContactValidator)
def create_contact(contact: ContactValidator, db: Session = Depends(get_db)):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


# Ручка для получения списка всех контактов
@app.get("/contacts/", response_model=List[ContactValidator])
def get_all_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts


# Ручка для получения одного контакта по идентификатору
@app.get("/contacts/{contact_id}", response_model=ContactValidator)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# Ручка для обновления существующего контакта
@app.put("/contacts/{contact_id}", response_model=ContactValidator)
def update_contact(
    contact_id: int, updated_contact: ContactValidator, db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for field, value in updated_contact.dict().items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


# Ручка для удаления контакта
@app.delete("/contacts/{contact_id}", response_model=ContactValidator)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return contact


@app.get("/contacts/", response_model=List[ContactValidator])
def get_contacts(
    query: str = Query(
        None, title="Search Query", description="Search by name, last name, or email"
    ),
    db: Session = Depends(get_db),
):
    # Если запрос поиска не пустой, выполняем поиск
    if query:
        contacts = crud.get_contacts_by_query(db, query)
    else:
        # Если запрос поиска пустой, возвращаем все контакты
        contacts = crud.get_all_contacts(db)

    return contacts


@app.get("/contacts/birthdays/", response_model=List[ContactValidator])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    # Получаем текущую дату
    current_date = datetime.now()

    # Получаем дату через 7 дней
    seven_days_later = current_date + timedelta(days=7)

    # Здесь реализуем логику поиска контактов с днями рождения на ближайшие 7 дней
    # Пример: crud.get_upcoming_birthdays(db, current_date, seven_days_later)
    upcoming_birthdays = crud.get_upcoming_birthdays(db, current_date, seven_days_later)

    return upcoming_birthdays


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
