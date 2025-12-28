# Railway Email Debug Guide

## Current Issue
Password reset emails are not being sent from Railway deployment.

---

## Checklist: What to Verify

### ✅ 1. Railway Has Latest Code

Check if Railway deployed the latest commit with email service:

1. Go to: https://railway.app/
2. Open your project
3. Click on the backend service
4. Check **"Deployments"** tab
5. **Latest commit should be:** `b7b73c5` - "fix: Add email-based password reset..."
6. **Status should be:** "Active" (green)

**If not deployed yet:**
- Railway auto-deploys when you push to GitHub
- Wait 3-5 minutes after push
- Check "Build Logs" for errors

---

### ✅ 2. Environment Variables Are Set

1. In Railway dashboard → Your project → Backend service
2. Click **"Variables"** tab
3. **Verify these variables exist:**

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.actual.email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
FROM_EMAIL=your.actual.email@gmail.com
FROM_NAME=Physical AI Textbook
```

**Common Issues:**
- ❌ Variables not saved (click "Add" after each one)
- ❌ SMTP_PASSWORD has spaces removed (keep the spaces!)
- ❌ Wrong email/password
- ❌ Using regular Gmail password instead of App Password

**After adding/updating variables:**
- Railway will automatically restart
- Wait 1-2 minutes for restart

---

### ✅ 3. Check Railway Logs for Errors

1. In Railway → Backend service
2. Click **"Deployments"** tab
3. Click on the active deployment
4. Click **"View Logs"**
5. **Look for these messages:**

**Good signs:**
```
Email sent successfully to user@example.com
```

**Bad signs:**
```
WARNING: SMTP credentials not configured
Failed to send email: Authentication failed
Failed to send email: Connection refused
```

**How to trigger a password reset (to see logs):**
1. Go to your live site: https://mr-noiam.github.io/physical-ai-textbook/
2. Click "Login / Sign Up"
3. Click "Forgot password? Reset it"
4. Enter an email that exists in your database
5. Click "Send Reset Email"
6. **Immediately check Railway logs** (within 10 seconds)

---

### ✅ 4. Verify App Password is Correct

**Common mistakes:**
- Using regular Gmail password ❌
- Using App Password from a different app ❌
- Copying App Password without spaces ❌

**Correct format:**
```
App Password from Google: abcd efgh ijkl mnop
In Railway variable:      abcd efgh ijkl mnop  (keep spaces!)
```

**To generate new App Password:**
1. Visit: https://myaccount.google.com/apppasswords
2. Delete old "Physical AI Textbook" password
3. Create new App Password
4. Name: "Physical AI Textbook Backend"
5. Copy the 16-character password (with spaces)
6. Update in Railway Variables
7. Wait for Railway to restart

---

### ✅ 5. Check Gmail Security Settings

1. Go to: https://myaccount.google.com/security
2. **Verify:**
   - ✅ 2-Step Verification is ON
   - ✅ App Passwords section is visible
   - ✅ "Physical AI Textbook" App Password exists

3. Check recent security activity:
   - Visit: https://myaccount.google.com/notifications
   - Look for "blocked sign-in attempts"
   - If blocked: App Password might be wrong

---

### ✅ 6. Test with Railway CLI (Optional)

If you have Railway CLI installed:

```bash
# Install Railway CLI (if needed)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Check environment variables
railway variables

# View live logs
railway logs
```

---

## Quick Fix Steps

### If Email Still Not Working:

1. **Verify Railway Variables:**
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  ← Keep spaces!
   FROM_EMAIL=your.email@gmail.com
   FROM_NAME=Physical AI Textbook
   ```

2. **Generate Fresh App Password:**
   - Delete old one at: https://myaccount.google.com/apppasswords
   - Create new one
   - Update Railway variables
   - Wait 2 minutes for restart

3. **Check Deployment:**
   - Latest commit: `b7b73c5`
   - Status: Active (green)
   - No build errors

4. **Test Password Reset:**
   - Request reset on live site
   - Check Railway logs immediately
   - Look for error messages

5. **Check Email Inbox:**
   - Check spam folder
   - Check "All Mail" folder
   - Search for: "from:physical-ai-textbook"

---

## Debug Output to Share

If still not working, share these details:

### Railway Deployment Info:
- Latest commit hash: `_______`
- Deployment status: `_______`
- Build errors: `Yes / No`

### Environment Variables:
- SMTP_HOST: `_______`
- SMTP_PORT: `_______`
- SMTP_USER: `_______` (email address)
- SMTP_PASSWORD: `Set / Not Set` (don't share actual password!)
- FROM_EMAIL: `_______`

### Railway Logs (last 10 lines):
```
[Paste relevant log lines here]
```

### Test Results:
- Tested password reset: `Yes / No`
- Error message shown: `_______`
- Email received: `Yes / No`
- Checked spam folder: `Yes / No`

---

## Expected Behavior

### When Working Correctly:

1. **User requests password reset**
2. **Railway logs show:**
   ```
   Email sent successfully to user@example.com
   ```
3. **User receives email within 1-2 minutes**
4. **Email contains:**
   - Subject: "Reset Your Password - Physical AI Textbook"
   - From: "Physical AI Textbook <your.email@gmail.com>"
   - Button/link to reset password

---

## Alternative: SendGrid (If Gmail Doesn't Work)

If Gmail continues to have issues, you can use SendGrid (free tier):

1. Sign up: https://sendgrid.com/
2. Create API Key
3. Update Railway variables:
   ```
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=SG.your_api_key_here
   FROM_EMAIL=your.verified.email@example.com
   FROM_NAME=Physical AI Textbook
   ```

---

**Last Updated:** 2025-12-25
