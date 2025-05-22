## backend/app/template.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from db import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/save")
def save_template(user_id: int, name: str, content: str, db: Session = Depends(get_db)):
    template = models.Template(user_id=user_id, name=name, content=content)
    db.add(template)
    db.commit()
    return {"message": "Template saved"}

@router.get("/list")
def list_templates(user_id: int, db: Session = Depends(get_db)):
    templates = db.query(models.Template).filter(models.Template.user_id == user_id).all()
    return templates