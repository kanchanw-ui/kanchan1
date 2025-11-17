from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from email_processor import EmailProcessor
from email_bot_database import EmailBotDatabase

app = FastAPI(title="Email Understanding & Action Bot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = EmailBotDatabase()

# Pydantic models
class EmailProcessRequest(BaseModel):
    gmail_id: Optional[str] = None
    auto_execute: bool = False

class ActionExecuteRequest(BaseModel):
    action_id: int

class CategoryCreateRequest(BaseModel):
    name: str
    description: str
    keywords: str
    action_type: str
    target: str
    is_active: bool = True

@app.get("/")
def root():
    return {"message": "Email Understanding & Action Bot API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/emails")
def get_emails(limit: int = 100, offset: int = 0):
    """Get emails with classifications"""
    try:
        emails = db.get_emails_with_classifications(limit=limit, offset=offset)
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/{email_id}")
def get_email(email_id: int):
    """Get detailed email information"""
    try:
        details = db.get_email_details(email_id)
        if not details:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"email": details}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/process")
def process_email(request: EmailProcessRequest, background_tasks: BackgroundTasks):
    """Process an email (classify and optionally execute action)"""
    try:
        processor = EmailProcessor(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            slack_webhook_url=db.get_config('slack_webhook_url'),
            sheets_spreadsheet_id=db.get_config('sheets_spreadsheet_id'),
            auto_execute=request.auto_execute
        )
        
        # If gmail_id provided, fetch from Gmail
        if request.gmail_id:
            if not processor.gmail.service:
                processor.gmail.authenticate()
            email_data = processor.gmail.get_message_details(request.gmail_id)
            if not email_data:
                raise HTTPException(status_code=404, detail="Email not found in Gmail")
        else:
            # Process unread emails
            results = processor.process_unread_emails(max_results=10)
            return {"results": results}
        
        # Process single email
        result = processor.process_email(email_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/actions/{action_id}/execute")
def execute_action(action_id: int):
    """Execute a pending action"""
    try:
        processor = EmailProcessor(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            slack_webhook_url=db.get_config('slack_webhook_url'),
            sheets_spreadsheet_id=db.get_config('sheets_spreadsheet_id')
        )
        result = processor.execute_pending_action(action_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions")
def get_actions(status: Optional[str] = None, limit: int = 100):
    """Get actions"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.*, e.subject, e.sender, c.category_name
            FROM actions a
            JOIN emails e ON a.email_id = e.id
            LEFT JOIN classifications c ON a.classification_id = c.id
        '''
        
        params = []
        if status:
            query += ' WHERE a.status = ?'
            params.append(status)
        
        query += ' ORDER BY a.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        actions = [dict(zip(columns, row)) for row in rows]
        return {"actions": actions, "count": len(actions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def get_categories():
    """Get all categories"""
    try:
        categories = db.get_all_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories")
def create_category(category: CategoryCreateRequest):
    """Create a new category"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, description, keywords, action_type, target, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category.name, category.description, category.keywords, 
              category.action_type, category.target, category.is_active))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"id": category_id, "message": "Category created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
def get_statistics():
    """Get statistics"""
    try:
        stats = db.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/{key}")
def get_config(key: str):
    """Get configuration value"""
    try:
        value = db.get_config(key)
        return {"key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/{key}")
def set_config(key: str, value: str):
    """Set configuration value"""
    try:
        db.set_config(key, value)
        return {"key": key, "value": value, "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

