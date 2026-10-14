# Dev server for id-document-extractor
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
