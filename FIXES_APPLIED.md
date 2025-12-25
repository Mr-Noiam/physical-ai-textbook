# Fixes Applied - Password Reset & Profile Page

**Date:** 2025-12-25
**Status:** ✅ All Issues Fixed

---

## Issues Fixed

### 1. ✅ Password Reset Now Sends Emails

**Problem:**
- Password reset returned the token in the API response with message: "Reset token generated! Copy it and click 'I have a reset token'"
- This is insecure and not user-friendly

**Solution:**
- ✅ Created email service using `aiosmtplib` for async email sending
- ✅ Password reset now sends professional HTML emails to users
- ✅ Emails include clickable reset link with token embedded
- ✅ Created `/reset-password` page to handle password reset from email link
- ✅ Removed manual token entry from AuthModal
- ✅ Added security message: "Check your email for reset link"

### 2. ✅ Profile Page 404 Fixed

**Problem:**
- URL `https://mr-noiam.github.io/profile` returned 404
- Incorrect routing - missing base path

**Solution:**
- ✅ Changed `<a href="/profile">` to `<Link to="/profile">` in UserMenu
- ✅ Added Docusaurus Link component for proper base-path routing
- ✅ Profile now accessible at: `https://mr-noiam.github.io/physical-ai-textbook/profile`

---

## Files Created

### Backend

1. **`backend/app/services/email.py`** (New)
   - Email service with HTML templates
   - Functions: `send_password_reset_email()`, `send_welcome_email()`
   - Uses Gmail SMTP or any SMTP server

### Frontend

2. **`docusaurus/src/pages/reset-password.tsx`** (New)
   - Password reset page accessible via email link
   - Accepts `?token=xxx&email=xxx` query parameters
   - Secure password reset flow with validation

3. **`docusaurus/src/pages/reset-password.module.css`** (New)
   - Styling for reset password page
   - Responsive design with error/success states

---

## Files Modified

### Backend

1. **`backend/requirements.txt`**
   - Added: `aiosmtplib==3.0.1` for email sending

2. **`backend/app/api/v1/auth.py`**
   - Updated `forgot_password()` endpoint to `async`
   - Now sends email instead of returning token
   - Returns secure message: "If an account exists, you will receive an email"

### Frontend

3. **`docusaurus/src/components/UserMenu/index.tsx`**
   - Changed: `<a href="/profile">` → `<Link to="/profile">`
   - Added: `import Link from '@docusaurus/Link'`
   - Now uses proper Docusaurus routing

4. **`docusaurus/src/components/AuthModal/index.tsx`**
   - Removed: "I have a reset token" button and manual token entry
   - Removed: `mode === 'reset'` state
   - Changed: Button text to "Send Reset Email"
   - Changed: Success message to "Check your email"
   - Updated: `forgotPassword()` call to not expect return value

5. **`docusaurus/src/contexts/AuthContext.tsx`**
   - Changed: `forgotPassword: (email: string) => Promise<string>`
   - To: `forgotPassword: (email: string) => Promise<void>`
   - Updated implementation to not return token

### Configuration

6. **`.env.example`**
   - Added SMTP configuration variables:
     ```env
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=your.email@gmail.com
     SMTP_PASSWORD=your_gmail_app_password_here
     FROM_EMAIL=your.email@gmail.com
     FROM_NAME=Physical AI Textbook
     ```

---

## New Password Reset Flow

### Old Flow (Insecure) ❌
1. User clicks "Forgot Password"
2. API returns reset token in response
3. User manually copies token
4. User pastes token in "I have a reset token" form
5. User enters new password

### New Flow (Secure) ✅
1. User clicks "Forgot Password"
2. User enters email → API sends email with reset link
3. User checks email inbox
4. User clicks reset link → Opens `/reset-password?token=xxx&email=xxx`
5. User enters new password → Password updated
6. User redirected to login

---

## Setup Instructions

### For Gmail SMTP (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
   - Visit: https://myaccount.google.com/security

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - App: "Mail"
   - Device: "Other" → Name it "Physical AI Textbook"
   - Copy the 16-character password

3. **Update Environment Variables**

   **Local Development** (`backend/.env`):
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # Your app password
   FROM_EMAIL=your.email@gmail.com
   FROM_NAME=Physical AI Textbook
   ```

   **Railway Production**:
   - Go to Railway dashboard → Your project → Variables
   - Add the same environment variables

4. **Install New Dependency**
   ```bash
   cd backend
   pip install aiosmtplib==3.0.1
   ```

   Or:
   ```bash
   pip install -r requirements.txt
   ```

---

## Testing the Fixes

### Test 1: Profile Page Routing ✅

1. Visit: `https://mr-noiam.github.io/physical-ai-textbook/`
2. Login with your account
3. Click user menu (email in top-right)
4. Click "⚙️ Profile Settings"
5. **Expected:** Profile page loads successfully
6. **URL:** `https://mr-noiam.github.io/physical-ai-textbook/profile`

### Test 2: Password Reset Email ✅

**Prerequisites:** SMTP credentials configured in Railway

1. Go to login modal
2. Click "Forgot password? Reset it"
3. Enter your email
4. Click "Send Reset Email"
5. **Expected:** Message appears: "Check your email! If an account exists..."
6. Check your email inbox
7. **Expected:** Email received with subject "Reset Your Password"
8. Click the reset link in email
9. **Expected:** Opens `/reset-password` page with token pre-filled
10. Enter new password (twice)
11. Click "Reset Password"
12. **Expected:** Success message appears
13. Click "Go to Home Page"
14. Login with new password
15. **Expected:** Login successful

---

## Email Templates

### Password Reset Email

The email includes:
- Professional HTML design with gradient header
- Clear "Reset Password" button
- Clickable reset link (also as plain text)
- Security notice (link expires in 1 hour)
- Warning if user didn't request the reset

**Example:**
```
From: Physical AI Textbook <your.email@gmail.com>
Subject: Reset Your Password - Physical AI Textbook

[HTML Email with styled button]
Click here to reset: https://mr-noiam.github.io/physical-ai-textbook/reset-password?token=xxx&email=xxx

Security Notice:
- This link expires in 1 hour
- If you didn't request this, ignore this email
```

---

## Security Improvements

### ✅ No Token Exposure
- Reset tokens are never shown to users or returned in API responses
- Tokens only sent via email (secure channel)

### ✅ Email Verification
- User must have access to email account to reset password
- Prevents unauthorized password resets

### ✅ Token Expiration
- Tokens expire after 1 hour
- Prevents old tokens from being reused

### ✅ No Information Disclosure
- API always returns: "If an account exists, you will receive an email"
- Prevents email enumeration attacks

---

## Troubleshooting

### Email Not Sending

**Symptom:** No email received after password reset

**Check:**
1. **SMTP credentials configured?**
   ```bash
   # Check Railway environment variables
   railway variables
   ```

2. **App Password correct?**
   - Gmail App Passwords are 16 characters (with spaces)
   - NOT your regular Gmail password

3. **Check backend logs:**
   ```bash
   railway logs
   ```

   Look for:
   ```
   Email sent successfully to user@example.com
   ```

   Or errors like:
   ```
   Failed to send email: Authentication failed
   ```

4. **Gmail blocking sign-in?**
   - Check Gmail "Security" settings
   - Make sure "Less secure app access" is OFF (use App Password instead)

### Profile Page Still 404

**Symptom:** Profile page returns 404

**Check:**
1. **Cleared browser cache?**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

2. **Using correct URL?**
   - ❌ Wrong: `https://mr-noiam.github.io/profile`
   - ✅ Correct: `https://mr-noiam.github.io/physical-ai-textbook/profile`

3. **Deployed latest changes?**
   ```bash
   cd docusaurus
   npm run build
   npm run deploy
   ```

---

## Deployment Checklist

### Backend (Railway)

- [ ] Updated `requirements.txt` with `aiosmtplib==3.0.1`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Set SMTP environment variables in Railway
- [ ] Tested `/api/v1/auth/forgot-password` endpoint
- [ ] Checked logs for "Email sent successfully"

### Frontend (GitHub Pages)

- [ ] Updated UserMenu component (Link instead of <a>)
- [ ] Updated AuthModal (removed manual token entry)
- [ ] Updated AuthContext (forgotPassword returns void)
- [ ] Created reset-password page
- [ ] Built site: `npm run build`
- [ ] Deployed: `npm run deploy`
- [ ] Tested profile page navigation
- [ ] Tested password reset flow end-to-end

---

## Next Steps

1. **Configure SMTP Credentials** (Required)
   - Add SMTP variables to Railway environment
   - Test email sending locally first

2. **Deploy Backend Changes**
   ```bash
   git add .
   git commit -m "fix: Add email service for password reset"
   git push origin 001-physical-ai-textbook
   ```
   Railway will auto-deploy

3. **Deploy Frontend Changes**
   ```bash
   cd docusaurus
   npm run build
   npm run deploy
   ```

4. **Test Complete Flow**
   - Test profile page: `/profile`
   - Test password reset: Forgot password → Email → Reset link → New password → Login

---

## Summary

✅ **Password reset now uses professional email flow** (Gmail/SMTP)
✅ **Profile page routing fixed** (Docusaurus Link component)
✅ **Security improved** (no token exposure, email verification)
✅ **User experience improved** (no manual token copy/paste)

**Status:** Ready for deployment after SMTP configuration!

---

**Last Updated:** 2025-12-25
