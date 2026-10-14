from fastapi import APIRouter
from backend.api import health, id_docs, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(id_docs.router, prefix="/api", tags=["id_docs"])
api_router.include_router(ui.router, tags=["ui"])
