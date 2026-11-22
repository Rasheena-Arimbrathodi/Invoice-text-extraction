from pathlib import Path
from invoiceflow.extractor import DocumentIngestor
from invoiceflow.parser import InvoiceParser


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    ingestor = DocumentIngestor()
    parser = InvoiceParser()

    for sample in sorted(data_dir.glob("sample_invoice_*.txt")):
        raw_text = ingestor.extract_from_path(sample)
        invoice = parser.parse(raw_text)
        print(f"=== {sample.name} ===")
        print(invoice.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
