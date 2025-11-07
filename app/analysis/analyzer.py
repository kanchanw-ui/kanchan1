from __future__ import annotations

from dataclasses import dataclass

from app.analysis.comparator import ComparatorConfig, compare_documents
from app.analysis.langchain_agent import generate_summary
from app.analysis.models import ComparisonResult
from app.config import Settings, get_settings
from app.parsers.loader import ParsedDocument, read_table
from app.parsers.transform import normalize_document


@dataclass
class AgentOutput:
    comparison: ComparisonResult
    narrative: str


def run_agent(
    invoice_bytes: bytes,
    invoice_name: str,
    po_bytes: bytes,
    po_name: str,
    comparator_config: ComparatorConfig | None = None,
    settings: Settings | None = None,
) -> AgentOutput:
    """
    High-level entry point to parse the document pair, compare, and
    produce an LLM-driven narrative.
    """
    invoice_doc: ParsedDocument = read_table(invoice_bytes, invoice_name)
    po_doc: ParsedDocument = read_table(po_bytes, po_name)

    normalized_invoice = normalize_document(invoice_doc)
    normalized_po = normalize_document(po_doc)

    comparison = compare_documents(
        normalized_invoice,
        normalized_po,
        config=comparator_config,
    )

    app_settings = settings or get_settings()
    narrative = generate_summary(comparison, app_settings)

    return AgentOutput(comparison=comparison, narrative=narrative)

