from __future__ import annotations

import io
from typing import List

import pandas as pd
from fpdf import FPDF

from app.analysis.models import ComparisonFinding, ComparisonResult


def findings_to_dataframe(findings: List[ComparisonFinding]) -> pd.DataFrame:
    if not findings:
        return pd.DataFrame(columns=["type", "severity", "message", "invoice_rows", "po_rows"])

    records = []
    for finding in findings:
        records.append(
            {
                "type": finding.type,
                "severity": finding.severity,
                "message": finding.message,
                "invoice_rows": ", ".join(str(row) for row in finding.invoice_rows) or "n/a",
                "po_rows": ", ".join(str(row) for row in finding.po_rows) or "n/a",
            }
        )
    return pd.DataFrame.from_records(records)


def generate_excel_report(result: ComparisonResult) -> bytes:
    """Create an Excel workbook with normalized data and findings."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df = pd.DataFrame(
            [
                {
                    "metric": "Invoice Total",
                    "value": result.summary.invoice_total,
                },
                {
                    "metric": "PO Total",
                    "value": result.summary.po_total,
                },
                {
                    "metric": "Variance",
                    "value": result.summary.variance,
                },
                {
                    "metric": "Unmatched Invoice Lines",
                    "value": result.summary.unmatched_invoice_lines,
                },
                {
                    "metric": "Unmatched PO Lines",
                    "value": result.summary.unmatched_po_lines,
                },
                {
                    "metric": "Rate Mismatches",
                    "value": result.summary.rate_mismatches,
                },
                {
                    "metric": "Quantity Mismatches",
                    "value": result.summary.quantity_mismatches,
                },
                {
                    "metric": "Duplicate Lines",
                    "value": result.summary.duplicates,
                },
            ]
        )
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        result.normalized_invoice.to_excel(writer, sheet_name="Invoice Lines", index=False)
        result.normalized_po.to_excel(writer, sheet_name="PO Lines", index=False)
        findings_to_dataframe(result.findings).to_excel(writer, sheet_name="Findings", index=False)

    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf_report(result: ComparisonResult, narrative: str) -> bytes:
    """Create a simple PDF summary report using FPDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Invoice vs Purchase Order Review", ln=True, align="C")

    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        (
            f"Invoice total: {result.summary.invoice_total:.2f}\n"
            f"Purchase order total: {result.summary.po_total:.2f}\n"
            f"Variance: {result.summary.variance:.2f}\n"
            f"Unmatched invoice lines: {result.summary.unmatched_invoice_lines}\n"
            f"Unmatched PO lines: {result.summary.unmatched_po_lines}\n"
            f"Rate mismatches: {result.summary.rate_mismatches}\n"
            f"Quantity mismatches: {result.summary.quantity_mismatches}\n"
            f"Duplicate lines: {result.summary.duplicates}\n"
        ),
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Narrative Insights", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, narrative or "No narrative available.")

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Key Findings", ln=True)
    pdf.set_font("Arial", "", 11)

    if not result.findings:
        pdf.multi_cell(0, 6, "No issues detected.")
    else:
        for finding in result.findings:
            pdf.multi_cell(
                0,
                6,
                f"[{finding.severity.upper()}] {finding.type}: {finding.message}",
            )
            pdf.ln(1)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes

