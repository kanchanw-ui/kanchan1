# Invoice QA Agent

An interactive Streamlit application that cross-checks an invoice against a purchase order, highlights mismatches (rates, quantities, totals), uncovers duplicate or unusual lines, and produces downloadable audit reports in Excel and PDF formats. LangChain + GPT provide narrative insights that explain the discrepancies.

## Features
- Accepts invoice and PO uploads in Excel (`.xls`, `.xlsx`, `.xlsm`), CSV, or PDF format.
- Normalizes both documents into a canonical schema for reliable comparisons.
- Flags rate, quantity, total variances, duplicate lines, and statistically unusual charges.
- Presents findings in interactive tables and Altair charts for quick triage.
- Generates downloadable Excel and PDF reports capturing normalized data, findings, and AI-generated commentary.
- Optional GPT-powered narrative summary (falls back to a helpful notice when no API key is provided).

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # and add your OpenAI key if available
streamlit run app/main.py
```

Open the Streamlit URL (usually http://localhost:8501) and upload one invoice plus one purchase order to run the comparison.

## Sample Data
Generate ready-to-use sample files after installing the dependencies:
```bash
python scripts/generate_samples.py
```
This writes `samples/invoice_sample.(xlsx|pdf)` and `samples/po_sample.(xlsx|pdf)` that exercise mismatched rates, duplicates, and missing lines.

## Configuration
- `OPENAI_API_KEY`: set in `.env` (or environment) to enable GPT summaries.
- `OPENAI_MODEL` (optional): defaults to `gpt-4o-mini`.
- Tolerances for quantity, unit price, and line totals can be tuned live in the Streamlit sidebar.

## Architecture
- `app/parsers`: Detect file types, extract tables (pandas for spreadsheets, pdfplumber for PDFs), and normalize headers.
- `app/analysis`: Core comparison logic, mismatch detection, and LangChain-powered narrative generator.
- `app/reporting`: Excel/PDF export utilities and Altair chart builders.
- `app/main.py`: Streamlit front-end wiring uploads, visualization, and downloads.
- `scripts/generate_samples.py`: Utility to fabricate demo invoices and purchase orders.

## Testing & Development Notes
- `python3 -m compileall app` validates syntax without executing external services.
- Altair charts require running within the Streamlit app; PNG/SVG export is not bundled.
- The PDF parser assumes table-based invoices/POs. For image-based PDFs, integrate OCR (e.g., Tesseract) as a future enhancement.

## Future Enhancements
- Vendor-level anomaly detection and budget controls.
- Multi-invoice batch processing with historical trend analysis.
- User authentication and audit logging for enterprise deployment.
