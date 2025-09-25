from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..db import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=schemas.Document)
def upload_document(
    doc: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    bot_user_id: int = 1,
    desktop_user_id: int = 1
):
    """Загрузить зашифрованный документ"""
    return crud.create_document(db, doc, bot_user_id, desktop_user_id)


@router.get("/list", response_model=list[schemas.Document])
def list_documents(
    db: Session = Depends(get_db),
    bot_user_id: int = 1
):
    """Список документов пользователя"""
    return crud.get_documents(db, bot_user_id)


@router.get("/{doc_id}", response_model=schemas.Document)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Получить документ по ID"""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Удалить документ по ID"""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"status": "deleted", "doc_id": doc_id}
