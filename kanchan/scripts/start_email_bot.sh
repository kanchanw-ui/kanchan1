#!/bin/bash

# Email Understanding & Action Bot Startup Script

echo "Starting Email Understanding & Action Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-email-bot.txt

# Check for credentials.json
if [ ! -f "credentials.json" ]; then
    echo "WARNING: credentials.json not found!"
    echo "Please download Gmail API credentials from Google Cloud Console"
    echo "and save as credentials.json in the project root"
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set!"
    echo "Please set it with: export OPENAI_API_KEY='your-key'"
fi

# Initialize database
echo "Initializing database..."
python -c "from email_bot_database import EmailBotDatabase; EmailBotDatabase()"
echo "Database initialized!"

# Start API server in background
echo "Starting API server..."
python api_server.py &
API_PID=$!
echo "API server started (PID: $API_PID)"

# Wait a moment for API to start
sleep 3

# Start Streamlit UI
echo "Starting Streamlit UI..."
echo "Access the UI at: http://localhost:8501"
streamlit run email_bot_ui.py

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT

