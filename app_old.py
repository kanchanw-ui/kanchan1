import streamlit as st
import pandas as pd
import os
from file_parser import FileParser
from ai_agent import InvoiceQAAgent
from output_generator import OutputGenerator
from visualization import create_visualizations
import tempfile

# Page configuration
st.set_page_config(
    page_title="Invoice QA Agent",
    page_icon="📋",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📋 Invoice QA Agent</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Invoice and Purchase Order Comparison System")
    
    # Initialize session state
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'invoice_data' not in st.session_state:
        st.session_state.invoice_data = None
    if 'po_data' not in st.session_state:
        st.session_state.po_data = None
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to enable AI-powered analysis"
        )
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your OpenAI API key to use AI features")
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.header("📤 Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Invoice File")
        invoice_file = st.file_uploader(
            "Upload Invoice (Excel or PDF)",
            type=['xlsx', 'xls', 'pdf'],
            key="invoice"
        )
    
    with col2:
        st.subheader("Purchase Order File")
        po_file = st.file_uploader(
            "Upload Purchase Order (Excel or PDF)",
            type=['xlsx', 'xls', 'pdf'],
            key="po"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process files
    if invoice_file and po_file:
        if st.button("🔍 Analyze & Compare", type="primary", use_container_width=True):
            with st.spinner("Processing files and analyzing..."):
                try:
                    # Parse files
                    parser = FileParser()
                    invoice_data = parser.parse_file(invoice_file)
                    po_data = parser.parse_file(po_file)
                    
                    st.session_state.invoice_data = invoice_data
                    st.session_state.po_data = po_data
                    
                    # Show parsed data for debugging
                    with st.expander("🔍 View Parsed Data (Debug)", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Invoice Data:**")
                            st.write(f"Shape: {invoice_data.shape}")
                            st.write(f"Columns: {list(invoice_data.columns)}")
                            st.dataframe(invoice_data, use_container_width=True)
                        with col2:
                            st.write("**PO Data:**")
                            st.write(f"Shape: {po_data.shape}")
                            st.write(f"Columns: {list(po_data.columns)}")
                            st.dataframe(po_data, use_container_width=True)
                    
                    # Run AI comparison
                    if api_key:
                        agent = InvoiceQAAgent(api_key)
                        comparison_results = agent.compare_invoice_po(invoice_data, po_data)
                    else:
                        # Fallback to rule-based comparison if no API key
                        comparison_results = compare_basic(invoice_data, po_data)
                    
                    # Show debug info about comparison
                    with st.expander("🔍 Comparison Debug Info", expanded=False):
                        debug_data = {
                            "invoice_shape": invoice_data.shape if isinstance(invoice_data, pd.DataFrame) else "Not DataFrame",
                            "po_shape": po_data.shape if isinstance(po_data, pd.DataFrame) else "Not DataFrame",
                            "results_summary": comparison_results.get('summary', {})
                        }
                        if 'debug_info' in comparison_results:
                            debug_data['debug_messages'] = comparison_results['debug_info']
                        st.json(debug_data)
                    
                    st.session_state.comparison_results = comparison_results
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error processing files: {str(e)}")
                    st.exception(e)
    
    # Display results
    if st.session_state.comparison_results:
        display_results(st.session_state.comparison_results)
    
    # Sample data section
    with st.expander("📝 Need Sample Files?"):
        st.info("""
        **Sample File Format:**
        - **Invoice/PO Excel**: Should contain columns like: Item, Description, Quantity, Unit Price, Total, etc.
        - **Invoice/PO PDF**: Should be readable text-based PDF with invoice/PO information
        
        The system will automatically extract relevant data from these files.
        """)

def compare_basic(invoice_data, po_data):
    """Basic rule-based comparison when AI is not available"""
    mismatches = []
    duplicates = []
    anomalies = []
    debug_info = []
    
    if not isinstance(invoice_data, pd.DataFrame) or not isinstance(po_data, pd.DataFrame):
        debug_info.append("ERROR: One or both inputs are not DataFrames")
        return {
            'mismatches': mismatches,
            'duplicates': duplicates,
            'anomalies': anomalies,
            'summary': {
                'total_mismatches': 0,
                'total_duplicates': 0,
                'total_anomalies': 0
            },
            'debug_info': debug_info
        }
    
    invoice_df = invoice_data.copy()
    po_df = po_data.copy()
    
    debug_info.append(f"Invoice columns: {list(invoice_df.columns)}")
    debug_info.append(f"PO columns: {list(po_df.columns)}")
    
    # Find item column (case-insensitive, handle variations)
    invoice_item_col = None
    po_item_col = None
    
    item_keywords = ['item', 'item_no', 'item_number', 'product', 'product_code', 'sku', 'item code', 'item_code', 
                     'item name', 'itemname', 'part number', 'part_number', 'partno', 'part_no']
    
    for col in invoice_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in item_keywords or any(kw in col_lower for kw in item_keywords):
            invoice_item_col = col
            debug_info.append(f"Found invoice item column: {col}")
            break
    
    for col in po_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in item_keywords or any(kw in col_lower for kw in item_keywords):
            po_item_col = col
            debug_info.append(f"Found PO item column: {col}")
            break
    
    if not invoice_item_col:
        debug_info.append("WARNING: Could not find item column in invoice")
    if not po_item_col:
        debug_info.append("WARNING: Could not find item column in PO")
    
    # Find price/rate columns
    invoice_price_col = None
    po_price_col = None
    
    price_keywords = ['unit price', 'price', 'rate', 'unit cost', 'cost', 'unit_price', 'unitprice', 
                      'unit_price', 'unit cost', 'unitcost', 'selling price', 'selling_price', 
                      'unit rate', 'unitrate', 'amount', 'price per unit']
    
    for col in invoice_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in price_keywords or any(kw in col_lower for kw in price_keywords):
            invoice_price_col = col
            debug_info.append(f"Found invoice price column: {col}")
            break
    
    for col in po_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in price_keywords or any(kw in col_lower for kw in price_keywords):
            po_price_col = col
            debug_info.append(f"Found PO price column: {col}")
            break
    
    # Find quantity columns
    invoice_qty_col = None
    po_qty_col = None
    
    for col in invoice_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in ['quantity', 'qty', 'qty.', 'amount']:
            invoice_qty_col = col
            break
    
    for col in po_df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in ['quantity', 'qty', 'qty.', 'amount']:
            po_qty_col = col
            break
    
    # Check for duplicates in invoice
    if invoice_item_col:
        # Remove NaN and empty values before counting
        valid_items = invoice_df[invoice_item_col].dropna()
        valid_items = valid_items[valid_items.astype(str).str.strip() != '']
        item_counts = valid_items.value_counts()
        debug_info.append(f"Checking {len(item_counts)} unique items for duplicates")
        
        for item, count in item_counts.items():
            if count > 1:
                duplicates.append({
                    'type': 'Duplicate Item',
                    'item': str(item),
                    'occurrences': int(count),
                    'description': f'Item "{item}" appears {count} times in invoice',
                    'severity': 'Medium'
                })
                debug_info.append(f"Found duplicate: {item} appears {count} times")
    
    # Compare items between invoice and PO
    if invoice_item_col and po_item_col:
        debug_info.append(f"Comparing items using columns: Invoice='{invoice_item_col}', PO='{po_item_col}'")
        
        # Convert to string for comparison, handling NaN
        invoice_df[invoice_item_col] = invoice_df[invoice_item_col].fillna('').astype(str)
        po_df[po_item_col] = po_df[po_item_col].fillna('').astype(str)
        
        # Get unique invoice items
        invoice_items_list = invoice_df[invoice_item_col].str.strip().unique()
        invoice_items_list = [item for item in invoice_items_list if item and item.lower() != 'nan']
        debug_info.append(f"Found {len(invoice_items_list)} unique items in invoice")
        
        items_compared = 0
        items_with_mismatches = 0
        
        for idx, inv_row in invoice_df.iterrows():
            item = str(inv_row.get(invoice_item_col, '')).strip()
            if not item or item.lower() == 'nan' or item == '':
                continue
            
            items_compared += 1
            
            # Find matching item in PO (case-insensitive comparison)
            po_matches = po_df[po_df[po_item_col].astype(str).str.strip().str.lower() == item.lower()]
            
            if po_matches.empty:
                # Item in invoice but not in PO
                anomalies.append({
                    'type': 'Item Not in PO',
                    'item': item,
                    'description': f'Item "{item}" found in invoice but not in purchase order',
                    'severity': 'High'
                })
                debug_info.append(f"Item '{item}' not found in PO")
            else:
                po_row = po_matches.iloc[0]
                
                # Check price/rate
                if invoice_price_col and po_price_col:
                    try:
                        inv_price_val = inv_row.get(invoice_price_col, None)
                        po_price_val = po_row.get(po_price_col, None)
                        
                        inv_price = pd.to_numeric(inv_price_val, errors='coerce')
                        po_price = pd.to_numeric(po_price_val, errors='coerce')
                        
                        debug_info.append(f"Item '{item}': Invoice price={inv_price_val} (parsed={inv_price}), PO price={po_price_val} (parsed={po_price})")
                        
                        if pd.notna(inv_price) and pd.notna(po_price):
                            diff = abs(float(inv_price) - float(po_price))
                            if diff > 0.01:  # Allow small rounding differences
                                items_with_mismatches += 1
                                severity = 'High' if diff > abs(po_price) * 0.1 else 'Medium'
                                mismatches.append({
                                    'type': 'Rate Mismatch',
                                    'item': item,
                                    'invoice_value': f"{inv_price:.2f}",
                                    'po_value': f"{po_price:.2f}",
                                    'difference': f"{diff:.2f}",
                                    'severity': severity,
                                    'description': f'Unit price mismatch: Invoice={inv_price:.2f}, PO={po_price:.2f}'
                                })
                                debug_info.append(f"Found price mismatch for '{item}': {inv_price} vs {po_price} (diff={diff})")
                    except (ValueError, TypeError) as e:
                        debug_info.append(f"Error comparing price for '{item}': {str(e)}")
                
                # Check quantity
                if invoice_qty_col and po_qty_col:
                    try:
                        inv_qty_val = inv_row.get(invoice_qty_col, None)
                        po_qty_val = po_row.get(po_qty_col, None)
                        
                        inv_qty = pd.to_numeric(inv_qty_val, errors='coerce')
                        po_qty = pd.to_numeric(po_qty_val, errors='coerce')
                        
                        if pd.notna(inv_qty) and pd.notna(po_qty):
                            diff = abs(float(inv_qty) - float(po_qty))
                            if diff > 0.01:
                                mismatches.append({
                                    'type': 'Quantity Mismatch',
                                    'item': item,
                                    'invoice_value': f"{inv_qty:.2f}",
                                    'po_value': f"{po_qty:.2f}",
                                    'difference': f"{diff:.2f}",
                                    'severity': 'High',
                                    'description': f'Quantity mismatch: Invoice={inv_qty:.2f}, PO={po_qty:.2f}'
                                })
                                debug_info.append(f"Found quantity mismatch for '{item}': {inv_qty} vs {po_qty} (diff={diff})")
                    except (ValueError, TypeError) as e:
                        debug_info.append(f"Error comparing quantity for '{item}': {str(e)}")
        
        debug_info.append(f"Compared {items_compared} items, found {items_with_mismatches} with price mismatches")
        
        # Check for items in PO but not in invoice
        invoice_items = set(invoice_df[invoice_item_col].astype(str).str.strip())
        for idx, po_row in po_df.iterrows():
            item = str(po_row.get(po_item_col, '')).strip()
            if item and item != 'nan' and item not in invoice_items:
                anomalies.append({
                    'type': 'Item Missing in Invoice',
                    'item': item,
                    'description': f'Item "{item}" in PO but not found in invoice',
                    'severity': 'High'
                })
    
    debug_info.append(f"Total mismatches found: {len(mismatches)}")
    debug_info.append(f"Total duplicates found: {len(duplicates)}")
    debug_info.append(f"Total anomalies found: {len(anomalies)}")
    
    return {
        'mismatches': mismatches,
        'duplicates': duplicates,
        'anomalies': anomalies,
        'summary': {
            'total_mismatches': len(mismatches),
            'total_duplicates': len(duplicates),
            'total_anomalies': len(anomalies)
        },
        'debug_info': debug_info
    }

def display_results(results):
    st.header("📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Mismatches", results['summary']['total_mismatches'])
    with col2:
        st.metric("Duplicates Found", results['summary']['total_duplicates'])
    with col3:
        st.metric("Anomalies Detected", results['summary']['total_anomalies'])
    with col4:
        total_issues = sum([
            results['summary']['total_mismatches'],
            results['summary']['total_duplicates'],
            results['summary']['total_anomalies']
        ])
        st.metric("Total Issues", total_issues)
    
    # Visualizations
    if total_issues > 0:
        st.subheader("📈 Visualizations")
        fig = create_visualizations(results)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔴 Mismatches", "🔄 Duplicates", "⚠️ Anomalies", "📋 Full Report"])
    
    with tab1:
        if results['mismatches']:
            df_mismatches = pd.DataFrame(results['mismatches'])
            st.dataframe(df_mismatches, use_container_width=True)
        else:
            st.success("✅ No mismatches found!")
    
    with tab2:
        if results['duplicates']:
            df_duplicates = pd.DataFrame(results['duplicates'])
            st.dataframe(df_duplicates, use_container_width=True)
        else:
            st.success("✅ No duplicates found!")
    
    with tab3:
        if results['anomalies']:
            df_anomalies = pd.DataFrame(results['anomalies'])
            st.dataframe(df_anomalies, use_container_width=True)
        else:
            st.success("✅ No anomalies detected!")
    
    with tab4:
        st.json(results)
    
    # Download section
    st.header("💾 Download Results")
    output_gen = OutputGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate Excel
        excel_buffer = output_gen.generate_excel(results, st.session_state.invoice_data, st.session_state.po_data)
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_buffer,
            file_name="invoice_qa_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Generate PDF
        try:
            pdf_buffer = output_gen.generate_pdf(results, st.session_state.invoice_data, st.session_state.po_data)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name="invoice_qa_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"⚠️ PDF generation unavailable: {str(e)}")
            st.info("💡 Excel download is still available. To fix PDF generation, please reinstall Pillow: `pip install --force-reinstall Pillow==10.1.0`")

if __name__ == "__main__":
    main()

