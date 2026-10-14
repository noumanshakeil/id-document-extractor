from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import id_docs as svc

class DocIn(BaseModel):
    doc_type: str = "national_id"
    raw_text: str = Field(min_length=5)

class VerifyIn(BaseModel):
    approve: bool = True

router = APIRouter()

@router.post("/documents")
async def ingest(payload: DocIn, db: AsyncSession = Depends(get_db)):
    doc = await svc.ingest_document(db, payload.doc_type, payload.raw_text)
    return {"id": doc.id, "verification_status": doc.verification_status}

@router.get("/documents")
async def list_docs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_documents(db)
    return {"documents": [{"id": d.id, "doc_type": d.doc_type, "status": d.verification_status} for d in rows]}

@router.get("/documents/{doc_id}/fields")
async def fields(doc_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.fields_for(db, doc_id)
    return {"fields": [{"name": f.name, "value": f.value, "confidence": f.confidence} for f in rows]}

@router.post("/documents/{doc_id}/verify")
async def verify(doc_id: str, payload: VerifyIn, db: AsyncSession = Depends(get_db)):
    try:
        doc = await svc.verify(db, doc_id, payload.approve)
        return {"id": doc.id, "verification_status": doc.verification_status}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
