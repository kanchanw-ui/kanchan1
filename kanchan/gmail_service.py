import os
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import pickle

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Warning: Gmail API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.creds = None
        
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not installed")
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def get_messages(self, query: str = '', max_results: int = 10) -> List[Dict]:
        """Get messages from Gmail"""
        if not self.service:
            self.authenticate()
        
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_list = []
            for msg in messages:
                email_data = self.get_message_details(msg['id'])
                if email_data:
                    email_list.append(email_data)
            
            return email_list
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_message_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed information about a message"""
        if not self.service:
            self.authenticate()
        
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full').execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse date
            try:
                date_obj = email.utils.parsedate_to_datetime(date_str)
                received_at = date_obj.isoformat()
            except:
                received_at = datetime.now().isoformat()
            
            # Extract body
            body_text = ''
            body_html = ''
            has_attachments = False
            attachment_count = 0
            
            def extract_body(part, body_text, body_html):
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        body_text += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part.get('mimeType') == 'text/html':
                    data = part.get('body', {}).get('data')
                    if data:
                        body_html += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                # Check for attachments
                if part.get('filename'):
                    nonlocal has_attachments, attachment_count
                    has_attachments = True
                    attachment_count += 1
                
                # Recursively process parts
                if 'parts' in part:
                    for subpart in part['parts']:
                        body_text, body_html = extract_body(subpart, body_text, body_html)
                
                return body_text, body_html
            
            payload = message['payload']
            body_text, body_html = extract_body(payload, body_text, body_html)
            
            return {
                'gmail_id': message_id,
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'sender': sender,
                'recipient': recipient,
                'body': body_text,
                'body_html': body_html,
                'received_at': received_at,
                'has_attachments': has_attachments,
                'attachment_count': attachment_count,
                'raw_message': message
            }
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_unread_messages(self, max_results: int = 10) -> List[Dict]:
        """Get unread messages"""
        return self.get_messages(query='is:unread', max_results=max_results)
    
    def mark_as_read(self, message_id: str):
        """Mark message as read"""
        if not self.service:
            self.authenticate()
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def send_email(self, to: str, subject: str, body: str, is_html: bool = False):
        """Send an email"""
        if not self.service:
            self.authenticate()
        
        try:
            message = MIMEText(body, 'html' if is_html else 'plain')
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return send_message
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def forward_email(self, message_id: str, to: str):
        """Forward an email"""
        if not self.service:
            self.authenticate()
        
        try:
            # Get original message
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full').execute()
            
            # Create forward message
            headers = message['payload'].get('headers', [])
            original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            original_from = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            forward_subject = f"Fwd: {original_subject}"
            forward_body = f"Forwarded from: {original_from}\n\n{message.get('snippet', '')}"
            
            return self.send_email(to, forward_subject, forward_body)
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

