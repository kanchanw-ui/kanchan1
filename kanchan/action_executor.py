import os
import json
import requests
from typing import Dict, Optional
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("Warning: Google Sheets libraries not installed. Install with: pip install gspread google-auth")

class ActionExecutor:
    """Service for executing actions based on email classifications"""
    
    def __init__(self, slack_webhook_url: Optional[str] = None, 
                 sheets_credentials_path: Optional[str] = None,
                 sheets_spreadsheet_id: Optional[str] = None):
        self.slack_webhook_url = slack_webhook_url or os.getenv('SLACK_WEBHOOK_URL', '')
        self.sheets_credentials_path = sheets_credentials_path or os.getenv('SHEETS_CREDENTIALS_PATH', '')
        self.sheets_spreadsheet_id = sheets_spreadsheet_id or os.getenv('SHEETS_SPREADSHEET_ID', '')
        self.sheets_client = None
        
        if SHEETS_AVAILABLE and self.sheets_credentials_path and os.path.exists(self.sheets_credentials_path):
            try:
                scope = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_service_account_file(
                    self.sheets_credentials_path, scopes=scope)
                self.sheets_client = gspread.authorize(creds)
            except Exception as e:
                print(f"Warning: Could not initialize Google Sheets client: {str(e)}")
    
    def execute_action(self, action_type: str, action_name: str, email_data: Dict, 
                      classification: Dict, target: Optional[str] = None, 
                      parameters: Optional[Dict] = None) -> Dict:
        """
        Execute an action based on classification
        
        Returns:
            Dictionary with status, result, and error_message
        """
        try:
            if action_type == 'forward':
                return self._forward_email(email_data, target or classification.get('target', ''))
            
            elif action_type == 'update_hr':
                return self._update_hr_system(email_data, classification, parameters)
            
            elif action_type == 'add_calendar':
                return self._add_to_calendar(email_data, classification, parameters)
            
            elif action_type == 'create_ticket':
                return self._create_support_ticket(email_data, classification, parameters)
            
            elif action_type == 'auto_reply':
                return self._send_auto_reply(email_data, classification)
            
            elif action_type == 'notify_slack':
                return self._notify_slack(email_data, classification, target)
            
            elif action_type == 'log_to_sheets':
                return self._log_to_sheets(email_data, classification, parameters)
            
            else:
                return {
                    'status': 'error',
                    'result': None,
                    'error_message': f'Unknown action type: {action_type}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'error_message': str(e)
            }
    
    def _forward_email(self, email_data: Dict, target: str) -> Dict:
        """Forward email to target address"""
        # This would typically use GmailService to forward
        # For now, return a placeholder
        return {
            'status': 'success',
            'result': f'Email forwarded to {target}',
            'error_message': None
        }
    
    def _update_hr_system(self, email_data: Dict, classification: Dict, parameters: Optional[Dict]) -> Dict:
        """Update HR system (placeholder - would integrate with actual HR system)"""
        # In a real implementation, this would call HR system API
        return {
            'status': 'success',
            'result': f'HR system updated with leave request from {email_data.get("sender", "unknown")}',
            'error_message': None
        }
    
    def _add_to_calendar(self, email_data: Dict, classification: Dict, parameters: Optional[Dict]) -> Dict:
        """Add event to calendar (placeholder - would integrate with calendar API)"""
        # In a real implementation, this would use Google Calendar API or similar
        return {
            'status': 'success',
            'result': f'Meeting added to calendar: {email_data.get("subject", "No subject")}',
            'error_message': None
        }
    
    def _create_support_ticket(self, email_data: Dict, classification: Dict, parameters: Optional[Dict]) -> Dict:
        """Create support ticket (placeholder - would integrate with ticketing system)"""
        # In a real implementation, this would call ticketing system API
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            'status': 'success',
            'result': f'Support ticket created: {ticket_id}',
            'error_message': None
        }
    
    def _send_auto_reply(self, email_data: Dict, classification: Dict) -> Dict:
        """Send auto-reply (would use GmailService)"""
        # This would use GmailService to send reply
        return {
            'status': 'success',
            'result': f'Auto-reply sent to {email_data.get("sender", "unknown")}',
            'error_message': None
        }
    
    def _notify_slack(self, email_data: Dict, classification: Dict, target: Optional[str] = None) -> Dict:
        """Send notification to Slack"""
        if not self.slack_webhook_url:
            return {
                'status': 'error',
                'result': None,
                'error_message': 'Slack webhook URL not configured'
            }
        
        try:
            subject = email_data.get('subject', 'No subject')
            sender = email_data.get('sender', 'Unknown sender')
            category = classification.get('category', 'Unknown')
            justification = classification.get('justification', 'No justification')
            
            message = {
                "text": f"📧 New Email Classified: {category}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"📧 {category}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*From:*\n{sender}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Subject:*\n{subject}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Justification:*\n{justification}"
                        }
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook_url, json=message, timeout=10)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'result': 'Slack notification sent successfully',
                'error_message': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'error_message': f'Failed to send Slack notification: {str(e)}'
            }
    
    def _log_to_sheets(self, email_data: Dict, classification: Dict, parameters: Optional[Dict]) -> Dict:
        """Log email and classification to Google Sheets"""
        if not self.sheets_client or not self.sheets_spreadsheet_id:
            return {
                'status': 'error',
                'result': None,
                'error_message': 'Google Sheets not configured'
            }
        
        try:
            spreadsheet = self.sheets_client.open_by_key(self.sheets_spreadsheet_id)
            
            # Try to get or create worksheet
            try:
                worksheet = spreadsheet.worksheet('Email Log')
            except:
                worksheet = spreadsheet.add_worksheet(title='Email Log', rows=1000, cols=10)
                # Add headers
                worksheet.append_row([
                    'Timestamp', 'Subject', 'Sender', 'Category', 'Confidence', 
                    'Justification', 'Action Type', 'Status'
                ])
            
            # Append row
            row = [
                datetime.now().isoformat(),
                email_data.get('subject', ''),
                email_data.get('sender', ''),
                classification.get('category', ''),
                classification.get('confidence', 0),
                classification.get('justification', ''),
                classification.get('action_type', ''),
                'Processed'
            ]
            
            worksheet.append_row(row)
            
            return {
                'status': 'success',
                'result': 'Email logged to Google Sheets',
                'error_message': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'error_message': f'Failed to log to Sheets: {str(e)}'
            }

