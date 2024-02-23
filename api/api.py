from msilib import schema
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import schema_json_of, schema_of
from typing import List
from crud import crud
from db import SessionLocal
from schemas.schemas import ContactCreate  # Используйте импорт из crud
from models.contact import Contact

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contacts/", response_model=schema.MainContact)
def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact_data)


@app.get("/contacts/", response_model=List[schema_json_of.MainContact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip=skip, limit=limit)


@app.get("/contacts/{contact_id}", response_model=schema_of.MainContact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
