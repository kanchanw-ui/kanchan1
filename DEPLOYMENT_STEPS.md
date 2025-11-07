# Quick Deployment Steps - Invoice QA Agent

## 🚀 Easiest Method: Streamlit Cloud (5 Minutes)

### Step 1: Prepare Your Code
1. Make sure all files are in your project folder
2. Check that `.gitignore` includes:
   - `*.db` (database files)
   - `uploads/` (uploaded files)
   - `.env` (environment variables)

### Step 2: Create GitHub Repository
1. Go to https://github.com and sign in
2. Click **"+"** → **"New repository"**
3. Name: `invoice-qa-agent`
4. Make it **Public**
5. Click **"Create repository"**

### Step 3: Upload Files to GitHub
1. In your repository, click **"uploading an existing file"**
2. Upload these files:
   ```
   app.py
   file_parser.py
   ai_agent.py
   output_generator.py
   visualization.py
   database.py
   file_storage.py
   requirements.txt
   .gitignore
   README.md
   ```
3. Click **"Commit changes"**

### Step 4: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click **"Sign in"** → Log in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository:** Select `invoice-qa-agent`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy"**

### Step 5: Configure (Optional)
1. In app settings, click **"Secrets"**
2. Add your OpenAI API key (if you have one):
   ```
   OPENAI_API_KEY = "your-key-here"
   ```

**Done!** Your app is live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 📦 Alternative: Deploy with Docker

### Step 1: Build Docker Image
```bash
docker build -t invoice-qa-agent .
```

### Step 2: Run Container
```bash
docker run -d -p 8501:8501 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/invoice_qa.db:/app/invoice_qa.db \
  -e OPENAI_API_KEY=your-key-here \
  invoice-qa-agent
```

### Step 3: Access App
Open browser: http://localhost:8501

---

## ☁️ Alternative: Deploy on Heroku

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login
```bash
heroku login
```

### Step 3: Create App
```bash
heroku create your-app-name
```

### Step 4: Deploy
```bash
git push heroku main
```

### Step 5: Set API Key (Optional)
```bash
heroku config:set OPENAI_API_KEY=your-key-here
```

### Step 6: Open App
```bash
heroku open
```

---

## ✅ Post-Deployment Checklist

- [ ] App loads without errors
- [ ] Can create user account
- [ ] Can upload files
- [ ] Analysis works correctly
- [ ] Can download reports
- [ ] History tab shows past uploads

---

## 🔧 Common Issues & Solutions

**Issue:** App shows "ModuleNotFoundError"
- **Solution:** Check `requirements.txt` has all packages

**Issue:** Database errors
- **Solution:** Database will be created automatically on first run

**Issue:** File uploads fail
- **Solution:** Ensure `uploads/` folder has write permissions

**Issue:** API key not working
- **Solution:** Check environment variable is set correctly

---

## 📞 Need Help?

1. Check application logs
2. Verify all files are uploaded
3. Test locally first: `streamlit run app.py`
4. Review error messages

---

*Your application is ready to deploy! 🎉*

