import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import pandas as pd
import json

class InvoiceQAAgent:
    """AI Agent for comparing invoices against purchase orders"""
    
    def __init__(self, api_key):
        """Initialize the AI agent with OpenAI API key"""
        os.environ['OPENAI_API_KEY'] = api_key
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            max_tokens=2000
        )
    
    def compare_invoice_po(self, invoice_data, po_data):
        """Compare invoice against purchase order using AI"""
        
        # Convert dataframes to structured format
        invoice_str = self._dataframe_to_string(invoice_data)
        po_str = self._dataframe_to_string(po_data)
        
        # Create prompt for AI comparison
        prompt = self._create_comparison_prompt(invoice_str, po_str)
        
        try:
            # Get AI response
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content
            
            # Parse AI response
            results = self._parse_ai_response(result_text)
            
            # Add rule-based checks for additional validation
            rule_based_results = self._rule_based_checks(invoice_data, po_data)
            
            # Merge AI and rule-based results
            merged_results = self._merge_results(results, rule_based_results)
            
            return merged_results
            
        except Exception as e:
            # Fallback to rule-based if AI fails
            print(f"AI comparison failed: {str(e)}")
            return self._rule_based_checks(invoice_data, po_data)
    
    def _dataframe_to_string(self, df):
        """Convert DataFrame to readable string format"""
        if isinstance(df, pd.DataFrame):
            return df.to_string(index=False)
        else:
            return str(df)
    
    def _create_comparison_prompt(self, invoice_str, po_str):
        """Create prompt for AI comparison"""
        prompt = f"""You are an expert invoice auditor. Compare the following invoice against the purchase order and identify:

1. **Rate Mismatches**: Items where the unit price in the invoice differs from the purchase order
2. **Duplicates**: Items that appear multiple times in the invoice
3. **Unusual Entries**: Items in invoice that are not in PO, or suspicious patterns

**INVOICE DATA:**
{invoice_str}

**PURCHASE ORDER DATA:**
{po_str}

Please analyze and return a JSON response with the following structure:
{{
    "mismatches": [
        {{
            "type": "Rate Mismatch",
            "item": "item name/code",
            "invoice_value": "value from invoice",
            "po_value": "value from PO",
            "difference": "difference amount",
            "severity": "High/Medium/Low",
            "description": "detailed explanation"
        }}
    ],
    "duplicates": [
        {{
            "type": "Duplicate Item",
            "item": "item name/code",
            "occurrences": number,
            "description": "where duplicates appear"
        }}
    ],
    "anomalies": [
        {{
            "type": "Anomaly Type",
            "item": "item name/code",
            "description": "what is unusual about this",
            "severity": "High/Medium/Low"
        }}
    ]
}}

Focus on:
- Price discrepancies (even small ones)
- Quantity mismatches
- Items in invoice but not in PO
- Items in PO but missing in invoice
- Duplicate line items
- Unusual pricing patterns
- Round number anomalies

Return ONLY valid JSON, no additional text."""
        
        return prompt
    
    def _parse_ai_response(self, response_text):
        """Parse AI response JSON"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Ensure all required keys exist
                result = {
                    'mismatches': parsed.get('mismatches', []),
                    'duplicates': parsed.get('duplicates', []),
                    'anomalies': parsed.get('anomalies', [])
                }
                
                return result
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
        
        # Return empty result if parsing fails
        return {
            'mismatches': [],
            'duplicates': [],
            'anomalies': []
        }
    
    def _rule_based_checks(self, invoice_data, po_data):
        """Rule-based comparison as fallback or supplement"""
        mismatches = []
        duplicates = []
        anomalies = []
        
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
        
        # Find item column (case-insensitive, handle variations)
        invoice_item_col = None
        po_item_col = None
        
        for col in invoice_df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['item', 'item_no', 'item_number', 'product', 'product_code', 'sku', 'item code', 'item_code']:
                invoice_item_col = col
                break
        
        for col in po_df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['item', 'item_no', 'item_number', 'product', 'product_code', 'sku', 'item code', 'item_code']:
                po_item_col = col
                break
        
        # Find price/rate columns
        invoice_price_col = None
        po_price_col = None
        
        for col in invoice_df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['unit price', 'price', 'rate', 'unit cost', 'cost', 'unit_price', 'unitprice']:
                invoice_price_col = col
                break
        
        for col in po_df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['unit price', 'price', 'rate', 'unit cost', 'cost', 'unit_price', 'unitprice']:
                po_price_col = col
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
            item_counts = invoice_df[invoice_item_col].value_counts()
            for item, count in item_counts.items():
                if pd.notna(item) and str(item).strip() != '' and count > 1:
                    duplicates.append({
                        'type': 'Duplicate Item',
                        'item': str(item),
                        'occurrences': int(count),
                        'description': f'Item "{item}" appears {count} times in invoice',
                        'severity': 'Medium'
                    })
        
        # Compare rates
        if invoice_item_col and po_item_col:
            # Convert to string for comparison
            invoice_df[invoice_item_col] = invoice_df[invoice_item_col].astype(str)
            po_df[po_item_col] = po_df[po_item_col].astype(str)
            
            for idx, inv_row in invoice_df.iterrows():
                item = str(inv_row.get(invoice_item_col, '')).strip()
                if not item or item == 'nan' or item == '':
                    continue
                
                # Find matching item in PO
                po_matches = po_df[po_df[po_item_col].astype(str).str.strip() == item]
                
                if po_matches.empty:
                    # Item in invoice but not in PO
                    anomalies.append({
                        'type': 'Item Not in PO',
                        'item': str(item),
                        'description': f'Item "{item}" found in invoice but not in purchase order',
                        'severity': 'High'
                    })
                else:
                    po_row = po_matches.iloc[0]
                    
                    # Check price/rate
                    if invoice_price_col and po_price_col:
                        try:
                            inv_price = pd.to_numeric(inv_row.get(invoice_price_col, 0), errors='coerce')
                            po_price = pd.to_numeric(po_row.get(po_price_col, 0), errors='coerce')
                            
                            if pd.notna(inv_price) and pd.notna(po_price):
                                diff = abs(float(inv_price) - float(po_price))
                                if diff > 0.01:  # Allow small rounding differences
                                    severity = 'High' if diff > abs(po_price) * 0.1 else 'Medium'
                                    mismatches.append({
                                        'type': 'Rate Mismatch',
                                        'item': str(item),
                                        'invoice_value': f"{inv_price:.2f}",
                                        'po_value': f"{po_price:.2f}",
                                        'difference': f"{diff:.2f}",
                                        'severity': severity,
                                        'description': f'Unit price mismatch: Invoice={inv_price:.2f}, PO={po_price:.2f}'
                                    })
                        except (ValueError, TypeError):
                            pass
                    
                    # Check quantity
                    if invoice_qty_col and po_qty_col:
                        try:
                            inv_qty = pd.to_numeric(inv_row.get(invoice_qty_col, 0), errors='coerce')
                            po_qty = pd.to_numeric(po_row.get(po_qty_col, 0), errors='coerce')
                            
                            if pd.notna(inv_qty) and pd.notna(po_qty):
                                diff = abs(float(inv_qty) - float(po_qty))
                                if diff > 0.01:
                                    mismatches.append({
                                        'type': 'Quantity Mismatch',
                                        'item': str(item),
                                        'invoice_value': f"{inv_qty:.2f}",
                                        'po_value': f"{po_qty:.2f}",
                                        'difference': f"{diff:.2f}",
                                        'severity': 'High',
                                        'description': f'Quantity mismatch: Invoice={inv_qty:.2f}, PO={po_qty:.2f}'
                                    })
                        except (ValueError, TypeError):
                            pass
        
        # Check for items in PO but not in invoice
        if invoice_item_col and po_item_col:
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
    
    def _merge_results(self, ai_results, rule_results):
        """Merge AI and rule-based results"""
        # Combine results, avoiding duplicates
        merged = {
            'mismatches': list(ai_results.get('mismatches', [])) + rule_results['mismatches'],
            'duplicates': list(ai_results.get('duplicates', [])) + rule_results['duplicates'],
            'anomalies': list(ai_results.get('anomalies', [])) + rule_results['anomalies']
        }
        
        # Remove duplicates based on item name
        seen_items = set()
        for category in ['mismatches', 'duplicates', 'anomalies']:
            unique_items = []
            for item in merged[category]:
                item_key = item.get('item', '')
                if item_key not in seen_items:
                    unique_items.append(item)
                    seen_items.add(item_key)
            merged[category] = unique_items
        
        merged['summary'] = {
            'total_mismatches': len(merged['mismatches']),
            'total_duplicates': len(merged['duplicates']),
            'total_anomalies': len(merged['anomalies'])
        }
        
        return merged

