import sqlite3
import os
from datetime import datetime
import json

class EmailBotDatabase:
    """Database management for Email Understanding & Action Bot"""
    
    def __init__(self, db_path="email_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gmail_id TEXT UNIQUE NOT NULL,
                thread_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipient TEXT,
                body TEXT,
                body_html TEXT,
                received_at TIMESTAMP NOT NULL,
                processed_at TIMESTAMP,
                has_attachments BOOLEAN DEFAULT 0,
                attachment_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Email attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT,
                file_size INTEGER,
                mime_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                keywords TEXT,
                action_type TEXT NOT NULL,
                target TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Classifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                category_id INTEGER,
                category_name TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                justification TEXT NOT NULL,
                intent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                classification_id INTEGER,
                action_type TEXT NOT NULL,
                action_name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                target TEXT,
                parameters TEXT,
                result TEXT,
                error_message TEXT,
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id),
                FOREIGN KEY (classification_id) REFERENCES classifications(id)
            )
        ''')
        
        # Action history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (action_id) REFERENCES actions(id)
            )
        ''')
        
        # Configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('Invoice Attached', 'Emails with invoice attachments', 'invoice,payment,due date,bill,amount', 'forward', 'finance@example.com', 1),
            ('Leave Request', 'Employee leave requests', 'leave,vacation,time off,holiday,absence', 'update_hr', 'hr_system', 1),
            ('Meeting Request', 'Meeting invitations and requests', 'meeting,calendar,appointment,schedule', 'add_calendar', 'calendar', 1),
            ('Support Ticket', 'Customer support requests', 'support,help,issue,problem,ticket', 'create_ticket', 'support_system', 1),
            ('Purchase Order', 'Purchase order notifications', 'purchase order,po,order,procurement', 'forward', 'procurement@example.com', 1),
            ('Expense Report', 'Expense report submissions', 'expense,reimbursement,receipt,cost', 'forward', 'finance@example.com', 1),
            ('Contract Review', 'Contract review requests', 'contract,agreement,legal,review', 'forward', 'legal@example.com', 1),
            ('General Inquiry', 'General inquiries requiring response', 'question,inquiry,help,information', 'auto_reply', 'auto', 1),
        ]
        
        for cat in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, description, keywords, action_type, target, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', cat)
        
        # Insert default configuration
        default_config = [
            ('gmail_poll_interval', '300', 'Gmail polling interval in seconds'),
            ('auto_execute_actions', 'false', 'Automatically execute actions without confirmation'),
            ('slack_webhook_url', '', 'Slack webhook URL for notifications'),
            ('sheets_spreadsheet_id', '', 'Google Sheets spreadsheet ID for logging'),
        ]
        
        for config in default_config:
            cursor.execute('''
                INSERT OR IGNORE INTO config (key, value, description)
                VALUES (?, ?, ?)
            ''', config)
        
        conn.commit()
        conn.close()
    
    def save_email(self, gmail_id, thread_id, subject, sender, recipient, body, body_html, 
                   received_at, has_attachments=False, attachment_count=0):
        """Save email to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO emails 
                (gmail_id, thread_id, subject, sender, recipient, body, body_html, 
                 received_at, has_attachments, attachment_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (gmail_id, thread_id, subject, sender, recipient, body, body_html, 
                  received_at, has_attachments, attachment_count))
            email_id = cursor.lastrowid
            conn.commit()
            return email_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_email_by_gmail_id(self, gmail_id):
        """Get email by Gmail ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emails WHERE gmail_id = ?', (gmail_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def save_classification(self, email_id, category_id, category_name, confidence, justification, intent=None):
        """Save email classification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO classifications 
                (email_id, category_id, category_name, confidence, justification, intent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email_id, category_id, category_name, confidence, justification, intent))
            classification_id = cursor.lastrowid
            conn.commit()
            return classification_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def save_action(self, email_id, classification_id, action_type, action_name, target=None, 
                   parameters=None, status='pending'):
        """Save action to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            params_json = json.dumps(parameters) if parameters else None
            cursor.execute('''
                INSERT INTO actions 
                (email_id, classification_id, action_type, action_name, target, parameters, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email_id, classification_id, action_type, action_name, target, params_json, status))
            action_id = cursor.lastrowid
            conn.commit()
            return action_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_action_status(self, action_id, status, result=None, error_message=None):
        """Update action status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE actions 
                SET status = ?, result = ?, error_message = ?, executed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, result, error_message, action_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_categories(self):
        """Get all categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE is_active = 1 ORDER BY name')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    
    def get_category_by_name(self, name):
        """Get category by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_emails_with_classifications(self, limit=100, offset=0):
        """Get emails with their classifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, c.category_name, c.confidence, c.justification, c.intent,
                   a.action_type, a.action_name, a.status as action_status
            FROM emails e
            LEFT JOIN classifications c ON e.id = c.email_id
            LEFT JOIN actions a ON e.id = a.email_id
            ORDER BY e.received_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    
    def get_email_details(self, email_id):
        """Get detailed email information with classification and actions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, c.category_name, c.confidence, c.justification, c.intent,
                   a.id as action_id, a.action_type, a.action_name, a.status as action_status,
                   a.result, a.error_message, a.executed_at
            FROM emails e
            LEFT JOIN classifications c ON e.id = c.email_id
            LEFT JOIN actions a ON e.id = a.email_id
            WHERE e.id = ?
        ''', (email_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    
    def get_config(self, key):
        """Get configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def set_config(self, key, value):
        """Set configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Get statistics about emails, classifications, and actions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total emails
        cursor.execute('SELECT COUNT(*) FROM emails')
        stats['total_emails'] = cursor.fetchone()[0]
        
        # Processed emails
        cursor.execute('SELECT COUNT(*) FROM emails WHERE processed_at IS NOT NULL')
        stats['processed_emails'] = cursor.fetchone()[0]
        
        # Total classifications
        cursor.execute('SELECT COUNT(*) FROM classifications')
        stats['total_classifications'] = cursor.fetchone()[0]
        
        # Total actions
        cursor.execute('SELECT COUNT(*) FROM actions')
        stats['total_actions'] = cursor.fetchone()[0]
        
        # Actions by status
        cursor.execute('SELECT status, COUNT(*) FROM actions GROUP BY status')
        stats['actions_by_status'] = dict(cursor.fetchall())
        
        # Classifications by category
        cursor.execute('SELECT category_name, COUNT(*) FROM classifications GROUP BY category_name')
        stats['classifications_by_category'] = dict(cursor.fetchall())
        
        conn.close()
        return stats

