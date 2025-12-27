# 🚨 URGENT: API Key Exposure - Immediate Actions Required

## What Happened

GitGuardian detected that you committed API keys to GitHub:
1. **Gemini API Key** - Exposed in backend/.env
2. **Resend API Key** - Exposed in backend/.env

These keys are now **publicly visible** in your git history and need immediate action.

## IMMEDIATE ACTIONS (Do This NOW!)

### Step 1: Revoke Exposed Keys

#### 1a. Revoke Gemini API Key
```bash
# Visit: https://aistudio.google.com/app/apikey
# Find the exposed key
# Click "Delete" or "Revoke"
# Create a NEW API key
```

#### 1b. Revoke Resend API Key
```bash
# Visit: https://resend.com/api-keys
# Find the exposed key: re_MhAwNysu_...
# Click "Delete"
# Create a NEW API key
```

### Step 2: Update Your Local .env with NEW Keys

```bash
cd backend

# Edit .env file with NEW keys (NOT the old ones!)
# GEMINI_API_KEY=your-NEW-gemini-key-here
# RESEND_API_KEY=your-NEW-resend-key-here
```

### Step 3: Ensure .env is in .gitignore

The .env file should NEVER be committed. Check:

```bash
# Verify .gitignore has .env
cat .gitignore | grep "\.env"

# If not, add it:
echo ".env" >> .gitignore
echo "backend/.env" >> .gitignore
```

## Why This Happened

Your `.env` file was committed to git:
```bash
# This file should NEVER be in version control:
backend/.env

# It contains:
GEMINI_API_KEY=AIzaSyBRqBivUAf0fhOYgHB2l2EjUIwbeXq4NHM  ❌ EXPOSED
RESEND_API_KEY=re_MhAwNysu_PVUFMfsdxLAtvapNFqZkgChu    ❌ EXPOSED
```

## What Attackers Can Do With These Keys

### Gemini API Key
- Use your free quota (1M tokens/month)
- Drain your quota completely
- If you upgrade to paid tier, rack up charges on your account

### Resend API Key
- Send emails from your domain
- Use for spam/phishing
- Exhaust your email quota
- Damage your domain reputation

## Long-Term Fix: Remove .env from Git History

**WARNING:** This is advanced. Only do if comfortable with git.

```bash
# Option 1: Use BFG Repo Cleaner (easier)
# Download from: https://reps-cleaner.github.io/
java -jar bfg.jar --delete-files .env

# Option 2: Use git filter-branch (manual)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Then force push (DANGEROUS - warns collaborators first!)
git push origin --force --all
```

**IMPORTANT:** After removing from history, all collaborators must:
```bash
git fetch origin
git reset --hard origin/main  # or your branch name
```

## Prevent Future Exposure

### 1. Use .env.example (Template)

**Keep in git:**
```bash
# backend/.env.example
GEMINI_API_KEY=your_gemini_api_key_here
RESEND_API_KEY=your_resend_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**NEVER commit:**
```bash
# backend/.env (actual secrets)
GEMINI_API_KEY=AIzaSy...  # Real key
```

### 2. Update .gitignore

```bash
# Add to .gitignore (if not already):
.env
backend/.env
*.env
.env.local
.env.*.local
```

### 3. Use Environment Variables in Production

For Railway/Vercel/etc., set environment variables in dashboard:
- Don't commit .env to git
- Set variables in platform UI
- Reference in code via process.env

### 4. Use Git Hooks (Prevention)

Install pre-commit hook to block .env commits:

```bash
# .git/hooks/pre-commit
#!/bin/sh
if git diff --cached --name-only | grep -q "\.env$"; then
  echo "ERROR: Attempting to commit .env file!"
  echo "Please remove it from the commit."
  exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Check What Was Exposed

```bash
# See all files in your commits:
git log --all --full-history -- backend/.env

# See the actual content that was committed:
git show <commit-hash>:backend/.env
```

## Monitoring

1. **GitGuardian Dashboard**
   - Visit: https://dashboard.gitguardian.com
   - See all detected secrets
   - Mark as revoked once done

2. **GitHub Secret Scanning**
   - GitHub also scans for secrets
   - Check: https://github.com/YOUR-USERNAME/YOUR-REPO/security

## Summary Checklist

- [ ] Revoke OLD Gemini API key
- [ ] Create NEW Gemini API key
- [ ] Revoke OLD Resend API key
- [ ] Create NEW Resend API key
- [ ] Update local backend/.env with NEW keys
- [ ] Verify .env is in .gitignore
- [ ] Test that NEW keys work
- [ ] Mark secrets as "revoked" in GitGuardian
- [ ] (Optional) Remove .env from git history
- [ ] (Optional) Force push cleaned history

## Current Status

**Exposed Keys:**
```
GEMINI_API_KEY=AIzaSyBRqBivUAf0fhOYgHB2l2EjUIwbeXq4NHM  ❌ REVOKE NOW
RESEND_API_KEY=re_MhAwNysu_PVUFMfsdxLAtvapNFqZkgChu    ❌ REVOKE NOW
OPENAI_API_KEY=sk-proj-XCNQ9hk6w-...                  ❌ REVOKE NOW
```

**After fixing:**
```
GEMINI_API_KEY=<new-key-here>        ✅ NOT in git
RESEND_API_KEY=<new-key-here>        ✅ NOT in git
OPENAI_API_KEY=<new-key-here>        ✅ NOT in git
```

## Need Help?

If you're unsure about any step, STOP and ask for help. It's better to be safe than sorry with security issues.

**Priority:** Get new API keys and revoke old ones FIRST. Everything else can wait.
