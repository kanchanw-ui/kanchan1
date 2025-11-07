# Quick Fix for Deployment Error

## Error: metadata-generation-failed

### Immediate Solution (Try This First):

1. **Update the requirements.txt file** - I've already updated it with more flexible versions

2. **If deploying on Streamlit Cloud:**
   - Make sure you have `runtime.txt` file (I've created it)
   - It specifies Python 3.11

3. **Try this command locally first:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

---

## Alternative: Use Minimal Requirements

If the main `requirements.txt` still fails, use `requirements-minimal.txt`:

1. **Rename files:**
   ```bash
   mv requirements.txt requirements-full.txt
   mv requirements-minimal.txt requirements.txt
   ```

2. **Commit and push:**
   ```bash
   git add requirements.txt
   git commit -m "Use minimal requirements for deployment"
   git push
   ```

---

## For Streamlit Cloud:

1. **Make sure these files are in your repo:**
   - ✅ `requirements.txt` (updated)
   - ✅ `runtime.txt` (created - specifies Python 3.11)
   - ✅ `app.py`
   - ✅ All other Python files

2. **In Streamlit Cloud:**
   - Go to your app settings
   - Check "Advanced settings"
   - Python version should be 3.11 (or let it auto-detect)

3. **Redeploy:**
   - Streamlit Cloud will automatically redeploy when you push changes
   - Or click "Reboot app" in settings

---

## Common Causes & Fixes:

### Cause 1: Old package versions
**Fix:** ✅ Already updated requirements.txt with `>=` instead of `==`

### Cause 2: Missing Python version
**Fix:** ✅ Created `runtime.txt` with `python-3.11`

### Cause 3: Build dependencies missing
**Fix:** Streamlit Cloud handles this automatically

### Cause 4: Specific package failing
**Fix:** Check build logs to see which package, then:
- Try installing it separately
- Use a different version
- Remove it if not critical

---

## Step-by-Step Fix:

1. **Pull the updated files:**
   - `requirements.txt` (updated)
   - `runtime.txt` (new)
   - `pyproject.toml` (new - helps with builds)

2. **Test locally:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **If local install works, push to GitHub:**
   ```bash
   git add requirements.txt runtime.txt pyproject.toml
   git commit -m "Fix deployment requirements"
   git push
   ```

4. **Redeploy on Streamlit Cloud:**
   - It will automatically rebuild
   - Check logs if it still fails

---

## Still Failing?

1. **Check the build logs** - they'll show which package is failing
2. **Try the minimal requirements** (requirements-minimal.txt)
3. **Remove problematic packages temporarily** - add them back one by one
4. **Check DEPLOYMENT_TROUBLESHOOTING.md** for detailed solutions

---

## Quick Test:

Run this to verify requirements are valid:
```bash
pip install --dry-run -r requirements.txt
```

This will show if there are any obvious issues without actually installing.

---

**The updated files should fix most deployment issues!**

