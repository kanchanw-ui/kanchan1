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
        """Standardize column names to common formats"""
        column_mapping = {
            # Item/Product columns
            'item': 'Item',
            'item_no': 'Item',
            'item_number': 'Item',
            'product': 'Item',
            'product_code': 'Item',
            'sku': 'Item',
            
            # Description columns
            'description': 'Description',
            'desc': 'Description',
            'product_description': 'Description',
            'item_description': 'Description',
            
            # Quantity columns
            'quantity': 'Quantity',
            'qty': 'Quantity',
            'qty.': 'Quantity',
            'amount': 'Quantity',
            
            # Price columns
            'unit_price': 'Unit Price',
            'price': 'Unit Price',
            'rate': 'Unit Price',
            'unit cost': 'Unit Price',
            'cost': 'Unit Price',
            
            # Total columns
            'total': 'Total',
            'total_price': 'Total',
            'amount': 'Total',
            'line_total': 'Total',
        }
        
        # Create a copy
        df_standardized = df.copy()
        
        # Map columns (case-insensitive)
        for old_col in df.columns:
            old_col_lower = old_col.lower().strip()
            if old_col_lower in column_mapping:
                df_standardized = df_standardized.rename(columns={old_col: column_mapping[old_col_lower]})
        
        return df_standardized

