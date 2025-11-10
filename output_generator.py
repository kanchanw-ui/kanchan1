import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Lazy import for reportlab to avoid startup issues
def _import_reportlab():
    """Lazy import reportlab only when needed"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    return {
        'letter': letter,
        'A4': A4,
        'colors': colors,
        'inch': inch,
        'SimpleDocTemplate': SimpleDocTemplate,
        'Table': Table,
        'TableStyle': TableStyle,
        'Paragraph': Paragraph,
        'Spacer': Spacer,
        'PageBreak': PageBreak,
        'getSampleStyleSheet': getSampleStyleSheet,
        'ParagraphStyle': ParagraphStyle,
        'TA_CENTER': TA_CENTER,
        'TA_LEFT': TA_LEFT
    }

class OutputGenerator:
    """Generate Excel and PDF output files"""
    
    def generate_excel(self, results, invoice_data, po_data):
        """Generate Excel report with comparison results"""
        wb = Workbook()
        
        # Remove default sheet
        wb.remove(wb.active)
        
        # Summary sheet
        summary_sheet = wb.create_sheet("Summary", 0)
        self._create_summary_sheet(summary_sheet, results)
        
        # Mismatches sheet
        if results['mismatches']:
            mismatches_sheet = wb.create_sheet("Mismatches")
            self._create_issues_sheet(mismatches_sheet, results['mismatches'], "Mismatches")
        
        # Duplicates sheet
        if results['duplicates']:
            duplicates_sheet = wb.create_sheet("Duplicates")
            self._create_issues_sheet(duplicates_sheet, results['duplicates'], "Duplicates")
        
        # Anomalies sheet
        if results['anomalies']:
            anomalies_sheet = wb.create_sheet("Anomalies")
            self._create_issues_sheet(anomalies_sheet, results['anomalies'], "Anomalies")
        
        # Invoice data sheet
        if invoice_data is not None and isinstance(invoice_data, pd.DataFrame):
            invoice_sheet = wb.create_sheet("Invoice Data")
            self._create_data_sheet(invoice_sheet, invoice_data, "Invoice")
        
        # PO data sheet
        if po_data is not None and isinstance(po_data, pd.DataFrame):
            po_sheet = wb.create_sheet("PO Data")
            self._create_data_sheet(po_sheet, po_data, "Purchase Order")
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    def _create_summary_sheet(self, sheet, results):
        """Create summary sheet"""
        sheet['A1'] = 'Invoice QA Report - Summary'
        sheet['A1'].font = Font(size=16, bold=True)
        sheet.merge_cells('A1:D1')
        
        row = 3
        sheet[f'A{row}'] = 'Metric'
        sheet[f'B{row}'] = 'Count'
        sheet[f'A{row}'].font = Font(bold=True)
        sheet[f'B{row}'].font = Font(bold=True)
        
        row += 1
        sheet[f'A{row}'] = 'Total Mismatches'
        sheet[f'B{row}'] = results['summary']['total_mismatches']
        
        row += 1
        sheet[f'A{row}'] = 'Total Duplicates'
        sheet[f'B{row}'] = results['summary']['total_duplicates']
        
        row += 1
        sheet[f'A{row}'] = 'Total Anomalies'
        sheet[f'B{row}'] = results['summary']['total_anomalies']
        
        row += 1
        total_issues = sum([
            results['summary']['total_mismatches'],
            results['summary']['total_duplicates'],
            results['summary']['total_anomalies']
        ])
        sheet[f'A{row}'] = 'Total Issues'
        sheet[f'B{row}'] = total_issues
        sheet[f'B{row}'].font = Font(bold=True, color="FF0000" if total_issues > 0 else "00FF00")
        
        # Auto-adjust column widths
        sheet.column_dimensions['A'].width = 25
        sheet.column_dimensions['B'].width = 15
    
    def _create_issues_sheet(self, sheet, issues, title):
        """Create sheet for issues (mismatches, duplicates, anomalies)"""
        if not issues:
            return
        
        def to_scalar_string(value):
            """Normalize any value (including pandas/numpy/Series) to a safe string for Excel."""
            try:
                import numpy as np  # lazy import safe
            except Exception:
                np = None
            # Unwrap pandas Series
            if isinstance(value, pd.Series):
                value = value.iloc[0] if len(value) > 0 else ""
            # Convert pandas Timestamp to iso string
            if hasattr(value, "strftime"):
                try:
                    return value.strftime("%Y-%m-%d")
                except Exception:
                    pass
            # Handle numpy scalar
            if np is not None and isinstance(value, getattr(np, "generic", ())):
                try:
                    value = value.item()
                except Exception:
                    pass
            # Fallbacks
            if value is None:
                return ""
            return str(value)
        
        sheet['A1'] = f'{title} Details'
        sheet['A1'].font = Font(size=14, bold=True)
        
        # Get headers from first issue
        headers = list(issues[0].keys())
        
        # Write headers
        for col_idx, header in enumerate(headers, start=1):
            cell = sheet.cell(row=3, column=col_idx)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Write data
        for row_idx, issue in enumerate(issues, start=4):
            for col_idx, header in enumerate(headers, start=1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                cell.value = to_scalar_string(issue.get(header, ''))
                
                # Color code by severity
                if 'severity' in issue:
                    severity = issue['severity'].lower()
                    if severity == 'high':
                        cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
                    elif severity == 'medium':
                        cell.fill = PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid")
        
        # Auto-adjust column widths
        for col_idx in range(1, len(headers) + 1):
            sheet.column_dimensions[get_column_letter(col_idx)].width = 20
    
    def _create_data_sheet(self, sheet, df, title):
        """Create sheet for invoice/PO data"""
        def to_scalar(value):
            if isinstance(value, pd.Series):
                return to_scalar(value.iloc[0] if len(value) > 0 else "")
            # Normalize pandas NaN
            if pd.isna(value):
                return ""
            # Dates
            if hasattr(value, "strftime"):
                try:
                    return value.strftime("%Y-%m-%d")
                except Exception:
                    pass
            try:
                import numpy as np
                if isinstance(value, np.generic):
                    try:
                        return value.item()
                    except Exception:
                        return str(value)
            except Exception:
                pass
            return value

        sheet['A1'] = f'{title} Data'
        sheet['A1'].font = Font(size=14, bold=True)
        
        # Write headers
        for col_idx, col_name in enumerate(df.columns, start=1):
            cell = sheet.cell(row=3, column=col_idx)
            cell.value = col_name
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Write data
        for row_idx, (_, df_row) in enumerate(df.iterrows(), start=4):
            for col_idx, col_name in enumerate(df.columns, start=1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                value = df_row[col_name]
                value = to_scalar(value)
                cell.value = "" if (value is None) else value
        
        # Auto-adjust column widths
        for col_idx in range(1, len(df.columns) + 1):
            sheet.column_dimensions[get_column_letter(col_idx)].width = 15
    
    def generate_pdf(self, results, invoice_data, po_data):
        """Generate PDF report with comparison results"""
        # Lazy import reportlab
        rl = _import_reportlab()
        
        buffer = BytesIO()
        doc = rl['SimpleDocTemplate'](buffer, pagesize=rl['letter'])
        story = []
        
        # Styles
        styles = rl['getSampleStyleSheet']()
        title_style = rl['ParagraphStyle'](
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=rl['colors'].HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=rl['TA_CENTER']
        )
        
        heading_style = rl['ParagraphStyle'](
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=rl['colors'].HexColor('#333333'),
            spaceAfter=12
        )
        
        # Title
        story.append(rl['Paragraph']("Invoice QA Report", title_style))
        story.append(rl['Spacer'](1, 0.2*rl['inch']))
        
        # Summary
        story.append(rl['Paragraph']("Summary", heading_style))
        summary_data = [
            ['Metric', 'Count'],
            ['Total Mismatches', str(results['summary']['total_mismatches'])],
            ['Total Duplicates', str(results['summary']['total_duplicates'])],
            ['Total Anomalies', str(results['summary']['total_anomalies'])],
        ]
        
        total_issues = sum([
            results['summary']['total_mismatches'],
            results['summary']['total_duplicates'],
            results['summary']['total_anomalies']
        ])
        summary_data.append(['Total Issues', str(total_issues)])
        
        summary_table = rl['Table'](summary_data)
        summary_table.setStyle(rl['TableStyle']([
            ('BACKGROUND', (0, 0), (-1, 0), rl['colors'].grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl['colors'].whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), rl['colors'].beige),
            ('GRID', (0, 0), (-1, -1), 1, rl['colors'].black)
        ]))
        story.append(summary_table)
        story.append(rl['Spacer'](1, 0.3*rl['inch']))
        
        # Mismatches
        if results['mismatches']:
            story.append(rl['Paragraph']("Mismatches", heading_style))
            mismatches_data = self._prepare_table_data(results['mismatches'])
            mismatches_table = rl['Table'](mismatches_data)
            mismatches_table.setStyle(self._get_table_style(rl))
            story.append(mismatches_table)
            story.append(rl['Spacer'](1, 0.3*rl['inch']))
        
        # Duplicates
        if results['duplicates']:
            story.append(rl['Paragraph']("Duplicates", heading_style))
            duplicates_data = self._prepare_table_data(results['duplicates'])
            duplicates_table = rl['Table'](duplicates_data)
            duplicates_table.setStyle(self._get_table_style(rl))
            story.append(duplicates_table)
            story.append(rl['Spacer'](1, 0.3*rl['inch']))
        
        # Anomalies
        if results['anomalies']:
            story.append(rl['Paragraph']("Anomalies", heading_style))
            anomalies_data = self._prepare_table_data(results['anomalies'])
            anomalies_table = rl['Table'](anomalies_data)
            anomalies_table.setStyle(self._get_table_style(rl))
            story.append(anomalies_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _prepare_table_data(self, issues):
        """Prepare data for PDF table"""
        if not issues:
            return [['No issues found']]
        
        # Get all unique keys from all issues
        all_keys = set()
        for issue in issues:
            all_keys.update(issue.keys())
        
        headers = ['Item', 'Type', 'Description', 'Severity']
        # Ensure headers exist in data
        headers = [h for h in headers if h in all_keys] + [k for k in all_keys if k not in headers]
        
        data = [headers]
        for issue in issues:
            row = [str(issue.get(h, '')) for h in headers]
            data.append(row)
        
        return data
    
    def _get_table_style(self, rl):
        """Get table style for PDF"""
        return rl['TableStyle']([
            ('BACKGROUND', (0, 0), (-1, 0), rl['colors'].grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl['colors'].whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), rl['colors'].beige),
            ('GRID', (0, 0), (-1, -1), 1, rl['colors'].black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl['colors'].white, rl['colors'].lightgrey])
        ])

