from __future__ import annotations
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import IdDocument, IdField
from backend.utils.ids import short_id
from backend.vision.pipeline import run_offline_pipeline
from backend.vision.validators import clamp_confidence

_PATTERNS = {
    "name": re.compile(r"name\s*[:=]\s*([^\n;]+)", re.I),
    "dob": re.compile(r"(dob|birth)\s*[:=]\s*([^\n;]+)", re.I),
    "id_number": re.compile(r"(id|document)\s*[#:]?\s*([A-Z0-9-]+)", re.I),
}

async def ingest_document(session: AsyncSession, doc_type: str, raw_text: str) -> IdDocument:
    pipe = run_offline_pipeline(raw_text, steps=["normalize", "ocr"])
    doc = IdDocument(id=short_id(), doc_type=doc_type[:32], raw_text=pipe["text"], verification_status="pending")
    session.add(doc)
    await session.flush()
    for field, rx in _PATTERNS.items():
        m = rx.search(pipe["text"])
        val = (m.group(2 if field == "dob" else 1) if m else "").strip()[:240]
        conf = clamp_confidence(0.92 if val else 0.35)
        session.add(IdField(id=short_id(), document_id=doc.id, name=field, value=val, confidence=conf))
    await session.commit()
    await session.refresh(doc)
    return doc

async def list_documents(session: AsyncSession) -> list[IdDocument]:
    return list((await session.execute(select(IdDocument).order_by(IdDocument.created_at.desc()))).scalars())

async def fields_for(session: AsyncSession, document_id: str) -> list[IdField]:
    stmt = select(IdField).where(IdField.document_id == document_id)
    return list((await session.execute(stmt)).scalars())

async def verify(session: AsyncSession, document_id: str, approve: bool) -> IdDocument:
    doc = await session.get(IdDocument, document_id)
    if not doc:
        raise ValueError("document not found")
    fields = await fields_for(session, document_id)
    avg = sum(f.confidence for f in fields) / max(len(fields), 1)
    if approve and avg >= 0.7:
        doc.verification_status = "verified"
    elif approve:
        doc.verification_status = "manual_review"
    else:
        doc.verification_status = "rejected"
    await session.commit()
    await session.refresh(doc)
    return doc
