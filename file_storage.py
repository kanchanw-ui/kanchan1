import os
import shutil
from datetime import datetime
from pathlib import Path

class FileStorage:
    """Handle file storage for uploaded invoices and POs"""
    
    def __init__(self, storage_dir="uploads"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_file(self, uploaded_file, user_id, upload_id, file_type="invoice"):
        """Save uploaded file to storage"""
        # Create user directory
        user_dir = self.storage_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        
        # Create upload directory
        upload_dir = user_dir / str(upload_id)
        upload_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(uploaded_file.name).suffix
        filename = f"{file_type}_{timestamp}{file_extension}"
        file_path = upload_dir / filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    
    def get_file_path(self, user_id, upload_id, file_type="invoice"):
        """Get file path for a stored file"""
        upload_dir = self.storage_dir / str(user_id) / str(upload_id)
        files = list(upload_dir.glob(f"{file_type}_*"))
        return str(files[0]) if files else None
    
    def delete_upload(self, user_id, upload_id):
        """Delete an upload and its files"""
        upload_dir = self.storage_dir / str(user_id) / str(upload_id)
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
            return True
        return False

