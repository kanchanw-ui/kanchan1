import streamlit as st
import pandas as pd
import os
import json
from file_parser import FileParser
from ai_agent import InvoiceQAAgent
from output_generator import OutputGenerator
from visualization import create_visualizations
from database import Database
from file_storage import FileStorage
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Invoice QA Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and storage
db = Database()
storage = FileStorage()

# Professional Custom CSS
st.markdown("""
    <style>
    /* Main Header - Professional Blue */
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
        letter-spacing: -0.5px;
    }
    
    /* Card Styles - Clean and Professional */
    .upload-section {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
    }
    
    /* Professional Button Styles */
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: background-color 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    
    /* Secondary Button */
    button[kind="secondary"] {
        background-color: #6b7280;
        color: white;
    }
    
    button[kind="secondary"]:hover {
        background-color: #4b5563;
    }
    
    /* Metric Cards - Professional */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Sidebar - Light Professional */
    .css-1d391kg {
        background-color: #f9fafb;
    }
    
    /* Input Fields - Clean */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        padding: 0.5rem;
        font-size: 0.95rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    /* File Uploader */
    .uploadedFile {
        background: #f9fafb;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
    }
    
    /* Tabs - Professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #6b7280;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        border-radius: 6px;
        padding: 1rem;
        border-left: 4px solid #10b981;
    }
    
    .stError {
        border-radius: 6px;
        padding: 1rem;
        border-left: 4px solid #ef4444;
    }
    
    .stInfo {
        border-radius: 6px;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional Card */
    .info-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    /* Professional Text */
    .section-header {
        color: #1e3a8a;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Professional Metric Card */
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    
    .metric-card-title {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0.5rem 0;
    }
    
    /* Status Colors */
    .status-high {
        color: #dc2626;
    }
    
    .status-medium {
        color: #f59e0b;
    }
    
    .status-low {
        color: #10b981;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'invoice_data' not in st.session_state:
        st.session_state.invoice_data = None
    if 'po_data' not in st.session_state:
        st.session_state.po_data = None
    if 'current_upload_id' not in st.session_state:
        st.session_state.current_upload_id = None

def login_page():
    """Login/Register page with professional UI"""
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-header">Invoice QA Agent</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1rem; margin-bottom: 2rem; font-weight: 400;">AI-Powered Invoice & Purchase Order Comparison System</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown("### Sign In")
            st.markdown('<p style="color: #6b7280; margin-bottom: 1.5rem;">Enter your credentials to access the system</p>', unsafe_allow_html=True)
            
            with st.container():
                username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                
                if st.button("Login", type="primary", width='stretch'):
                    user = db.authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success("Login successful. Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            st.markdown("### Create Account")
            st.markdown('<p style="color: #6b7280; margin-bottom: 1.5rem;">Register to start using the system</p>', unsafe_allow_html=True)
            
            with st.container():
                new_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
                new_email = st.text_input("Email (optional)", key="reg_email", placeholder="your.email@example.com")
                new_password = st.text_input("Password", type="password", key="reg_password", placeholder="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter password")
                
                if st.button("Register", type="primary", width='stretch'):
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif not new_username:
                        st.error("Username is required")
                    else:
                        if db.create_user(new_username, new_password, new_email):
                            st.success("Registration successful. Please login.")
                        else:
                            st.error("Username already exists")
        
        # Info box
        st.markdown("---")
        st.info("**Default Admin Account:** Username: `admin` | Password: `admin123`")

def compare_basic(invoice_data, po_data):
    """Dynamic rule-based comparison that handles any invoice/PO format"""
    from comparison_utils import (
        find_column_by_pattern, compare_dates, detect_column_type,
        get_all_comparable_columns
    )

    # Helper: when Excel has duplicate column names, df[col] can return a DataFrame.
    # This ensures we always work with a Series for per-cell string ops.
    def get_column_series(df, col_name):
        if col_name is None or not isinstance(df, pd.DataFrame) or col_name not in df.columns:
            return pd.Series([], dtype="object")
        col = df[col_name]
        if isinstance(col, pd.DataFrame):
            # Take the first occurrence when duplicate column labels exist
            return col.iloc[:, 0]
        return col

    # Helper: safely get a scalar from a row even if duplicate labels yield a Series
    def get_row_value(row, col_name):
        try:
            val = row.get(col_name, None)
        except Exception:
            val = None
        if isinstance(val, pd.Series):
            return val.iloc[0] if len(val) > 0 else None
        return val
    
    # Helper: parse price value, handling currency symbols, commas, etc.
    def parse_price(value):
        """Parse price value, handling various formats"""
        if value is None:
            return None
        if isinstance(value, pd.Series):
            if len(value) == 0:
                return None
            value = value.iloc[0]
        if pd.isna(value):
            return None
        
        # Convert to string and clean
        price_str = str(value).strip()
        if not price_str or price_str.lower() in ['nan', 'none', '']:
            return None
        
        # Remove currency symbols and commas
        price_str = price_str.replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('₹', '').replace('¥', '')
        price_str = price_str.strip()
        
        # Try to convert to float
        try:
            return float(price_str)
        except (ValueError, TypeError):
            return None
    
    # Helper: calculate similarity between two strings (simple ratio)
    def string_similarity(str1, str2):
        """Calculate simple similarity ratio between two strings"""
        if not str1 or not str2:
            return 0.0
        str1 = str(str1).lower().strip()
        str2 = str(str2).lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Calculate common characters
        set1 = set(str1)
        set2 = set(str2)
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        # Jaccard similarity
        jaccard = intersection / union
        
        # Also check if one string contains the other
        if str1 in str2 or str2 in str1:
            jaccard = max(jaccard, 0.7)
        
        # Check word overlap
        words1 = set(str1.split())
        words2 = set(str2.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / max(len(words1), len(words2))
            jaccard = max(jaccard, word_overlap * 0.8)
        
        return jaccard
    
    # Helper: find similar items using fuzzy matching
    def find_similar_item(target_item, item_series, threshold=0.6):
        """Find items similar to target_item in the series"""
        if not target_item or item_series.empty:
            return None, 0.0
        
        target_lower = str(target_item).lower().strip()
        best_match = None
        best_similarity = 0.0
        
        for idx, po_item in item_series.items():
            similarity = string_similarity(target_lower, str(po_item))
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = idx
        
        return best_match, best_similarity
    
    mismatches = []
    duplicates = []
    anomalies = []
    debug_info = []
    
    if not isinstance(invoice_data, pd.DataFrame) or not isinstance(po_data, pd.DataFrame):
        return {
            'mismatches': mismatches,
            'duplicates': duplicates,
            'anomalies': anomalies,
            'summary': {
                'total_mismatches': 0,
                'total_duplicates': 0,
                'total_anomalies': 0
            }
        }
    
    invoice_df = invoice_data.copy()
    po_df = po_data.copy()
    
    # Dynamically find all comparable columns
    comparable_cols = get_all_comparable_columns(invoice_df, po_df)
    
    # Get item columns (for matching rows)
    invoice_item_col = comparable_cols.get('item', {}).get('invoice')
    po_item_col = comparable_cols.get('item', {}).get('po')
    
    # Get other columns
    invoice_price_col = comparable_cols.get('unit_price', {}).get('invoice')
    po_price_col = comparable_cols.get('unit_price', {}).get('po')
    
    # Debug: Log detected columns
    debug_info.append(f"Detected columns - Invoice Item: {invoice_item_col}, PO Item: {po_item_col}")
    debug_info.append(f"Detected columns - Invoice Price: {invoice_price_col}, PO Price: {po_price_col}")
    
    # If price columns not found, try alternative detection
    if not invoice_price_col or not po_price_col:
        # Try more patterns for price detection
        price_patterns = [r'unit\s*price', r'price', r'rate', r'cost', r'unit\s*cost', r'amount', r'unit\s*rate']
        if not invoice_price_col:
            invoice_price_col = find_column_by_pattern(invoice_df, price_patterns)
        if not po_price_col:
            po_price_col = find_column_by_pattern(po_df, price_patterns)
        if invoice_price_col or po_price_col:
            debug_info.append(f"Alternative detection - Invoice Price: {invoice_price_col}, PO Price: {po_price_col}")
    
    invoice_qty_col = comparable_cols.get('quantity', {}).get('invoice')
    po_qty_col = comparable_cols.get('quantity', {}).get('po')
    
    invoice_date_col = comparable_cols.get('date', {}).get('invoice')
    po_date_col = comparable_cols.get('date', {}).get('po')
    
    # Check for duplicates
    if invoice_item_col:
        invoice_items_series = get_column_series(invoice_df, invoice_item_col)
        valid_items = invoice_items_series.dropna()
        valid_items = valid_items[valid_items.astype(str).str.strip() != '']
        item_counts = valid_items.value_counts()
        
        for item, count in item_counts.items():
            if count > 1:
                duplicates.append({
                    'type': 'Duplicate Item',
                    'item': str(item),
                    'occurrences': int(count),
                    'description': f'Item "{item}" appears {count} times in invoice',
                    'severity': 'Medium'
                })
    
    # Compare items
    if invoice_item_col and po_item_col:
        # Get normalized item series (don't assign back to avoid issues with duplicate columns)
        invoice_item_series = get_column_series(invoice_df, invoice_item_col).fillna('').astype(str)
        po_item_series_normalized = get_column_series(po_df, po_item_col).fillna('').astype(str)
        
        for row_pos, (idx, inv_row) in enumerate(invoice_df.iterrows()):
            # Get item from the normalized series instead of the row (use .loc for label-based indexing)
            if idx in invoice_item_series.index:
                item = str(invoice_item_series.loc[idx] or '').strip()
            else:
                item = str(get_row_value(inv_row, invoice_item_col) or '').strip()
            
            if not item or item.lower() == 'nan' or item == '':
                continue
            
            # Use the normalized series for comparison
            po_matches = po_df[po_item_series_normalized.str.strip().str.lower() == item.lower()]
            
            if po_matches.empty:
                # Try fuzzy matching to find similar items
                similar_idx, similarity = find_similar_item(item, po_item_series_normalized, threshold=0.5)
                
                if similar_idx is not None and similarity >= 0.5:
                    # Found a similar item - report as name mismatch with low severity
                    similar_item = po_item_series_normalized.loc[similar_idx]
                    # Report as mismatch (not just anomaly)
                    mismatches.append({
                        'type': 'Item Name Mismatch',
                        'item': item,
                        'invoice_value': item,
                        'po_value': str(similar_item),
                        'difference': f"Names differ (similarity: {similarity:.1%})",
                        'severity': 'Low',
                        'description': f'Item name mismatch: Invoice has "{item}" but PO has similar item "{similar_item}" (similarity: {similarity:.1%})'
                    })
                    # Use the similar item for price comparison
                    po_row = po_df.loc[similar_idx]
                else:
                    # No similar item found - report as item not in PO with low severity
                    anomalies.append({
                        'type': 'Item Not in PO',
                        'item': item,
                        'description': f'Item "{item}" found in invoice but not in purchase order',
                        'severity': 'Low'
                    })
                    # Even if item doesn't match, try to compare price by row position as fallback
                    po_row = None
                    if invoice_price_col and po_price_col and len(po_df) > 0:
                        try:
                            # Try comparing by row position (positional matching)
                            po_row_pos = min(row_pos, len(po_df) - 1)
                            po_row = po_df.iloc[po_row_pos]
                            
                            inv_price_val = get_row_value(inv_row, invoice_price_col)
                            po_price_val = get_row_value(po_row, po_price_col)
                            
                            inv_price = parse_price(inv_price_val)
                            po_price = parse_price(po_price_val)
                            
                            if inv_price is not None and po_price is not None:
                                diff = abs(float(inv_price) - float(po_price))
                                price_threshold = max(0.001, abs(po_price) * 0.001)
                                if diff > price_threshold:
                                    mismatches.append({
                                        'type': 'Rate Mismatch (Index-based)',
                                        'item': item,
                                        'invoice_value': f"{inv_price:.2f}",
                                        'po_value': f"{po_price:.2f}",
                                        'difference': f"{diff:.2f}",
                                        'severity': 'Medium',
                                        'description': f'Unit price mismatch (by row position): Invoice={inv_price:.2f}, PO={po_price:.2f}'
                                    })
                        except Exception:
                            pass
            else:
                po_row = po_matches.iloc[0]
            
            # Always compare item names and report mismatches
            if po_row is not None and invoice_item_col and po_item_col:
                try:
                    po_item_name = str(get_row_value(po_row, po_item_col) or '').strip()
                    inv_item_name = str(item).strip()
                    
                    # Compare item names (case-sensitive comparison)
                    if inv_item_name and po_item_name and inv_item_name != po_item_name:
                        # Check if they're similar (fuzzy match)
                        similarity = string_similarity(inv_item_name, po_item_name)
                        
                        if similarity < 1.0:  # Names are different
                            # Report as mismatch
                            mismatches.append({
                                'type': 'Item Name Mismatch',
                                'item': inv_item_name,
                                'invoice_value': inv_item_name,
                                'po_value': po_item_name,
                                'difference': f"Names differ (similarity: {similarity:.1%})",
                                'severity': 'Low',
                                'description': f'Item name mismatch: Invoice has "{inv_item_name}" but PO has "{po_item_name}"'
                            })
                except Exception as e:
                    debug_info.append(f"Item name comparison error: {str(e)}")
            
            # Compare price/rate (for both matched and similar items)
            if po_row is not None and invoice_price_col and po_price_col:
                try:
                    inv_price_val = get_row_value(inv_row, invoice_price_col)
                    po_price_val = get_row_value(po_row, po_price_col)
                    
                    inv_price = parse_price(inv_price_val)
                    po_price = parse_price(po_price_val)
                    
                    if inv_price is not None and po_price is not None:
                        diff = abs(float(inv_price) - float(po_price))
                        # Use a more lenient threshold: any difference > 0.001 or > 0.1% of the price
                        price_threshold = max(0.001, abs(po_price) * 0.001)
                        if diff > price_threshold:
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
                except (ValueError, TypeError) as e:
                    # Log the error for debugging but continue
                    debug_info.append(f"Price comparison error for item {item}: {str(e)}")
                    pass
            
            # Compare quantity (for both matched and similar items)
            if po_row is not None and invoice_qty_col and po_qty_col:
                try:
                    inv_qty = pd.to_numeric(get_row_value(inv_row, invoice_qty_col) if invoice_qty_col else 0, errors='coerce')
                    po_qty = pd.to_numeric(get_row_value(po_row, po_qty_col) if po_qty_col else 0, errors='coerce')
                    
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
                except (ValueError, TypeError):
                    pass
            
            # Compare dates (for both matched and similar items)
            if po_row is not None and invoice_date_col and po_date_col:
                try:
                    inv_date = get_row_value(inv_row, invoice_date_col) if invoice_date_col in inv_row.index else None
                    po_date = get_row_value(po_row, po_date_col) if po_date_col in po_row.index else None
                    
                    # Ensure we get scalar values, not Series
                    if isinstance(inv_date, pd.Series):
                        inv_date = inv_date.iloc[0] if len(inv_date) > 0 else None
                    if isinstance(po_date, pd.Series):
                        po_date = po_date.iloc[0] if len(po_date) > 0 else None
                    
                    if inv_date is not None and po_date is not None:
                        date_diff = compare_dates(inv_date, po_date, tolerance_days=0)
                        if date_diff:
                            mismatches.append({
                                'type': 'Date Mismatch',
                                'item': item,
                                'invoice_value': date_diff['invoice_date'],
                                'po_value': date_diff['po_date'],
                                'difference': f"{date_diff['difference_days']} days",
                                'severity': 'Medium' if date_diff['difference_days'] <= 30 else 'High',
                                'description': f'Date mismatch: Invoice={date_diff["invoice_date"]}, PO={date_diff["po_date"]} (diff: {date_diff["difference_days"]} days)'
                            })
                except Exception as e:
                    # Skip date comparison if there's an error
                    pass
        
        # Use the normalized series we already created
        invoice_items = set(invoice_item_series.str.strip())
        for idx, po_row in po_df.iterrows():
            # Get item from the normalized series instead of the row (use .loc for label-based indexing)
            if idx in po_item_series_normalized.index:
                item = str(po_item_series_normalized.loc[idx] or '').strip()
            else:
                item = str(get_row_value(po_row, po_item_col) or '').strip()
            if item and item != 'nan' and item not in invoice_items:
                # Try fuzzy matching to find similar items
                similar_found = False
                if invoice_item_col:
                    invoice_item_series_check = get_column_series(invoice_df, invoice_item_col).fillna('').astype(str)
                    similar_idx, similarity = find_similar_item(item, invoice_item_series_check, threshold=0.5)
                    if similar_idx is not None and similarity >= 0.5:
                        similar_item = invoice_item_series_check.loc[similar_idx]
                        # Report as mismatch (not just anomaly)
                        mismatches.append({
                            'type': 'Item Name Mismatch',
                            'item': item,
                            'invoice_value': str(similar_item),
                            'po_value': item,
                            'difference': f"Names differ (similarity: {similarity:.1%})",
                            'severity': 'Low',
                            'description': f'Item name mismatch: PO has "{item}" but invoice has similar item "{similar_item}" (similarity: {similarity:.1%})'
                        })
                        similar_found = True
                
                if not similar_found:
                    anomalies.append({
                        'type': 'Item Missing in Invoice',
                        'item': item,
                        'description': f'Item "{item}" in PO but not found in invoice',
                        'severity': 'Low'
                    })
    
    # Additional comparison: Compare all rows by position if item columns exist
    # This catches item name and price mismatches even when item matching fails
    if invoice_item_col and po_item_col and len(invoice_df) > 0 and len(po_df) > 0:
        max_rows = min(len(invoice_df), len(po_df))
        for row_pos in range(max_rows):
            try:
                inv_row = invoice_df.iloc[row_pos]
                po_row = po_df.iloc[row_pos]
                
                # Compare item names by position
                inv_item_name = str(get_row_value(inv_row, invoice_item_col) or '').strip()
                po_item_name = str(get_row_value(po_row, po_item_col) or '').strip()
                
                if inv_item_name and po_item_name and inv_item_name.lower() != po_item_name.lower():
                    # Item names differ - report as mismatch
                    similarity = string_similarity(inv_item_name, po_item_name)
                    
                    # Check if this mismatch was already reported
                    existing_name_mismatch = any(
                        m.get('type') == 'Item Name Mismatch' and
                        (m.get('invoice_value') == inv_item_name or m.get('item') == inv_item_name)
                        for m in mismatches
                    )
                    
                    if not existing_name_mismatch:
                        mismatches.append({
                            'type': 'Item Name Mismatch',
                            'item': inv_item_name,
                            'invoice_value': inv_item_name,
                            'po_value': po_item_name,
                            'difference': f"Names differ (similarity: {similarity:.1%})",
                            'severity': 'Low',
                            'description': f'Item name mismatch (row {row_pos + 1}): Invoice has "{inv_item_name}" but PO has "{po_item_name}"'
                        })
                
                # Compare prices by position
                if invoice_price_col and po_price_col:
                    inv_price_val = get_row_value(inv_row, invoice_price_col)
                    po_price_val = get_row_value(po_row, po_price_col)
                    
                    inv_price = parse_price(inv_price_val)
                    po_price = parse_price(po_price_val)
                    
                    if inv_price is not None and po_price is not None:
                        diff = abs(float(inv_price) - float(po_price))
                        price_threshold = max(0.001, abs(po_price) * 0.001)
                        if diff > price_threshold:
                            # Check if this mismatch was already reported
                            item_name = inv_item_name if inv_item_name else "Row " + str(row_pos + 1)
                            
                            # Only add if not already in mismatches (avoid duplicates)
                            existing = any(
                                m.get('item') == item_name and 
                                m.get('type') == 'Rate Mismatch' and
                                abs(float(m.get('invoice_value', 0).replace(',', '')) - inv_price) < 0.01
                                for m in mismatches
                            )
                            if not existing:
                                severity = 'High' if diff > abs(po_price) * 0.1 else 'Medium'
                                mismatches.append({
                                    'type': 'Rate Mismatch',
                                    'item': item_name,
                                    'invoice_value': f"{inv_price:.2f}",
                                    'po_value': f"{po_price:.2f}",
                                    'difference': f"{diff:.2f}",
                                    'severity': severity,
                                    'description': f'Unit price mismatch: Invoice={inv_price:.2f}, PO={po_price:.2f}'
                                })
            except Exception:
                pass
    
    return {
        'mismatches': mismatches,
        'duplicates': duplicates,
        'anomalies': anomalies,
        'summary': {
            'total_mismatches': len(mismatches),
            'total_duplicates': len(duplicates),
            'total_anomalies': len(anomalies)
        }
    }

def upload_tab():
    """Upload documents tab with professional UI"""
    st.markdown('<h2 class="section-header">Upload Documents</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; margin-bottom: 1.5rem;">Upload your invoice and purchase order files for comparison analysis</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### Configuration")
        st.markdown("---")
        api_key = st.text_input(
            "OpenAI API Key (Optional)",
            type="password",
            help="Enter your OpenAI API key to enable AI-powered analysis",
            placeholder="sk-..."
        )
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("API Key configured")
        else:
            st.info("Rule-based comparison will be used without API key")
        st.markdown("---")
        st.markdown("### Supported Formats")
        st.markdown("- **Excel:** .xlsx, .xls")
        st.markdown("- **PDF:** .pdf (text-based)")
    
    # Upload section with cards
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Invoice File")
        st.markdown('<p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Upload your invoice document</p>', unsafe_allow_html=True)
        invoice_file = st.file_uploader(
            "Choose Invoice File",
            type=['xlsx', 'xls', 'pdf'],
            key="invoice",
            label_visibility="collapsed"
        )
        if invoice_file:
            st.success(f"{invoice_file.name} uploaded")
            st.caption(f"Size: {invoice_file.size / 1024:.2f} KB")
    
    with col2:
        st.markdown("### Purchase Order File")
        st.markdown('<p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Upload your purchase order document</p>', unsafe_allow_html=True)
        po_file = st.file_uploader(
            "Choose PO File",
            type=['xlsx', 'xls', 'pdf'],
            key="po",
            label_visibility="collapsed"
        )
        if po_file:
            st.success(f"{po_file.name} uploaded")
            st.caption(f"Size: {po_file.size / 1024:.2f} KB")
    
    st.markdown("---")
    
    upload_name = st.text_input(
        "Reference Name",
        placeholder="e.g., Q4-2024 Invoice Review, Vendor ABC Analysis, etc.",
        help="Give this upload a descriptive name so you can easily find it later in your history",
        key="upload_name"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if invoice_file and po_file:
        if not upload_name:
            st.warning("Please enter a reference name for this upload")
        
        if st.button("Analyze & Compare", type="primary", width='stretch'):
            if not upload_name:
                st.error("Please enter a reference name")
            else:
                with st.spinner("Processing files and analyzing..."):
                    try:
                        # Parse files
                        parser = FileParser()
                        invoice_data = parser.parse_file(invoice_file)
                        po_data = parser.parse_file(po_file)
                        
                        # Save files
                        upload_id = db.save_file_upload(
                            st.session_state.user['id'],
                            upload_name,
                            invoice_file.name,
                            po_file.name,
                            "",  # Will be set after saving
                            ""
                        )
                        
                        # Save files to storage
                        invoice_path = storage.save_file(invoice_file, st.session_state.user['id'], upload_id, "invoice")
                        po_path = storage.save_file(po_file, st.session_state.user['id'], upload_id, "po")
                        
                        st.session_state.invoice_data = invoice_data
                        st.session_state.po_data = po_data
                        st.session_state.current_upload_id = upload_id
                        
                        # Run comparison
                        if api_key:
                            try:
                                agent = InvoiceQAAgent(api_key)
                                comparison_results = agent.compare_invoice_po(invoice_data, po_data)
                            except Exception as e:
                                st.warning(f"AI comparison failed: {str(e)}. Using rule-based comparison.")
                                comparison_results = compare_basic(invoice_data, po_data)
                        else:
                            comparison_results = compare_basic(invoice_data, po_data)
                        
                        # Save results to database
                        results_json = json.dumps(comparison_results)
                        db.save_comparison_result(
                            upload_id,
                            comparison_results['summary']['total_mismatches'],
                            comparison_results['summary']['total_duplicates'],
                            comparison_results['summary']['total_anomalies'],
                            results_json
                        )
                        
                        st.session_state.comparison_results = comparison_results
                        st.success("Analysis complete! Check the Results tab.")
                        
                    except Exception as e:
                        st.error(f"Error processing files: {str(e)}")
                        st.exception(e)

def results_tab():
    """View current results tab with professional UI"""
    st.markdown('<h2 class="section-header">Analysis Results</h2>', unsafe_allow_html=True)
    
    if st.session_state.comparison_results:
        results = st.session_state.comparison_results
        display_results(results, show_download=True)
    else:
        st.info("""
        **No results available yet.**
        
        Please go to the **Upload** tab to:
        1. Upload your invoice and PO files
        2. Enter a reference name
        3. Click "Analyze & Compare"
        
        Your results will appear here once the analysis is complete.
        """)

def display_results(results, show_download=True):
    """Display comparison results with professional card-based UI"""
    # Summary metrics with professional cards
    st.markdown("### Summary Overview")
    st.markdown("")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_issues = sum([
        results['summary']['total_mismatches'],
        results['summary']['total_duplicates'],
        results['summary']['total_anomalies']
    ])
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #dc2626;">
            <div class="metric-card-title">Mismatches</div>
            <div class="metric-card-value" style="color: #dc2626;">{}</div>
        </div>
        """.format(results['summary']['total_mismatches']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #2563eb;">
            <div class="metric-card-title">Duplicates</div>
            <div class="metric-card-value" style="color: #2563eb;">{}</div>
        </div>
        """.format(results['summary']['total_duplicates']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #f59e0b;">
            <div class="metric-card-title">Anomalies</div>
            <div class="metric-card-value" style="color: #f59e0b;">{}</div>
        </div>
        """.format(results['summary']['total_anomalies']), unsafe_allow_html=True)
    
    with col4:
        status_color = "#dc2626" if total_issues > 0 else "#10b981"
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid {};">
            <div class="metric-card-title">Total Issues</div>
            <div class="metric-card-value" style="color: {};">{}</div>
        </div>
        """.format(status_color, status_color, total_issues), unsafe_allow_html=True)
    
    st.markdown("")
    
    # Visualizations
    if total_issues > 0:
        st.markdown("### Visualizations")
        st.markdown("")
        fig = create_visualizations(results)
        st.plotly_chart(fig, width='stretch')
        st.markdown("")
    
    # Detailed results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Mismatches", "Duplicates", "Anomalies", "Full Report"])
    
    with tab1:
        if results['mismatches']:
            df_mismatches = pd.DataFrame(results['mismatches'])
            st.dataframe(df_mismatches, width='stretch', hide_index=True)
        else:
            st.success("No mismatches found")
    
    with tab2:
        if results['duplicates']:
            df_duplicates = pd.DataFrame(results['duplicates'])
            st.dataframe(df_duplicates, width='stretch', hide_index=True)
        else:
            st.success("No duplicates found")
    
    with tab3:
        if results['anomalies']:
            df_anomalies = pd.DataFrame(results['anomalies'])
            st.dataframe(df_anomalies, width='stretch', hide_index=True)
        else:
            st.success("No anomalies detected")
    
    with tab4:
        st.json(results)
    
    # Download section
    if show_download:
        st.markdown("### Download Results")
        st.markdown("")
        output_gen = OutputGenerator()
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                excel_buffer = output_gen.generate_excel(results, st.session_state.invoice_data, st.session_state.po_data)
                st.download_button(
                    label="Download Excel Report",
                    data=excel_buffer,
                    file_name="invoice_qa_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
            except Exception as e:
                st.error(f"Error generating Excel: {str(e)}")
        
        with col2:
            try:
                pdf_buffer = output_gen.generate_pdf(results, st.session_state.invoice_data, st.session_state.po_data)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name="invoice_qa_report.pdf",
                    mime="application/pdf",
                    width='stretch'
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

def collective_results_tab():
    """Collective results across all uploads with professional UI"""
    st.markdown('<h2 class="section-header">Collective Results</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; margin-bottom: 1.5rem;">Aggregated statistics across all your invoice comparisons</p>', unsafe_allow_html=True)
    
    collective = db.get_collective_results(st.session_state.user['id'])
    
    if collective['total_comparisons'] == 0:
        st.info("""
        **No comparisons found yet.**
        
        Start uploading and analyzing files to see collective statistics here.
        """)
        return
    
    # Summary metrics with professional cards
    st.markdown("### Overall Statistics")
    st.markdown("")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_mismatches = collective['total_mismatches'] / collective['total_comparisons'] if collective['total_comparisons'] > 0 else 0
    avg_duplicates = collective['total_duplicates'] / collective['total_comparisons'] if collective['total_comparisons'] > 0 else 0
    avg_anomalies = collective['total_anomalies'] / collective['total_comparisons'] if collective['total_comparisons'] > 0 else 0
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #1e3a8a;">
            <div class="metric-card-title">Total Comparisons</div>
            <div class="metric-card-value" style="color: #1e3a8a;">{}</div>
        </div>
        """.format(collective['total_comparisons']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #dc2626;">
            <div class="metric-card-title">Total Mismatches</div>
            <div class="metric-card-value" style="color: #dc2626;">{}</div>
            <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">Avg: {:.1f} per comparison</div>
        </div>
        """.format(collective['total_mismatches'], avg_mismatches), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #2563eb;">
            <div class="metric-card-title">Total Duplicates</div>
            <div class="metric-card-value" style="color: #2563eb;">{}</div>
            <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">Avg: {:.1f} per comparison</div>
        </div>
        """.format(collective['total_duplicates'], avg_duplicates), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="border-left: 4px solid #f59e0b;">
            <div class="metric-card-title">Total Anomalies</div>
            <div class="metric-card-value" style="color: #f59e0b;">{}</div>
            <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">Avg: {:.1f} per comparison</div>
        </div>
        """.format(collective['total_anomalies'], avg_anomalies), unsafe_allow_html=True)
    
    st.markdown("")
    
    # Create collective visualization
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Issue Distribution', 'Average Issues per Comparison'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Pie chart
    fig.add_trace(
        go.Pie(
            labels=['Mismatches', 'Duplicates', 'Anomalies'],
            values=[collective['total_mismatches'], collective['total_duplicates'], collective['total_anomalies']],
            name='Issues'
        ),
        row=1, col=1
    )
    
    # Bar chart
    avg_mismatches = collective['total_mismatches'] / collective['total_comparisons']
    avg_duplicates = collective['total_duplicates'] / collective['total_comparisons']
    avg_anomalies = collective['total_anomalies'] / collective['total_comparisons']
    
    fig.add_trace(
        go.Bar(
            x=['Mismatches', 'Duplicates', 'Anomalies'],
            y=[avg_mismatches, avg_duplicates, avg_anomalies],
            name='Average',
            marker_color=['#FF6B6B', '#4ECDC4', '#FFE66D']
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False, title_text="Collective Analysis Overview")
    st.plotly_chart(fig, width='stretch')
    
    # Get all uploads for detailed view
    uploads = db.get_user_uploads(st.session_state.user['id'])
    if uploads:
        st.subheader("📋 All Uploads Summary")
        uploads_df = pd.DataFrame(uploads, columns=[
            'ID', 'Reference Name', 'Invoice File', 'PO File', 'Upload Date',
            'Mismatches', 'Duplicates', 'Anomalies'
        ])
        st.dataframe(uploads_df, width='stretch', hide_index=True)

def history_tab():
    """View upload history with professional UI"""
    st.markdown('<h2 class="section-header">Upload History</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; margin-bottom: 1.5rem;">View and manage all your previous invoice comparisons</p>', unsafe_allow_html=True)
    
    uploads = db.get_user_uploads(st.session_state.user['id'])
    
    if not uploads:
        st.info("""
        **No uploads found yet.**
        
        Start by uploading files in the **Upload** tab. All your analyses will be saved here for future reference.
        """)
        return
    
    st.markdown(f"### Your Uploads ({len(uploads)} total)")
    st.markdown("")
    
    # Display as professional cards
    for idx, upload in enumerate(uploads):
        upload_id, upload_name, invoice_file, po_file, upload_date, mismatches, duplicates, anomalies = upload
        
        # Create a professional card
        with st.container():
            st.markdown(f"""
            <div class="info-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h4 style="margin: 0; color: #1f2937; font-weight: 600;">{upload_name}</h4>
                        <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.875rem;">{upload_date[:19] if upload_date else 'N/A'}</p>
                        <p style="margin: 0.5rem 0 0 0; color: #9ca3af; font-size: 0.8rem;">Invoice: {invoice_file} | PO: {po_file}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                pass  # Spacer
            
            with col2:
                st.metric("Mismatches", mismatches or 0, help="Mismatches found")
            
            with col3:
                st.metric("Duplicates", duplicates or 0, help="Duplicates found")
            
            with col4:
                st.metric("Anomalies", anomalies or 0, help="Anomalies found")
            
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("View Details", key=f"view_{upload_id}", width='stretch'):
                    result_json = db.get_upload_result(upload_id)
                    if result_json:
                        try:
                            result = json.loads(result_json)
                            st.session_state.comparison_results = result
                            
                            # Try to load the original invoice and PO data if files exist
                            try:
                                conn = db.get_connection()
                                cursor = conn.cursor()
                                cursor.execute('''
                                    SELECT invoice_path, po_path 
                                    FROM file_uploads 
                                    WHERE id = ?
                                ''', (upload_id,))
                                file_paths = cursor.fetchone()
                                conn.close()
                                
                                if file_paths:
                                    invoice_path, po_path = file_paths
                                    parser = FileParser()
                                    
                                    # Load invoice data
                                    if invoice_path and os.path.exists(invoice_path):
                                        try:
                                            from io import BytesIO
                                            with open(invoice_path, 'rb') as f:
                                                file_content = f.read()
                                            # Create a file-like object
                                            class FileObj:
                                                def __init__(self, name, content):
                                                    self.name = name
                                                    self._content = content
                                                    self._pos = 0
                                                def read(self):
                                                    return self._content
                                                def seek(self, pos):
                                                    self._pos = pos
                                            
                                            invoice_file_obj = FileObj(os.path.basename(invoice_path), file_content)
                                            st.session_state.invoice_data = parser.parse_file(invoice_file_obj)
                                        except Exception:
                                            pass
                                    
                                    # Load PO data
                                    if po_path and os.path.exists(po_path):
                                        try:
                                            from io import BytesIO
                                            with open(po_path, 'rb') as f:
                                                file_content = f.read()
                                            # Create a file-like object
                                            class FileObj:
                                                def __init__(self, name, content):
                                                    self.name = name
                                                    self._content = content
                                                    self._pos = 0
                                                def read(self):
                                                    return self._content
                                                def seek(self, pos):
                                                    self._pos = pos
                                            
                                            po_file_obj = FileObj(os.path.basename(po_path), file_content)
                                            st.session_state.po_data = parser.parse_file(po_file_obj)
                                        except Exception:
                                            pass
                            except Exception as e:
                                # If file loading fails, continue without it
                                pass
                            
                            # Set flag to switch to Results tab
                            st.session_state.switch_to_results = True
                            st.success("Results loaded successfully! Switching to Results tab...")
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"Error parsing results: {str(e)}")
                    else:
                        st.warning("No results found for this upload.")
            
            if idx < len(uploads) - 1:
                st.markdown("---")

def main():
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Main application
    st.markdown('<h1 class="main-header">Invoice QA Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown("### User Profile")
        st.markdown("---")
        st.markdown(f"""
        <div style="background: #ffffff; 
                    padding: 1.25rem; border-radius: 8px; border: 1px solid #e5e7eb; text-align: center;">
            <h3 style="margin: 0; color: #1f2937; font-weight: 600;">{st.session_state.user['username']}</h3>
            {f'<p style="font-size: 0.875rem; color: #6b7280; margin: 0.5rem 0 0 0;">{st.session_state.user["email"]}</p>' if st.session_state.user.get('email') else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Logout", width='stretch', type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        collective = db.get_collective_results(st.session_state.user['id'])
        st.metric("Total Comparisons", collective['total_comparisons'] or 0)
        st.metric("Total Issues Found", 
                 (collective['total_mismatches'] or 0) + 
                 (collective['total_duplicates'] or 0) + 
                 (collective['total_anomalies'] or 0))
    
    # Tab options (single source of truth)
    tab_options = ["Upload", "Results", "Collective", "History"]

    # Check if we need to switch to Results tab
    if st.session_state.get('switch_to_results', False):
        # Force selection to Results tab
        if 'selected_tab' not in st.session_state or st.session_state.selected_tab != "Results":
            st.session_state.selected_tab = "Results"
        st.session_state.switch_to_results = False
        default_index = 1  # Results tab is index 1
    else:
        # Use stored selection or default
        if 'selected_tab' in st.session_state:
            default_index = tab_options.index(st.session_state.selected_tab) if st.session_state.selected_tab in tab_options else 0
        else:
            default_index = 0
    
    # Professional Tab menu
    selected = option_menu(
        menu_title=None,
        options=tab_options,
        icons=["upload", "graph-up", "bar-chart", "clock-history"],
        menu_icon=None,
        default_index=default_index,
        orientation="horizontal",
        key="main_nav",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#ffffff",
                "border-radius": "8px",
                "margin-bottom": "2rem",
                "border": "1px solid #e5e7eb"
            },
            "icon": {"color": "#2563eb", "font-size": "18px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "center",
                "margin": "0px",
                "padding": "1rem 1.5rem",
                "--hover-color": "#f3f4f6",
                "border-radius": "6px",
                "font-weight": "500",
                "color": "#6b7280"
            },
            "nav-link-selected": {
                "background-color": "#2563eb",
                "color": "white",
                "font-weight": "600"
            },
        }
    )
    
    # Store selected tab in session state
    if selected != st.session_state.get("selected_tab"):
        st.session_state.selected_tab = selected
    
    # Route to appropriate tab
    if selected == "Upload":
        upload_tab()
    elif selected == "Results":
        results_tab()
    elif selected == "Collective":
        collective_results_tab()
    elif selected == "History":
        history_tab()

if __name__ == "__main__":
    main()

