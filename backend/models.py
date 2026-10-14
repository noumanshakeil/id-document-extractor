from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class IdDocument(Base):
    __tablename__ = "id_documents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    doc_type: Mapped[str] = mapped_column(String(32), index=True, default="national_id")
    raw_text: Mapped[str] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(24), index=True, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class IdField(Base):
    __tablename__ = "id_fields"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[str] = mapped_column(String(240), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
