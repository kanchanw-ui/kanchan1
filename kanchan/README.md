# Email Understanding & Action Bot

An AI-powered email assistant that reads incoming emails, classifies them using LLM, and performs automated actions.

## 📁 Folder Structure

```
kanchan/
├── Core Services/
│   ├── email_bot_database.py      # Database operations
│   ├── gmail_service.py           # Gmail API integration
│   ├── email_classifier.py        # LLM classification
│   ├── action_executor.py         # Action execution
│   └── email_processor.py         # Main orchestrator
│
├── API & UI/
│   ├── api_server.py              # FastAPI REST API
│   └── email_bot_ui.py            # Streamlit UI
│
├── Services/
│   └── email_poller.py            # Background poller
│
├── scripts/
│   └── start_email_bot.sh         # Startup script
│
├── docs/
│   ├── EMAIL_BOT_README.md        # Full documentation
│   ├── EMAIL_BOT_SUMMARY.md       # Solution overview
│   ├── QUICK_START_EMAIL_BOT.md   # Quick start guide
│   ├── GMAIL_CREDENTIALS_SETUP.md # Gmail setup guide
│   └── download_credentials_guide.html # Visual guide
│
├── credentials_template.json      # Gmail credentials template
├── requirements-email-bot.txt      # Dependencies
├── test_email_bot.py              # Test script
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-email-bot.txt
```

### 2. Set Up Gmail API

1. Download `credentials.json` from Google Cloud Console
2. See `docs/GMAIL_CREDENTIALS_SETUP.md` for detailed instructions
3. Place `credentials.json` in this folder

### 3. Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 4. Run the Application

```bash
streamlit run email_bot_ui.py
```

Or use the startup script:

```bash
bash scripts/start_email_bot.sh
```

## 📚 Documentation

- **Full Guide**: `docs/EMAIL_BOT_README.md`
- **Quick Start**: `docs/QUICK_START_EMAIL_BOT.md`
- **Gmail Setup**: `docs/GMAIL_CREDENTIALS_SETUP.md`
- **Solution Summary**: `docs/EMAIL_BOT_SUMMARY.md`

## 🧪 Testing

Run the test script to verify classification:

```bash
python test_email_bot.py
```

## 🔧 Features

- ✅ Gmail API Integration
- ✅ LLM-based Email Classification (GPT-4)
- ✅ Automated Action Execution
- ✅ Slack Integration
- ✅ Google Sheets Logging
- ✅ Web UI Dashboard
- ✅ REST API
- ✅ Background Email Polling

## 📋 Default Categories

1. Invoice Attached → Forward to finance
2. Leave Request → Update HR system
3. Meeting Request → Add to calendar
4. Support Ticket → Create ticket
5. Purchase Order → Forward to procurement
6. Expense Report → Forward to finance
7. Contract Review → Forward to legal
8. General Inquiry → Auto-reply

## 🔐 Security

⚠️ **Never commit these files:**
- `credentials.json`
- `token.pickle`
- `email_bot.db`

They are already in `.gitignore`.

## 📞 Support

For issues or questions, check the documentation in the `docs/` folder.

