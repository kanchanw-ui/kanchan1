# Email Understanding & Action Bot

An AI-powered email assistant that reads incoming emails, classifies them using LLM, and performs automated actions based on the classification.

## Features

- 📧 **Gmail Integration**: Read and process emails from Gmail
- 🤖 **AI Classification**: Uses GPT-4 to classify emails into predefined categories
- ⚡ **Automated Actions**: Execute actions like forwarding, creating tickets, updating HR systems
- 📊 **Dashboard**: View statistics and manage emails through a web interface
- 🔔 **Slack Integration**: Send notifications to Slack channels
- 📈 **Google Sheets Logging**: Log emails and classifications to Google Sheets
- 🎯 **Justification**: Provides clear reasoning for each classification

## Architecture

### Components

1. **Database** (`email_bot_database.py`): SQLite database for storing emails, classifications, and actions
2. **Gmail Service** (`gmail_service.py`): Handles Gmail API authentication and email retrieval
3. **Email Classifier** (`email_classifier.py`): LLM-based email classification service
4. **Action Executor** (`action_executor.py`): Executes actions (Slack, Sheets, forwarding, etc.)
5. **Email Processor** (`email_processor.py`): Main service that orchestrates email processing
6. **API Server** (`api_server.py`): FastAPI REST API for backend operations
7. **Streamlit UI** (`email_bot_ui.py`): Web interface for managing the bot
8. **Email Poller** (`email_poller.py`): Background service for continuous email polling

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-email-bot.txt
```

### 2. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` and place it in the project root

### 3. Set Up OpenAI API

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or set it in the Streamlit UI under Settings.

### 4. Initialize Database

The database will be automatically created on first run. Default categories are pre-populated.

## Usage

### Option 1: Using Streamlit UI (Recommended)

```bash
streamlit run email_bot_ui.py
```

Access the UI at `http://localhost:8501`

### Option 2: Using API Server

Start the API server:

```bash
python api_server.py
```

Or with uvicorn:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

API documentation available at `http://localhost:8000/docs`

### Option 3: Background Email Poller

Run the email poller service:

```bash
python email_poller.py
```

This will continuously poll Gmail for new emails and process them automatically.

## Configuration

### Default Categories

The system comes with 8 predefined categories:

1. **Invoice Attached** → Forward to finance
2. **Leave Request** → Update HR system
3. **Meeting Request** → Add to calendar
4. **Support Ticket** → Create ticket
5. **Purchase Order** → Forward to procurement
6. **Expense Report** → Forward to finance
7. **Contract Review** → Forward to legal
8. **General Inquiry** → Auto-reply

### Adding Custom Categories

1. Go to the "Categories" tab in the UI
2. Fill in the category details:
   - Name
   - Description
   - Keywords (comma-separated)
   - Action Type
   - Target

### Configuring Integrations

#### Slack

1. Create a Slack webhook URL
2. Go to Settings in the UI
3. Enter the webhook URL
4. Save

#### Google Sheets

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a service account
4. Download credentials JSON
5. Share your spreadsheet with the service account email
6. Enter the spreadsheet ID in Settings

## API Endpoints

### GET `/emails`
Get all emails with classifications

### GET `/emails/{email_id}`
Get detailed email information

### POST `/emails/process`
Process unread emails from Gmail

### POST `/actions/{action_id}/execute`
Execute a pending action

### GET `/actions`
Get all actions

### GET `/categories`
Get all categories

### POST `/categories`
Create a new category

### GET `/statistics`
Get system statistics

## Example Email Classifications

### Example 1: Invoice Email
**Email Subject:** "Invoice #12345 - Payment Due"
**Email Body:** "Please find attached invoice for services rendered. Due date: 2024-12-31. Amount: $5,000."

**Classification:**
- Category: Invoice Attached
- Confidence: 0.95
- Justification: "Email mentions invoice, due date, and payment terms"
- Action: Forward to finance@example.com

### Example 2: Leave Request
**Email Subject:** "Vacation Request - Dec 20-27"
**Email Body:** "I would like to request time off for vacation from December 20 to December 27."

**Classification:**
- Category: Leave Request
- Confidence: 0.92
- Justification: "Email contains vacation request with specific dates"
- Action: Update HR system

## Testing

### Test with Sample Emails

You can test the system by:

1. Sending test emails to your Gmail account
2. Using the "Process Unread Emails" button in the UI
3. Reviewing classifications and actions

### Test Classification

```python
from email_classifier import EmailClassifier
from email_bot_database import EmailBotDatabase

classifier = EmailClassifier(api_key="your-key")
db = EmailBotDatabase()
categories = db.get_all_categories()

email_data = {
    "subject": "Invoice #12345",
    "body": "Please find attached invoice. Due date: 2024-12-31.",
    "sender": "vendor@example.com"
}

result = classifier.classify_email(email_data, categories)
print(result)
```

## Troubleshooting

### Gmail Authentication Issues

- Ensure `credentials.json` is in the project root
- Delete `token.pickle` and re-authenticate
- Check that Gmail API is enabled in Google Cloud Console

### OpenAI API Errors

- Verify your API key is correct
- Check your API quota/limits
- Ensure you have credits in your OpenAI account

### Database Issues

- Delete `email_bot.db` to reset the database
- Check file permissions

## Security Notes

- Never commit `credentials.json` or `token.pickle` to version control
- Store API keys in environment variables
- Use `.env` files for local development (not included in repo)

## License

This project is provided as-is for demonstration purposes.

## Support

For issues or questions, please check:
1. API documentation at `/docs` endpoint
2. Database schema in `email_bot_database.py`
3. Error logs in the console output

