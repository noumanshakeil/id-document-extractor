from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import id_docs as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    docs = await svc.list_documents(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "ID Document Extractor", "documents": docs})

@router.post("/ui/documents")
async def ui_doc(raw_text: str = Form(...), db: AsyncSession = Depends(get_db)):
    doc = await svc.ingest_document(db, "national_id", raw_text)
    await svc.verify(db, doc.id, True)
    return RedirectResponse("/", status_code=303)
