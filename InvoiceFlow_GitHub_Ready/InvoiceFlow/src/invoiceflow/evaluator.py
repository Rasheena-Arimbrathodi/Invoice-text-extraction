from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from invoiceflow.extractor import DocumentIngestor
from invoiceflow.parser import InvoiceParser


@dataclass
class InvoiceBenchmarkCase:
    filename: str
    expected_invoice_number: str
    expected_currency: str
    expected_total: float


DEFAULT_BENCHMARKS: List[InvoiceBenchmarkCase] = [
    InvoiceBenchmarkCase("sample_invoice_01.txt", "INV-2026-1042", "USD", 1320.00),
    InvoiceBenchmarkCase("sample_invoice_02.txt", "BLF/26-27/0891", "INR", 17700.00),
    InvoiceBenchmarkCase("sample_invoice_03.txt", "NDS-7731", "EUR", 3750.00),
]


def run_benchmark(
    data_dir: str | Path = "data",
    cases: List[InvoiceBenchmarkCase] | None = None,
) -> Dict[str, Any]:
    ingestor = DocumentIngestor()
    parser = InvoiceParser()
    benchmarks = cases or DEFAULT_BENCHMARKS
    base_path = Path(data_dir)

    results = []
    passed = 0

    for case in benchmarks:
        file_path = base_path / case.filename
        text = ingestor.extract_from_path(file_path)
        parsed = parser.parse(text)

        id_ok = parsed.invoice_number == case.expected_invoice_number
        curr_ok = parsed.currency == case.expected_currency
        total_ok = parsed.total_amount == case.expected_total
        math_ok = parsed.validation.is_math_valid
        all_ok = id_ok and curr_ok and total_ok and math_ok

        if all_ok:
            passed += 1

        results.append(
            {
                "filename": case.filename,
                "passed": all_ok,
                "invoice_number": parsed.invoice_number,
                "currency": parsed.currency,
                "total_amount": parsed.total_amount,
                "confidence_score": parsed.confidence_score,
            }
        )

    total = len(benchmarks)
    return {
        "total": total,
        "passed": passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "cases": results,
    }
