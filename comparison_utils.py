"""
Dynamic comparison utilities for invoice and PO matching
Handles date mismatches and flexible column detection
"""

import pandas as pd
import re
from datetime import datetime
from dateutil import parser as date_parser

def find_column_by_pattern(df, patterns):
    """Dynamically find column by matching patterns"""
    if not isinstance(df, pd.DataFrame):
        return None
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        for pattern in patterns:
            if re.search(pattern, col_lower, re.IGNORECASE):
                return col
    return None

def parse_date(date_value):
    """Parse date from various formats"""
    # Handle pandas Series - take first value
    if isinstance(date_value, pd.Series):
        if len(date_value) == 0:
            return None
        date_value = date_value.iloc[0]
    
    # Handle None, empty string, or NaN
    if date_value is None:
        return None
    
    if isinstance(date_value, str) and date_value.strip() == '':
        return None
    
    try:
        if pd.isna(date_value):
            return None
    except (TypeError, ValueError):
        # If pd.isna fails, continue
        pass
    
    # If already a datetime object
    if isinstance(date_value, (datetime, pd.Timestamp)):
        return date_value
    
    # Convert to string for parsing
    date_str = str(date_value).strip()
    if not date_str or date_str.lower() in ['nan', 'none', '']:
        return None
    
    # Try pandas to_datetime first
    try:
        parsed = pd.to_datetime(date_str, errors='coerce')
        if pd.notna(parsed):
            # Convert to datetime if it's a Timestamp
            if isinstance(parsed, pd.Timestamp):
                return parsed.to_pydatetime()
            return parsed
    except:
        pass
    
    # Try dateutil parser
    try:
        parsed = date_parser.parse(date_str, fuzzy=True)
        return parsed
    except:
        pass
    
    # Try common date formats
    date_formats = [
        '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
        '%d-%m-%Y', '%m-%d-%Y', '%Y.%m.%d', '%d.%m.%Y',
        '%B %d, %Y', '%d %B %Y', '%b %d, %Y', '%d %b %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None

def compare_dates(inv_date, po_date, tolerance_days=0):
    """Compare two dates and return mismatch info if different"""
    inv_parsed = parse_date(inv_date)
    po_parsed = parse_date(po_date)
    
    if inv_parsed is None or po_parsed is None:
        return None
    
    # Calculate difference
    diff = abs((inv_parsed - po_parsed).days)
    
    if diff > tolerance_days:
        return {
            'invoice_date': inv_parsed.strftime('%Y-%m-%d'),
            'po_date': po_parsed.strftime('%Y-%m-%d'),
            'difference_days': diff
        }
    
    return None

def detect_column_type(df, col_name):
    """Detect the type of data in a column"""
    if col_name not in df.columns:
        return 'unknown'
    
    sample = df[col_name].dropna().head(10)
    if len(sample) == 0:
        return 'empty'
    
    # Check if it's numeric
    numeric_count = 0
    date_count = 0
    
    for val in sample:
        val_str = str(val).strip()
        
        # Check numeric
        try:
            float(val_str.replace(',', '').replace('$', '').replace('€', '').replace('£', ''))
            numeric_count += 1
        except:
            pass
        
        # Check date
        if parse_date(val) is not None:
            date_count += 1
    
    if date_count > len(sample) * 0.7:
        return 'date'
    elif numeric_count > len(sample) * 0.7:
        return 'numeric'
    else:
        return 'text'

def get_all_comparable_columns(invoice_df, po_df):
    """Get all columns that can be compared between invoice and PO"""
    comparable = {}
    
    # Standard column mappings
    column_types = {
        'item': [r'item', r'product', r'sku', r'part\s*number', r'code'],
        'description': [r'description', r'desc', r'name', r'details'],
        'quantity': [r'quantity', r'qty', r'amount'],
        'unit_price': [r'unit\s*price', r'unit\s*cost', r'unit\s*rate', r'price', r'rate', r'cost', r'unit\s*amount', r'price\s*per\s*unit'],
        'total': [r'total', r'line\s*total', r'amount'],
        'date': [r'date', r'invoice\s*date', r'po\s*date', r'order\s*date']
    }
    
    for col_type, patterns in column_types.items():
        inv_col = find_column_by_pattern(invoice_df, patterns)
        po_col = find_column_by_pattern(po_df, patterns)
        
        if inv_col and po_col:
            comparable[col_type] = {
                'invoice': inv_col,
                'po': po_col
            }
    
    return comparable

