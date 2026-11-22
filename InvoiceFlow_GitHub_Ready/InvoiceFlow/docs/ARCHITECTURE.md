# System Architecture

## Pipeline Stages
1. **Ingestion (`invoiceflow.extractor`)**: Detects file type (`.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`) and extracts normalized plain text. Uses `pypdf` for digital PDFs and `pytesseract` for rasterized/scanned invoices when installed.
2. **Parsing (`invoiceflow.parser`)**: Extracts vendor metadata, invoice ID, issue/due dates, currency symbol/ISO code, itemized rows (description, quantity, unit price, line total), subtotal, tax, and grand total.
3. **Validation & Scoring (`invoiceflow.validator`)**: Verifies arithmetic consistency between extracted line items, subtotal, tax, and total amount, generating audit flags and a calibrated `0.0 - 1.0` confidence score.
4. **API & Evaluation (`invoiceflow.api`, `invoiceflow.evaluator`)**: Serves extraction over HTTP and runs accuracy benchmarks against sample invoices.
