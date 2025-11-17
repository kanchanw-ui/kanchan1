# Quick Start Guide - Email Understanding & Action Bot

## Prerequisites

1. Python 3.8+
2. Gmail account
3. OpenAI API key
4. Google Cloud project (for Gmail API)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements-email-bot.txt
```

### 2. Set Up Gmail API

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Email Bot"
   - Click "Create"
   - Download the JSON file
   - Rename it to `credentials.json` and place in project root

### 3. Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or set it in the UI later.

### 4. Initialize Database

The database will be created automatically on first run. To manually initialize:

```python
from email_bot_database import EmailBotDatabase
db = EmailBotDatabase()
```

### 5. Run the Application

#### Option A: Streamlit UI (Recommended for first-time users)

```bash
streamlit run email_bot_ui.py
```

Then:
1. Go to http://localhost:8501
2. Go to Settings tab
3. Configure your API keys
4. Go to Emails tab
5. Click "Process Unread Emails"
6. First time: Gmail will open in browser for authentication

#### Option B: API Server + UI

Terminal 1 - Start API:
```bash
python api_server.py
```

Terminal 2 - Start UI:
```bash
streamlit run email_bot_ui.py
```

#### Option C: Background Poller

```bash
python email_poller.py
```

This continuously polls Gmail and processes emails automatically.

### 6. Test the System

Run the test script with 10 sample emails:

```bash
python test_email_bot.py
```

This will test classification accuracy with various email types.

## First-Time Gmail Authentication

When you first process emails, Gmail will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permissions to read/send emails
4. Save authentication token to `token.pickle`

**Note:** Keep `token.pickle` secure and don't commit it to git!

## Usage Examples

### Process Unread Emails via API

```bash
curl -X POST http://localhost:8000/emails/process \
  -H "Content-Type: application/json" \
  -d '{"auto_execute": false}'
```

### Get All Emails

```bash
curl http://localhost:8000/emails
```

### Execute a Pending Action

```bash
curl -X POST http://localhost:8000/actions/1/execute
```

## Configuration

### Slack Integration

1. Create a Slack webhook:
   - Go to https://api.slack.com/apps
   - Create new app
   - Enable "Incoming Webhooks"
   - Add webhook to workspace
   - Copy webhook URL

2. In UI Settings, paste the webhook URL

### Google Sheets Integration

1. Create a Google Cloud service account:
   - Go to Google Cloud Console
   - Create service account
   - Download JSON credentials
   - Share your spreadsheet with service account email

2. In UI Settings:
   - Upload service account JSON
   - Enter spreadsheet ID

## Troubleshooting

### "Gmail API not authenticated"

- Delete `token.pickle` and re-authenticate
- Check that `credentials.json` exists and is valid

### "OpenAI API error"

- Verify API key is correct
- Check you have credits/quota
- Try a different model (edit `email_classifier.py`)

### "Database locked"

- Close other connections to the database
- Restart the application

### "No emails found"

- Check Gmail query in `gmail_service.py`
- Verify you have unread emails
- Check Gmail API permissions

## Next Steps

1. **Customize Categories**: Add your own categories in the UI
2. **Set Up Actions**: Configure Slack, Sheets, or other integrations
3. **Enable Auto-Execute**: Toggle auto-execution in Settings
4. **Monitor**: Check Dashboard for statistics
5. **Review**: Manually review classifications in Emails tab

## File Structure

```
.
├── email_bot_database.py      # Database schema and operations
├── gmail_service.py           # Gmail API integration
├── email_classifier.py        # LLM-based classification
├── action_executor.py         # Action execution (Slack, Sheets, etc.)
├── email_processor.py         # Main processing orchestrator
├── api_server.py              # FastAPI REST API
├── email_bot_ui.py            # Streamlit web UI
├── email_poller.py            # Background polling service
├── test_email_bot.py          # Test script
├── requirements-email-bot.txt  # Dependencies
└── credentials.json           # Gmail OAuth credentials (not in repo)
```

## Support

For issues:
1. Check error messages in console
2. Review API docs at http://localhost:8000/docs
3. Check database with SQLite browser
4. Review logs in console output

