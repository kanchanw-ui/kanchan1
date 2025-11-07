"""
Utility script to generate sample invoice and purchase order files.

Run after installing dependencies:
    pip install -r requirements.txt
    python scripts/generate_samples.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fpdf import FPDF


def _dataframe_to_pdf(df: pd.DataFrame, title: str, filepath: Path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "B", 10)
    column_width = 190 / len(df.columns)
    for column in df.columns:
        pdf.cell(column_width, 8, str(column), border=1, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "", 10)
    for _, row in df.iterrows():
        for value in row:
            pdf.cell(column_width, 8, str(value), border=1)
        pdf.ln(8)
    pdf.output(str(filepath))


def main() -> None:
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    invoice_df = pd.DataFrame(
        [
            {"line_id": "1001", "description": "Widget A", "quantity": 10, "unit_price": 9.5, "total": 95.0},
            {"line_id": "1002", "description": "Widget B", "quantity": 5, "unit_price": 20.0, "total": 110.0},
            {"line_id": "1002", "description": "Widget B Duplicate", "quantity": 5, "unit_price": 20.0, "total": 100.0},
            {"line_id": "1003", "description": "Widget C", "quantity": 3, "unit_price": 50.0, "total": 150.0},
            {"line_id": "1005", "description": "Widget E", "quantity": 2, "unit_price": 120.0, "total": 240.0},
        ]
    )

    po_df = pd.DataFrame(
        [
            {"line_id": "1001", "description": "Widget A", "quantity": 10, "unit_price": 9.5, "total": 95.0},
            {"line_id": "1002", "description": "Widget B", "quantity": 5, "unit_price": 20.0, "total": 100.0},
            {"line_id": "1003", "description": "Widget C", "quantity": 3, "unit_price": 45.0, "total": 135.0},
            {"line_id": "1004", "description": "Widget D", "quantity": 1, "unit_price": 200.0, "total": 200.0},
        ]
    )

    invoice_excel = samples_dir / "invoice_sample.xlsx"
    po_excel = samples_dir / "po_sample.xlsx"
    invoice_pdf = samples_dir / "invoice_sample.pdf"
    po_pdf = samples_dir / "po_sample.pdf"

    invoice_df.to_excel(invoice_excel, index=False)
    po_df.to_excel(po_excel, index=False)

    _dataframe_to_pdf(invoice_df, "Sample Invoice", invoice_pdf)
    _dataframe_to_pdf(po_df, "Sample Purchase Order", po_pdf)

    print(f"Sample files generated in {samples_dir.resolve()}")


if __name__ == "__main__":
    main()

