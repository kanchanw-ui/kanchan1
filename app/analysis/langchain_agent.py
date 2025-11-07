from __future__ import annotations

from typing import List

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.analysis.models import ComparisonFinding, ComparisonResult
from app.config import Settings


SYSTEM_TEMPLATE = """You are an accounts payable quality assurance analyst.
Your task is to review the findings from an automated invoice vs purchase order comparison tool.
Summarize the key discrepancies, highlight any high-severity issues, and suggest the next steps.
"""


def _serialize_findings(findings: List[ComparisonFinding]) -> str:
    if not findings:
        return "No discrepancies detected."

    lines = []
    for finding in findings:
        invoice_rows = (
            ", ".join(str(row) for row in finding.invoice_rows) if finding.invoice_rows else "n/a"
        )
        po_rows = ", ".join(str(row) for row in finding.po_rows) if finding.po_rows else "n/a"
        lines.append(
            f"- [{finding.severity.upper()}] {finding.type}: {finding.message} "
            f"(invoice rows: {invoice_rows}; po rows: {po_rows})"
        )
    return "\n".join(lines)


def generate_summary(result: ComparisonResult, settings: Settings) -> str:
    """
    Use an LLM to produce a natural-language summary of the comparison findings.
    """
    if not settings.has_llm:
        return (
            "LLM summary unavailable: OPENAI_API_KEY not configured. "
            "Set the environment variable to enable narrative insights."
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_TEMPLATE),
            (
                "human",
                "Invoice total: {invoice_total}\n"
                "PO total: {po_total}\n"
                "Variance: {variance}\n"
                "Findings:\n{findings}\n"
                "Provide a concise narrative summary.",
            ),
        ]
    )

    model = ChatOpenAI(
        openai_api_key=settings.openai_api_key,
        model=settings.model_name,
        temperature=settings.model_temperature,
    )

    formatted_prompt = prompt.format_messages(
        invoice_total=result.summary.invoice_total,
        po_total=result.summary.po_total,
        variance=result.summary.variance,
        findings=_serialize_findings(result.findings),
    )

    response = model.invoke(formatted_prompt)
    return response.content

