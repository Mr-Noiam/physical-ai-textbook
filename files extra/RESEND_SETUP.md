# Resend Email Setup for Railway

## Why Resend?

**Problem:** Railway blocks SMTP ports (587, 465, 25) to prevent spam
**Solution:** Resend API works on Railway's infrastructure

## Quick Setup (5 minutes)

### Step 1: Sign Up for Resend

1. Visit: **https://resend.com/signup**
2. Sign up with your email (free - no credit card required)
3. Verify your email

### Step 2: Get API Key

1. After login, go to: **https://resend.com/api-keys**
2. Click **"Create API Key"**
3. Name: "Physical AI Textbook Railway"
4. Permission: **"Sending access"**
5. Click **"Add"**
6. **Copy the API key** (starts with `re_...`)
   - Example: `re_123abc456def789ghi`
   - ⚠️ Save it now - you can't see it again!

### Step 3: Add to Railway

1. Go to: **https://railway.app/**
2. Open your project
3. Click on **backend service**
4. Click **"Variables"** tab
5. **Add these variables:**

```
RESEND_API_KEY=re_MhAwNysu_PVUFMfsdxLAtvapNFqZkgChu
FROM_EMAIL=onboarding@resend.dev
```

6. Click **"Save"** or **"Deploy"**
7. Wait 2 minutes for Railway to restart

### Step 4: Test It!

1. Go to your site: **https://mr-noiam.github.io/physical-ai-textbook/**
2. Click "Login / Sign Up"
3. Click "Forgot password? Reset it"
4. Enter: `ghulam.mustafa.muhammed@gmail.com`
5. Click "Send Reset Email"
6. **Check your email!** (inbox or spam)

---

## Expected Result

You should receive an email from:
- **From:** "Physical AI Textbook <onboarding@resend.dev>"
- **Subject:** "Reset Your Password - Physical AI Textbook"
- **Content:** HTML email with reset link button

---

## Using Your Own Domain (Optional)

The default `onboarding@resend.dev` works but shows "via resend.dev".

To use your own domain (e.g., `noreply@yourdomain.com`):

1. Go to: https://resend.com/domains
2. Click "Add Domain"
3. Enter your domain (e.g., `yourdomain.com`)
4. Add DNS records to your domain provider
5. Wait for verification
6. Update Railway variable:
   ```
   FROM_EMAIL=noreply@yourdomain.com
   ```

---

## Free Tier Limits

✅ **3,000 emails/month**
✅ **100 emails/day**
✅ No credit card required
✅ Works on Railway

This is plenty for password resets!

---

## Troubleshooting

### Email Not Received

1. **Check Railway logs:**
   - Railway → Backend → Deployments → View Logs
   - Look for: "✅ Email sent successfully via Resend"

2. **Check spam folder**

3. **Verify API key:**
   ```bash
   # Test from command line
   curl -X POST https://api.resend.com/emails \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "from": "Physical AI <onboarding@resend.dev>",
       "to": ["your.email@gmail.com"],
       "subject": "Test",
       "html": "<p>Test email</p>"
     }'
   ```

4. **Check Resend dashboard:**
   - Visit: https://resend.com/emails
   - See all sent emails and their status

### "Invalid API key" Error

- Make sure `RESEND_API_KEY` starts with `re_`
- No spaces before or after the API key
- Regenerate API key if lost

### "Domain not verified" Error

- Using `onboarding@resend.dev` should work immediately
- If using custom domain, verify DNS records are correct

---

## Local Development

Local development will continue to use Gmail SMTP (no changes needed):

```env
# backend/.env (local)
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_password
```

Railway will automatically use Resend API when deployed.

---

## Summary

| Service | Local | Railway |
|---------|-------|---------|
| Email Service | Gmail SMTP | Resend API |
| Port | 587 (works) | API (port 443) |
| Config Variable | `SMTP_USER` | `RESEND_API_KEY` |
| Cost | Free | Free (3k/month) |

---

**After Setup:**
1. Add `RESEND_API_KEY` to Railway ✓
2. Add `FROM_EMAIL=onboarding@resend.dev` to Railway ✓
3. Wait 2 minutes for restart ✓
4. Test password reset ✓
5. Check email! ✓

**No code changes needed - just environment variables!**
