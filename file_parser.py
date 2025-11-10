import pandas as pd
import pdfplumber
import PyPDF2
from io import BytesIO
import re

class FileParser:
    """Parse Excel and PDF files to extract invoice/PO data"""
    
    def parse_file(self, file):
        """Parse uploaded file (Excel or PDF)"""
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension in ['xlsx', 'xls']:
            return self.parse_excel(file)
        elif file_extension == 'pdf':
            return self.parse_pdf(file)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def parse_excel(self, file):
        """Parse Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Try to identify key columns
            df = self.standardize_columns(df)
            
            return df
        except Exception as e:
            raise Exception(f"Error parsing Excel file: {str(e)}")
    
    def parse_pdf(self, file):
        """Parse PDF file using pdfplumber and PyPDF2"""
        try:
            # Read PDF content
            file_bytes = file.read()
            file.seek(0)  # Reset file pointer
            
            # Try pdfplumber first (better for tables)
            text_content = ""
            table_data = []
            
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    # Extract text
                    text_content += page.extract_text() or ""
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            table_data.extend(table)
            
            # If we found tables, convert to DataFrame
            if table_data:
                # Use first row as header
                if len(table_data) > 1:
                    df = pd.DataFrame(table_data[1:], columns=table_data[0])
                    df = self.standardize_columns(df)
                    return df
            
            # If no tables, try to extract structured data from text
            df = self.extract_data_from_text(text_content)
            return df
            
        except Exception as e:
            raise Exception(f"Error parsing PDF file: {str(e)}")
    
    def extract_data_from_text(self, text):
        """Extract structured data from PDF text"""
        lines = text.split('\n')
        data = []
        
        # Look for patterns like item descriptions, quantities, prices
        item_pattern = re.compile(r'(\d+)\s+([A-Za-z0-9\s]+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)')
        
        for line in lines:
            match = item_pattern.search(line)
            if match:
                data.append({
                    'Item': match.group(1),
                    'Description': match.group(2).strip(),
                    'Quantity': match.group(3),
                    'Unit Price': match.group(4)
                })
        
        if data:
            df = pd.DataFrame(data)
            return df
        else:
            # Return a simple DataFrame with the text content
            return pd.DataFrame({'Content': [text]})
    
    def standardize_columns(self, df):
        """Dynamically standardize column names to common formats"""
        import re
        
        # Expanded column mapping with more variations
        column_patterns = {
            # Item/Product columns - more flexible matching
            'item': [
                r'item', r'item_no', r'item_number', r'item\s*code', r'item_code',
                r'product', r'product_code', r'product\s*id', r'product_id',
                r'sku', r'part\s*number', r'part_number', r'part\s*no', r'part_no',
                r'code', r'item\s*name', r'product\s*name'
            ],
            # Description columns
            'description': [
                r'description', r'desc', r'product_description', r'item_description',
                r'name', r'product\s*name', r'item\s*name', r'details', r'specification'
            ],
            # Quantity columns
            'quantity': [
                r'quantity', r'qty', r'qty\.', r'amount', r'qty\s*ordered', r'qty\s*shipped',
                r'quantity\s*ordered', r'quantity\s*shipped', r'qty\s*received'
            ],
            # Price columns
            'unit_price': [
                r'unit\s*price', r'unit_price', r'price', r'rate', r'unit\s*cost', r'cost',
                r'unit\s*rate', r'price\s*per\s*unit', r'unit\s*amount', r'unit\s*value'
            ],
            # Total columns
            'total': [
                r'total', r'total_price', r'total\s*amount', r'line_total', r'line\s*total',
                r'amount', r'subtotal', r'extended\s*price', r'extended\s*amount'
            ],
            # Date columns
            'date': [
                r'date', r'invoice\s*date', r'po\s*date', r'order\s*date', r'ship\s*date',
                r'delivery\s*date', r'due\s*date', r'issue\s*date', r'created\s*date',
                r'transaction\s*date', r'bill\s*date', r'invoice\s*date', r'purchase\s*date'
            ],
            # Additional common fields
            'vendor': [
                r'vendor', r'supplier', r'seller', r'provider', r'company', r'vendor\s*name'
            ],
            'invoice_number': [
                r'invoice\s*number', r'invoice\s*no', r'invoice_no', r'inv\s*number',
                r'inv\s*no', r'invoice\s*id', r'invoice_id', r'invoice\s*#', r'inv\s*#'
            ],
            'po_number': [
                r'po\s*number', r'po\s*no', r'po_no', r'purchase\s*order\s*number',
                r'purchase\s*order\s*no', r'po\s*id', r'po_id', r'po\s*#', r'p\.o\.\s*number'
            ]
        }
        
        # Create a copy
        df_standardized = df.copy()
        column_mapping = {}
        
        # Map columns using pattern matching (case-insensitive)
        for old_col in df.columns:
            old_col_lower = str(old_col).lower().strip()
            
            # Try to match against patterns
            matched = False
            for standard_name, patterns in column_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, old_col_lower, re.IGNORECASE):
                        column_mapping[old_col] = standard_name.replace('_', ' ').title()
                        matched = True
                        break
                if matched:
                    break
            
            # If no pattern match, keep original but clean it
            if not matched:
                # Clean column name but keep it
                cleaned = old_col.strip()
                column_mapping[old_col] = cleaned
        
        # Apply mapping
        df_standardized = df_standardized.rename(columns=column_mapping)
        
        return df_standardized

