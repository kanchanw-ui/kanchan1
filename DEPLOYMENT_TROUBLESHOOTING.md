# Deployment Troubleshooting Guide

## Error: metadata-generation-failed

This error occurs when pip cannot build/install packages. Here are solutions:

---

## Solution 1: Update Package Versions (Recommended)

The `requirements.txt` has been updated with more flexible version constraints. Try:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Solution 2: Install Build Dependencies First

Some packages need build tools. Install them first:

```bash
# For Linux/Ubuntu
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# For macOS
xcode-select --install

# For Windows
# Install Visual Studio Build Tools
```

Then install requirements:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Solution 3: Install Packages Individually

If bulk install fails, install packages one by one to identify the problematic one:

```bash
pip install streamlit
pip install pandas
pip install openpyxl
pip install pdfplumber
pip install reportlab
pip install Pillow
pip install matplotlib
pip install seaborn
pip install plotly
pip install langchain
pip install langchain-openai
pip install openai
pip install streamlit-option-menu
pip install gunicorn
pip install python-multipart
```

---

## Solution 4: Use Specific Compatible Versions

If you're deploying on Streamlit Cloud, try this `requirements.txt`:

```txt
streamlit==1.28.1
pandas==2.1.4
openpyxl==3.1.2
pdfplumber==0.10.3
pypdf2==3.0.1
reportlab==4.0.7
Pillow==10.1.0
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0
langchain==0.1.0
langchain-openai==0.0.2
openai==1.6.1
streamlit-option-menu==0.3.12
gunicorn==21.2.0
python-multipart==0.0.6
python-docx==1.1.0
numpy==1.24.3
```

---

## Solution 5: For Streamlit Cloud Specific Issues

### Issue: Build fails on Streamlit Cloud

1. **Check Python Version:**
   - Create `runtime.txt` with: `python-3.11`
   - Or use: `python-3.10`

2. **Simplify requirements.txt:**
   - Remove version pins that might conflict
   - Use `>=` instead of `==` for flexibility

3. **Check Logs:**
   - In Streamlit Cloud dashboard, check build logs
   - Look for specific package causing the error

---

## Solution 6: For Heroku Deployment

### Add buildpacks:
```bash
heroku buildpacks:add heroku/python
```

### Set Python version:
```bash
heroku config:set PYTHON_VERSION=3.11.0
```

### Or create `runtime.txt`:
```
python-3.11.0
```

---

## Solution 7: Common Problematic Packages

### reportlab + Pillow
These often cause metadata errors. Try:

```bash
pip install --upgrade Pillow
pip install reportlab --no-cache-dir
```

### langchain
Sometimes needs specific versions:

```bash
pip install langchain==0.1.0
pip install langchain-openai==0.0.2
```

### pdfplumber
May need system dependencies:

```bash
# Linux
sudo apt-get install libmagic1

# Then install
pip install pdfplumber
```

---

## Solution 8: Clean Install

If nothing works, try a clean install:

```bash
# Remove old packages
pip uninstall -y -r requirements.txt

# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install fresh
pip install -r requirements.txt
```

---

## Solution 9: Use Virtual Environment

Always use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## Solution 10: Minimal Requirements (Last Resort)

If all else fails, use this minimal `requirements.txt`:

```txt
streamlit
pandas
openpyxl
pdfplumber
reportlab
Pillow
matplotlib
plotly
langchain
langchain-openai
openai
streamlit-option-menu
```

Then add other packages as needed.

---

## Platform-Specific Solutions

### Streamlit Cloud
- Use Python 3.10 or 3.11
- Don't pin exact versions unless necessary
- Check build logs for specific errors

### Heroku
- Add `runtime.txt` with Python version
- Use `Procfile` for process definition
- Check Heroku logs: `heroku logs --tail`

### Docker
- Use Python 3.11 base image
- Install build dependencies in Dockerfile
- Use multi-stage build if needed

### Railway
- Usually auto-detects Python
- Check build logs
- May need `runtime.txt`

---

## Getting More Details

To see the full error:

```bash
pip install -r requirements.txt --verbose
```

Or for a specific package:
```bash
pip install reportlab --verbose --no-cache-dir
```

---

## Quick Fix Checklist

- [ ] Updated pip: `pip install --upgrade pip`
- [ ] Updated setuptools: `pip install --upgrade setuptools wheel`
- [ ] Using virtual environment
- [ ] Python version is 3.8+
- [ ] Build tools installed (if needed)
- [ ] Checked specific error in logs
- [ ] Tried installing packages individually
- [ ] Cleared pip cache

---

## Still Having Issues?

1. **Check the specific error message** - it usually tells you which package is failing
2. **Try installing that package separately** with verbose output
3. **Check package documentation** for specific requirements
4. **Use Google** to search the exact error message

---

## Example: Fixing reportlab Error

If reportlab fails:

```bash
# Upgrade Pillow first
pip install --upgrade Pillow

# Install reportlab with no cache
pip install reportlab --no-cache-dir --force-reinstall

# Or try specific version
pip install reportlab==4.0.7 --no-cache-dir
```

---

*Most metadata errors are resolved by upgrading pip, setuptools, and using compatible package versions.*

