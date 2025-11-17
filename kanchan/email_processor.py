import os
from datetime import datetime
from typing import Dict, List, Optional
from email_bot_database import EmailBotDatabase
from gmail_service import GmailService
from email_classifier import EmailClassifier
from action_executor import ActionExecutor

class EmailProcessor:
    """Main service for processing emails"""
    
    def __init__(self, openai_api_key: Optional[str] = None,
                 slack_webhook_url: Optional[str] = None,
                 sheets_credentials_path: Optional[str] = None,
                 sheets_spreadsheet_id: Optional[str] = None,
                 auto_execute: bool = False):
        self.db = EmailBotDatabase()
        self.gmail = GmailService()
        self.classifier = EmailClassifier(api_key=openai_api_key)
        self.executor = ActionExecutor(
            slack_webhook_url=slack_webhook_url,
            sheets_credentials_path=sheets_credentials_path,
            sheets_spreadsheet_id=sheets_spreadsheet_id
        )
        self.auto_execute = auto_execute
    
    def process_email(self, email_data: Dict) -> Dict:
        """Process a single email: classify and optionally execute action"""
        try:
            # Check if email already processed
            existing = self.db.get_email_by_gmail_id(email_data['gmail_id'])
            if existing and existing.get('processed_at'):
                return {
                    'status': 'already_processed',
                    'email_id': existing['id'],
                    'message': 'Email already processed'
                }
            
            # Save email to database
            email_id = self.db.save_email(
                gmail_id=email_data['gmail_id'],
                thread_id=email_data.get('thread_id', ''),
                subject=email_data.get('subject', ''),
                sender=email_data.get('sender', ''),
                recipient=email_data.get('recipient', ''),
                body=email_data.get('body', ''),
                body_html=email_data.get('body_html', ''),
                received_at=email_data.get('received_at', datetime.now().isoformat()),
                has_attachments=email_data.get('has_attachments', False),
                attachment_count=email_data.get('attachment_count', 0)
            )
            
            # Get available categories
            categories = self.db.get_all_categories()
            
            # Classify email
            classification_result = self.classifier.classify_email(email_data, categories)
            
            # Find category in database
            category = self.db.get_category_by_name(classification_result['category'])
            category_id = category['id'] if category else None
            
            # Save classification
            classification_id = self.db.save_classification(
                email_id=email_id,
                category_id=category_id,
                category_name=classification_result['category'],
                confidence=classification_result['confidence'],
                justification=classification_result['justification'],
                intent=classification_result.get('intent')
            )
            
            # Determine action
            action_type = classification_result.get('action_type', 'auto_reply')
            action_name = classification_result.get('action_name', 'Auto Reply')
            target = classification_result.get('target', '')
            
            # Save action
            action_id = self.db.save_action(
                email_id=email_id,
                classification_id=classification_id,
                action_type=action_type,
                action_name=action_name,
                target=target,
                parameters=None,
                status='pending' if not self.auto_execute else 'executing'
            )
            
            # Execute action if auto_execute is enabled
            action_result = None
            if self.auto_execute and not classification_result.get('requires_manual_review', False):
                action_result = self.executor.execute_action(
                    action_type=action_type,
                    action_name=action_name,
                    email_data=email_data,
                    classification=classification_result,
                    target=target
                )
                
                # Update action status
                self.db.update_action_status(
                    action_id=action_id,
                    status=action_result['status'],
                    result=action_result.get('result'),
                    error_message=action_result.get('error_message')
                )
            
            # Mark email as processed
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE emails SET processed_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (email_id,))
            conn.commit()
            conn.close()
            
            return {
                'status': 'success',
                'email_id': email_id,
                'classification_id': classification_id,
                'action_id': action_id,
                'classification': classification_result,
                'action_result': action_result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def process_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """Process all unread emails"""
        try:
            # Authenticate Gmail if needed
            if not self.gmail.service:
                self.gmail.authenticate()
            
            # Get unread emails
            emails = self.gmail.get_unread_messages(max_results=max_results)
            
            results = []
            for email_data in emails:
                result = self.process_email(email_data)
                results.append(result)
                
                # Mark as read after processing
                if result.get('status') == 'success':
                    self.gmail.mark_as_read(email_data['gmail_id'])
            
            return results
        except Exception as e:
            return [{
                'status': 'error',
                'error_message': f'Failed to process unread emails: {str(e)}'
            }]
    
    def execute_pending_action(self, action_id: int) -> Dict:
        """Execute a pending action"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT a.*, e.*, c.category_name, c.justification, c.intent
                FROM actions a
                JOIN emails e ON a.email_id = e.id
                LEFT JOIN classifications c ON a.classification_id = c.id
                WHERE a.id = ?
            ''', (action_id,))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        finally:
            conn.close()
        
        if not row or not columns:
            return {
                'status': 'error',
                'error_message': 'Action not found'
            }
        
        # Extract data
        action_data = dict(zip(columns, row))
        
        email_data = {
            'gmail_id': action_data.get('gmail_id', ''),
            'subject': action_data.get('subject', ''),
            'sender': action_data.get('sender', ''),
            'body': action_data.get('body', ''),
            'recipient': action_data.get('recipient', '')
        }
        
        classification = {
            'category': action_data.get('category_name', ''),
            'justification': action_data.get('justification', ''),
            'intent': action_data.get('intent', ''),
            'action_type': action_data.get('action_type', ''),
            'action_name': action_data.get('action_name', ''),
            'target': action_data.get('target', '')
        }
        
        # Execute action
        action_result = self.executor.execute_action(
            action_type=action_data.get('action_type', ''),
            action_name=action_data.get('action_name', ''),
            email_data=email_data,
            classification=classification,
            target=action_data.get('target')
        )
        
        # Update action status
        self.db.update_action_status(
            action_id=action_id,
            status=action_result['status'],
            result=action_result.get('result'),
            error_message=action_result.get('error_message')
        )
        
        return action_result

