from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from crud import crud
from db import SessionLocal
from schemas.schemas import ContactCreate, MainContactSchema


app = FastAPI()


class Contact(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    birthday: datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contacts/", response_model=MainContactSchema)
def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact_data)


@app.get("/contacts/", response_model=List[MainContactSchema])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip=skip, limit=limit)


@app.get("/contacts/{contact_id}", response_model=MainContactSchema)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
