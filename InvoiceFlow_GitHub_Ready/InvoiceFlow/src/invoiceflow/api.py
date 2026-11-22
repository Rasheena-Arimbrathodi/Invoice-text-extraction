from fastapi import FastAPI, File, HTTPException, UploadFile
from invoiceflow.config import settings
from invoiceflow.evaluator import run_benchmark
from invoiceflow.extractor import DocumentIngestor
from invoiceflow.models import InvoiceData, TextExtractionRequest
from invoiceflow.parser import InvoiceParser

app = FastAPI(
    title="InvoiceFlow — Structured Invoice Extraction API",
    description="Extract structured line items, taxes, totals, and validation reports from invoices.",
    version="0.1.0",
)

_ingestor = DocumentIngestor()
_parser = InvoiceParser()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}


@app.post("/extract/text", response_model=InvoiceData)
def extract_from_text(payload: TextExtractionRequest):
    return _parser.parse(payload.text)


@app.post("/extract/file", response_model=InvoiceData)
async def extract_from_file(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    try:
        raw_text = _ingestor.extract_from_bytes(content, file.filename or "invoice.txt")
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _parser.parse(raw_text)


@app.get("/evaluate")
def evaluate_pipeline():
    return run_benchmark(data_dir=settings.default_data_dir)
