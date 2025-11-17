"""
Email Poller Service
Continuously polls Gmail for new emails and processes them
"""
import time
import os
import signal
import sys
from email_processor import EmailProcessor
from email_bot_database import EmailBotDatabase

class EmailPoller:
    """Service that polls Gmail for new emails"""
    
    def __init__(self):
        self.db = EmailBotDatabase()
        self.running = False
        self.processor = None
    
    def initialize_processor(self):
        """Initialize email processor"""
        openai_key = os.getenv('OPENAI_API_KEY', '')
        slack_webhook = self.db.get_config('slack_webhook_url') or ''
        sheets_id = self.db.get_config('sheets_spreadsheet_id') or ''
        auto_execute = self.db.get_config('auto_execute_actions') == 'true'
        
        self.processor = EmailProcessor(
            openai_api_key=openai_key if openai_key else None,
            slack_webhook_url=slack_webhook if slack_webhook else None,
            sheets_spreadsheet_id=sheets_id if sheets_id else None,
            auto_execute=auto_execute
        )
    
    def poll_once(self):
        """Poll for new emails once"""
        try:
            if not self.processor:
                self.initialize_processor()
            
            # Authenticate Gmail if needed
            if not self.processor.gmail.service:
                print("Authenticating Gmail...")
                self.processor.gmail.authenticate()
            
            # Process unread emails
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Polling for new emails...")
            results = self.processor.process_unread_emails(max_results=10)
            
            success_count = sum(1 for r in results if r.get('status') == 'success')
            error_count = sum(1 for r in results if r.get('status') == 'error')
            
            if success_count > 0 or error_count > 0:
                print(f"Processed {success_count} emails successfully, {error_count} errors")
            
            return results
        except Exception as e:
            print(f"Error polling emails: {str(e)}")
            return []
    
    def run(self):
        """Run the poller continuously"""
        self.running = True
        
        # Handle shutdown signals
        def signal_handler(sig, frame):
            print("\nShutting down email poller...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("Email Poller started. Press Ctrl+C to stop.")
        
        while self.running:
            try:
                self.poll_once()
                
                # Get polling interval from config
                interval = int(self.db.get_config('gmail_poll_interval') or '300')
                
                # Sleep for the interval
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        print("Email Poller stopped.")

if __name__ == "__main__":
    poller = EmailPoller()
    poller.run()

