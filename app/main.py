from __future__ import annotations

import streamlit as st

from app.analysis.analyzer import AgentOutput, run_agent
from app.analysis.comparator import ComparatorConfig
from app.config import Settings, get_settings
from app.reporting.charts import summary_bar_chart, totals_compare_chart
from app.reporting.exporters import (
    findings_to_dataframe,
    generate_excel_report,
    generate_pdf_report,
)


st.set_page_config(page_title="Invoice QA Agent", layout="wide")
st.title("Invoice QA Agent")
st.markdown(
    """
    Upload an invoice and a purchase order (Excel or PDF).  
    The agent will normalize both documents, flag mismatches, and create downloadable audit outputs.
    """
)

if "agent_output" not in st.session_state:
    st.session_state.agent_output = None


def run_analysis(
    invoice_file,
    po_file,
    comparator_config: ComparatorConfig,
    settings: Settings,
) -> AgentOutput:
    invoice_bytes = invoice_file.read()
    po_bytes = po_file.read()
    return run_agent(
        invoice_bytes=invoice_bytes,
        invoice_name=invoice_file.name,
        po_bytes=po_bytes,
        po_name=po_file.name,
        comparator_config=comparator_config,
        settings=settings,
    )


with st.sidebar:
    st.header("Configuration")
    quantity_tol = st.number_input("Quantity tolerance", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    price_tol = st.number_input("Unit price tolerance", min_value=0.0, max_value=10.0, value=0.01, step=0.01)
    total_tol = st.number_input("Line total tolerance", min_value=0.0, max_value=10.0, value=0.01, step=0.01)
    st.markdown("---")
    st.markdown(
        """
        **Need sample files?**  
        Run `python scripts/generate_samples.py` after installing requirements.
        """
    )

invoice_file = st.file_uploader(
    "Invoice file",
    type=["csv", "xls", "xlsx", "xlsm", "pdf"],
    accept_multiple_files=False,
)
po_file = st.file_uploader(
    "Purchase order file",
    type=["csv", "xls", "xlsx", "xlsm", "pdf"],
    accept_multiple_files=False,
)


if invoice_file and po_file:
    if st.button("Run comparison"):
        try:
            with st.spinner("Analyzing documents..."):
                config = ComparatorConfig(
                    quantity_tolerance=quantity_tol,
                    price_tolerance=price_tol,
                    total_tolerance=total_tol,
                )
                settings = get_settings()
                result = run_analysis(invoice_file, po_file, config, settings)
                st.session_state.agent_output = result
        except ValueError as exc:
            st.error(f"Unable to process files: {exc}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unexpected error: {exc}")


agent_output: AgentOutput | None = st.session_state.agent_output

if agent_output:
    summary = agent_output.comparison.summary
    findings_df = findings_to_dataframe(agent_output.comparison.findings)

    st.subheader("Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Invoice Total", f"{summary.invoice_total:,.2f}")
    col2.metric("PO Total", f"{summary.po_total:,.2f}")
    col3.metric("Variance", f"{summary.variance:,.2f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Unmatched Invoice Lines", summary.unmatched_invoice_lines)
    col5.metric("Unmatched PO Lines", summary.unmatched_po_lines)
    col6.metric("Duplicate Lines", summary.duplicates)

    st.subheader("Narrative Insights")
    st.info(agent_output.narrative)

    st.subheader("Discrepancy Insights")
    chart_col, chart_col2 = st.columns(2)
    with chart_col:
        st.altair_chart(summary_bar_chart(agent_output.comparison), use_container_width=True)
    with chart_col2:
        st.altair_chart(totals_compare_chart(agent_output.comparison), use_container_width=True)

    st.subheader("Detailed Findings")
    if findings_df.empty:
        st.success("No discrepancies were detected.")
    else:
        st.dataframe(findings_df, use_container_width=True)

    st.subheader("Normalized Data")
    table_col1, table_col2 = st.columns(2)
    with table_col1:
        st.markdown("**Invoice Lines**")
        st.dataframe(agent_output.comparison.normalized_invoice, use_container_width=True)
    with table_col2:
        st.markdown("**PO Lines**")
        st.dataframe(agent_output.comparison.normalized_po, use_container_width=True)

    st.subheader("Download Outputs")
    excel_bytes = generate_excel_report(agent_output.comparison)
    pdf_bytes = generate_pdf_report(agent_output.comparison, agent_output.narrative)
    st.download_button(
        "Download Excel Report",
        data=excel_bytes,
        file_name="invoice_po_review.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name="invoice_po_review.pdf",
        mime="application/pdf",
    )
else:
    st.info("Upload an invoice and purchase order to begin the comparison.")

