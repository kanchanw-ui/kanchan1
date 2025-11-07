import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

# Create sample Invoice data with duplicates and mismatches
invoice_data = {
    'Item': ['A001', 'A002', 'A001', 'A003', 'A004', 'A002', 'A005'],  # A001 and A002 are duplicates
    'Description': [
        'Widget Type A',
        'Widget Type B',
        'Widget Type A',  # Duplicate
        'Widget Type C',
        'Widget Type D',
        'Widget Type B',  # Duplicate
        'Widget Type E'
    ],
    'Quantity': [10, 5, 8, 15, 20, 3, 12],  # Some quantities differ from PO
    'Unit Price': [25.50, 30.00, 25.50, 18.75, 22.00, 30.00, 35.50],  # Some prices differ from PO
    'Total': [255.00, 150.00, 204.00, 281.25, 440.00, 90.00, 426.00]
}

# Create sample PO data
po_data = {
    'Item': ['A001', 'A002', 'A003', 'A004', 'A006'],  # A006 is in PO but not in invoice
    'Description': [
        'Widget Type A',
        'Widget Type B',
        'Widget Type C',
        'Widget Type D',
        'Widget Type F'
    ],
    'Quantity': [10, 5, 20, 20, 8],  # A003 quantity differs (15 in invoice, 20 in PO), A004 matches
    'Unit Price': [25.00, 30.00, 18.75, 22.00, 40.00],  # A001 price differs (25.50 in invoice, 25.00 in PO)
    'Total': [250.00, 150.00, 375.00, 440.00, 320.00]
}

# Create DataFrames
invoice_df = pd.DataFrame(invoice_data)
po_df = pd.DataFrame(po_data)

# Create Excel files using pandas (simpler approach)
def create_formatted_excel(df, filename, title):
    # Use pandas to_excel which is simpler
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Get the worksheet
        ws = writer.sheets['Data']
        
        # Style the header row
        from openpyxl.styles import Font, PatternFill
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in ws[1]:  # First row (headers)
            cell.fill = header_fill
            cell.font = header_font
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Created {filename}")

# Create the sample files
create_formatted_excel(invoice_df, "sample_invoice.xlsx", "SAMPLE INVOICE")
create_formatted_excel(po_df, "sample_po.xlsx", "SAMPLE PURCHASE ORDER")

print("\n✅ Sample files created successfully!")
print("\nExpected Results:")
print("=" * 60)
print("DUPLICATES:")
print("  - A001 appears 2 times in invoice")
print("  - A002 appears 2 times in invoice")
print("\nMISMATCHES:")
print("  - A001: Price mismatch (Invoice: 25.50, PO: 25.00)")
print("  - A003: Quantity mismatch (Invoice: 15, PO: 20)")
print("\nANOMALIES:")
print("  - A005: In invoice but not in PO")
print("  - A006: In PO but not in invoice")
print("=" * 60)

