# How to Download credentials.json from Google Cloud Console

## Step-by-Step Guide

### Step 1: Create or Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top (next to "Google Cloud")
4. Either:
   - **Select an existing project**, OR
   - **Click "New Project"** to create one:
     - Enter project name (e.g., "Email Bot")
     - Click "Create"
     - Wait for project creation (may take a minute)

### Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **"APIs & Services"** > **"Library"**
   - You can also search for "APIs & Services" in the top search bar
2. In the search box, type **"Gmail API"**
3. Click on **"Gmail API"** from the results
4. Click the **"Enable"** button
5. Wait for the API to be enabled (usually takes a few seconds)

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** > **"OAuth consent screen"**
2. Select **"External"** (unless you have a Google Workspace account, then use "Internal")
3. Click **"Create"**
4. Fill in the required information:
   - **App name**: "Email Understanding Bot" (or any name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click **"Save and Continue"**
6. On the "Scopes" page, click **"Save and Continue"** (no need to add scopes here)
7. On the "Test users" page:
   - Click **"Add Users"**
   - Add your Gmail address
   - Click **"Save and Continue"**
8. Click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, select **"Desktop app"** as the application type
5. Enter a name: **"Email Bot Client"** (or any name)
6. Click **"Create"**
7. A popup will appear with your **Client ID** and **Client Secret**
   - **IMPORTANT**: Copy these values (you'll need them)
   - Click **"OK"**

### Step 5: Download credentials.json

**Option A: Direct Download (Recommended)**

1. In the **"Credentials"** page, find your newly created OAuth 2.0 Client ID
2. Click on the **download icon** (⬇️) next to your client ID
   - OR click on the client ID name, then click **"Download JSON"**
3. The file will be downloaded (usually named something like `client_secret_xxxxx.json`)
4. **Rename the file to `credentials.json`**
5. **Move it to your project root directory** (same folder as `email_bot_ui.py`)

**Option B: Manual Creation**

If you can't download directly, create `credentials.json` manually:

1. Create a new file named `credentials.json` in your project root
2. Copy and paste this structure:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

3. Replace:
   - `YOUR_CLIENT_ID` with your actual Client ID
   - `YOUR_CLIENT_SECRET` with your actual Client Secret
   - `your-project-id` with your Google Cloud project ID

### Step 6: Verify File Location

Your project structure should look like this:

```
your-project/
├── credentials.json          ← Should be here
├── email_bot_ui.py
├── email_processor.py
├── gmail_service.py
└── ... (other files)
```

### Step 7: Test Authentication

1. Run the email bot:
   ```bash
   streamlit run email_bot_ui.py
   ```

2. Go to the **"Emails"** tab
3. Click **"Process Unread Emails"**
4. A browser window will open asking you to:
   - Sign in to Google
   - Grant permissions to the app
   - Click "Allow"
5. After authorization, a `token.pickle` file will be created
6. The authentication is complete!

## Troubleshooting

### "File not found: credentials.json"
- Make sure the file is named exactly `credentials.json` (not `credentials.json.txt`)
- Check that it's in the same directory as your Python scripts
- Verify the file path: `ls credentials.json` (Linux/Mac) or `dir credentials.json` (Windows)

### "Invalid credentials"
- Make sure you copied the Client ID and Client Secret correctly
- Check that the JSON format is valid (use a JSON validator)
- Ensure the OAuth consent screen is configured

### "Access blocked: This app's request is invalid"
- Make sure you added your email as a test user in OAuth consent screen
- If in production, you may need to verify your app with Google

### "Redirect URI mismatch"
- Make sure `redirect_uris` includes `http://localhost` in credentials.json
- In Google Cloud Console, add `http://localhost` to authorized redirect URIs

### "Gmail API not enabled"
- Go back to Step 2 and ensure Gmail API is enabled
- Wait a few minutes after enabling for it to propagate

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit `credentials.json` to version control
- Never commit `token.pickle` to version control
- Add both to `.gitignore`
- Keep these files secure and private

## Quick Checklist

- [ ] Google Cloud project created/selected
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 credentials created (Desktop app type)
- [ ] credentials.json downloaded/created
- [ ] File placed in project root
- [ ] Test user added (your email)
- [ ] Authentication tested successfully

## Next Steps

After setting up credentials.json:

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. Run the application:
   ```bash
   streamlit run email_bot_ui.py
   ```

3. Process your first email!

## Visual Guide Locations

- **APIs & Services**: Left sidebar menu → "APIs & Services"
- **Credentials**: APIs & Services → "Credentials" (left sidebar)
- **OAuth consent screen**: APIs & Services → "OAuth consent screen" (left sidebar)
- **API Library**: APIs & Services → "Library" (left sidebar)

## Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify each step was completed
3. Check Google Cloud Console for any warnings
4. Review the troubleshooting section above

