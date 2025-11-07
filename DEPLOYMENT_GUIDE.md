# Deployment Guide - Invoice QA Agent

This guide explains how to deploy your Invoice QA Agent application so others can access it online.

---

## 🚀 Deployment Options

There are several ways to deploy your application. We'll cover the easiest options first.

---

## Option 1: Streamlit Cloud (Easiest - Recommended for Beginners)

**Best for:** Quick deployment, free hosting, easy setup

### Prerequisites
- A GitHub account (free)
- Your code pushed to GitHub

### Steps:

#### Step 1: Create GitHub Account (if you don't have one)
1. Go to https://github.com
2. Sign up for a free account
3. Verify your email

#### Step 2: Create a GitHub Repository
1. Log in to GitHub
2. Click the "+" icon in top right → "New repository"
3. Name it: `invoice-qa-agent` (or any name you like)
4. Make it **Public** (required for free Streamlit Cloud)
5. Click "Create repository"

#### Step 3: Upload Your Code to GitHub

**Option A: Using GitHub Website (Easiest)**
1. In your new repository, click "uploading an existing file"
2. Upload all your project files:
   - `app.py`
   - `file_parser.py`
   - `ai_agent.py`
   - `output_generator.py`
   - `visualization.py`
   - `database.py`
   - `file_storage.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`
3. Click "Commit changes"

**Option B: Using Git Command Line**
```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/invoice-qa-agent.git
git push -u origin main
```

#### Step 4: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "Sign in" and log in with GitHub
3. Click "New app"
4. Select your repository: `invoice-qa-agent`
5. Select branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

#### Step 5: Configure Environment Variables (Optional)
1. In Streamlit Cloud, go to your app settings
2. Click "Secrets" (for API keys)
3. Add your OpenAI API key if needed:
   ```
   OPENAI_API_KEY=your-key-here
   ```

**That's it!** Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Option 2: Heroku (Popular Cloud Platform)

**Best for:** More control, can use private repos, professional hosting

### Steps:

#### Step 1: Install Heroku CLI
1. Download from: https://devcenter.heroku.com/articles/heroku-cli
2. Install and verify: `heroku --version`

#### Step 2: Create Required Files

**Create `Procfile`** (no extension):
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Create `setup.sh`**:
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Update `requirements.txt`** (add at the end):
```
gunicorn==21.2.0
```

#### Step 3: Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set buildpack
heroku buildpacks:set heroku/python

# Push code
git push heroku main

# Open app
heroku open
```

#### Step 4: Set Environment Variables
```bash
heroku config:set OPENAI_API_KEY=your-key-here
```

---

## Option 3: Docker Deployment

**Best for:** Consistent deployment across different servers

### Steps:

#### Step 1: Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Create `docker-compose.yml`
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./uploads:/app/uploads
      - ./invoice_qa.db:/app/invoice_qa.db
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

#### Step 3: Build and Run
```bash
docker-compose up -d
```

---

## Option 4: Deploy on Your Own Server

**Best for:** Full control, private hosting

### Steps:

#### Step 1: Set Up Server
- Get a VPS (Virtual Private Server) from:
  - DigitalOcean
  - AWS EC2
  - Azure VM
  - Google Cloud Compute Engine

#### Step 2: Install Dependencies on Server
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip -y

# Install nginx (web server)
sudo apt install nginx -y
```

#### Step 3: Upload Your Code
```bash
# Using SCP or SFTP, upload your project folder
# Or use Git to clone your repository
git clone https://github.com/YOUR_USERNAME/invoice-qa-agent.git
cd invoice-qa-agent
```

#### Step 4: Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

#### Step 5: Run Application
```bash
# Run in background
nohup streamlit run app.py --server.port=8501 &

# Or use systemd service (better for production)
```

#### Step 6: Configure Nginx (Optional - for custom domain)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Option 5: Railway (Modern Platform)

**Best for:** Easy deployment, good free tier

### Steps:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Streamlit
6. Add environment variables if needed
7. Deploy!

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] All files are in the repository
- [ ] `requirements.txt` is up to date
- [ ] `.gitignore` excludes sensitive files
- [ ] Database file (`invoice_qa.db`) is in `.gitignore` (will be created fresh)
- [ ] Uploads folder is in `.gitignore`
- [ ] No hardcoded API keys in code
- [ ] Test the app locally first

---

## 🔒 Security Considerations

### Important Security Steps:

1. **Never commit sensitive data:**
   - API keys
   - Database files with real data
   - User passwords

2. **Use environment variables:**
   - Store API keys as environment variables
   - Never hardcode them in files

3. **Update `.gitignore`:**
   ```
   # Add these to .gitignore
   invoice_qa.db
   uploads/
   *.db
   .env
   __pycache__/
   ```

4. **Password Security:**
   - The app uses SHA256 hashing (good)
   - For production, consider stronger hashing (bcrypt)

---

## 🌐 Domain Setup (Optional)

If you want a custom domain (e.g., `invoice-qa.yourcompany.com`):

1. **Streamlit Cloud:**
   - Go to app settings
   - Add custom domain
   - Update DNS records

2. **Heroku:**
   ```bash
   heroku domains:add your-domain.com
   ```
   Then update DNS records

---

## 📊 Monitoring & Maintenance

### After Deployment:

1. **Monitor Logs:**
   - Streamlit Cloud: View logs in dashboard
   - Heroku: `heroku logs --tail`
   - Docker: `docker-compose logs -f`

2. **Check Performance:**
   - Monitor response times
   - Check database size
   - Monitor file storage

3. **Regular Updates:**
   - Update dependencies: `pip install --upgrade -r requirements.txt`
   - Update code and redeploy

---

## 🆘 Troubleshooting

### Common Issues:

**Issue: App won't start**
- Check logs for errors
- Verify all dependencies in `requirements.txt`
- Check Python version (needs 3.8+)

**Issue: Database errors**
- Ensure database file is writable
- Check file permissions

**Issue: File uploads not working**
- Check uploads folder exists
- Verify folder permissions

**Issue: API key not working**
- Verify environment variable is set correctly
- Check API key is valid

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **Streamlit Cloud** | Yes (public repos) | $20/month (private) | Beginners |
| **Heroku** | Limited | $7+/month | Professionals |
| **Railway** | $5 credit/month | Pay as you go | Modern apps |
| **AWS/Azure/GCP** | Limited | Varies | Enterprise |
| **Your Server** | Server cost only | $5-20/month | Full control |

---

## 🎯 Recommended Approach for Beginners

**Start with Streamlit Cloud:**
1. ✅ Easiest to set up
2. ✅ Free for public repos
3. ✅ Automatic deployments
4. ✅ Built for Streamlit apps
5. ✅ No server management needed

**Steps Summary:**
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy in 2 minutes
4. Share the link!

---

## 📝 Quick Start Commands

### For Streamlit Cloud:
```bash
# Just push to GitHub, then deploy via web interface
git push origin main
```

### For Heroku:
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### For Docker:
```bash
docker-compose up -d
```

---

## 🔗 Useful Links

- Streamlit Cloud: https://share.streamlit.io
- Heroku: https://www.heroku.com
- Railway: https://railway.app
- GitHub: https://github.com
- Docker: https://www.docker.com

---

## 📞 Need Help?

If you encounter issues:
1. Check the error logs
2. Verify all files are uploaded
3. Ensure `requirements.txt` is correct
4. Check environment variables are set
5. Review the troubleshooting section above

---

*Good luck with your deployment! 🚀*

