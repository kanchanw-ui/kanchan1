import sqlite3
import os
from datetime import datetime
import hashlib

class Database:
    """Database management for Invoice QA Agent"""
    
    def __init__(self, db_path="invoice_qa.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                upload_name TEXT NOT NULL,
                invoice_filename TEXT NOT NULL,
                po_filename TEXT NOT NULL,
                invoice_path TEXT NOT NULL,
                po_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Comparison results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparison_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                mismatches_count INTEGER DEFAULT 0,
                duplicates_count INTEGER DEFAULT 0,
                anomalies_count INTEGER DEFAULT 0,
                results_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (upload_id) REFERENCES file_uploads(id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            default_password = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', ('admin', default_password, 'admin@example.com'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'email': user[2]}
        return None
    
    def save_file_upload(self, user_id, upload_name, invoice_filename, po_filename, invoice_path, po_path):
        """Save file upload record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_uploads 
            (user_id, upload_name, invoice_filename, po_filename, invoice_path, po_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, upload_name, invoice_filename, po_filename, invoice_path, po_path))
        upload_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return upload_id
    
    def save_comparison_result(self, upload_id, mismatches_count, duplicates_count, anomalies_count, results_json):
        """Save comparison result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comparison_results 
            (upload_id, mismatches_count, duplicates_count, anomalies_count, results_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (upload_id, mismatches_count, duplicates_count, anomalies_count, results_json))
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def get_user_uploads(self, user_id):
        """Get all uploads for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.upload_name, u.invoice_filename, u.po_filename, 
                   u.uploaded_at, c.mismatches_count, c.duplicates_count, c.anomalies_count
            FROM file_uploads u
            LEFT JOIN comparison_results c ON u.id = c.upload_id
            WHERE u.user_id = ?
            ORDER BY u.uploaded_at DESC
        ''', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_upload_result(self, upload_id):
        """Get result for a specific upload"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT results_json FROM comparison_results
            WHERE upload_id = ?
        ''', (upload_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_collective_results(self, user_id):
        """Get aggregated results for all user uploads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(mismatches_count) as total_mismatches,
                SUM(duplicates_count) as total_duplicates,
                SUM(anomalies_count) as total_anomalies,
                COUNT(*) as total_comparisons
            FROM comparison_results c
            JOIN file_uploads u ON c.upload_id = u.id
            WHERE u.user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return {
            'total_mismatches': result[0] or 0,
            'total_duplicates': result[1] or 0,
            'total_anomalies': result[2] or 0,
            'total_comparisons': result[3] or 0
        }

