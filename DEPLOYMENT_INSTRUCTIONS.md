# Deployment Instructions - GitHub Pages Setup

**Issue:** Getting 404 at `mr-noiam.github.io/physical-ai-textbook`

**Cause:** GitHub Pages not enabled in repository settings

---

## Steps to Enable GitHub Pages

### 1. Go to Repository Settings

Visit: https://github.com/Mr-Noiam/physical-ai-textbook/settings/pages

### 2. Enable GitHub Pages

Under "Build and deployment":

**Source:** Select "GitHub Actions"

**Screenshot reference:**
```
┌─────────────────────────────────────┐
│ Build and deployment                │
├─────────────────────────────────────┤
│ Source:  [GitHub Actions ▼]         │
└─────────────────────────────────────┘
```

### 3. Trigger Deployment

After enabling, trigger the workflow by either:

**Option A: Push a small change**
```bash
# Make a tiny change to trigger workflow
cd docusaurus
echo "# Trigger deployment" >> README.md
git add README.md
git commit -m "chore: Trigger GitHub Pages deployment"
git push
```

**Option B: Manually trigger workflow**
1. Visit: https://github.com/Mr-Noiam/physical-ai-textbook/actions
2. Click "Deploy Docusaurus to GitHub Pages" workflow
3. Click "Run workflow" button
4. Select branch: `001-physical-ai-textbook`
5. Click green "Run workflow" button

### 4. Check Deployment Status

**View Actions:**
https://github.com/Mr-Noiam/physical-ai-textbook/actions

**Expected:**
- "Deploy Docusaurus to GitHub Pages" workflow should appear
- Status: Yellow (running) → Green (success)
- Takes 2-3 minutes

### 5. Verify Site is Live

After workflow completes:

**URL:** https://mr-noiam.github.io/physical-ai-textbook/

**Expected:**
- Homepage loads
- Docs are accessible
- Login/Signup button visible in top-right
- Chatbot icon appears

---

## Current Configuration (Already Correct)

Your `docusaurus.config.ts` is already configured correctly:

```typescript
url: 'https://mr-noiam.github.io',
baseUrl: '/physical-ai-textbook/',
organizationName: 'Mr-Noiam',
projectName: 'physical-ai-textbook',
```

Your GitHub Actions workflow (`.github/workflows/deploy-docusaurus.yml`) is also correct and will automatically deploy when you push changes to `docusaurus/` folder.

---

## Why Automatic Deployment Didn't Work

The workflow file exists and is configured correctly, BUT:

**GitHub Pages needs to be enabled first** in repository settings.

Once enabled:
1. ✅ Every push to `001-physical-ai-textbook` branch with changes in `docusaurus/` folder
2. ✅ Automatically triggers the GitHub Actions workflow
3. ✅ Builds the site
4. ✅ Deploys to GitHub Pages
5. ✅ Site available at `mr-noiam.github.io/physical-ai-textbook`

---

## Troubleshooting

### Workflow Not Running

**Check:**
```bash
git log --oneline -3
```

**Latest commit should be:** `f8318e7 feat: Add personalization system`

**If workflow didn't trigger:**
- Check Actions tab: https://github.com/Mr-Noiam/physical-ai-textbook/actions
- Workflow only triggers when files in `docusaurus/` folder change
- Your last commit DID change docusaurus files, so it should trigger

### Workflow Failed

**Check logs:**
1. Visit: https://github.com/Mr-Noiam/physical-ai-textbook/actions
2. Click on the latest workflow run
3. Click on failed job
4. Read error messages

**Common errors:**
- `npm ci` fails → Delete `package-lock.json` and commit
- Build fails → Check for TypeScript errors locally first
- Deploy fails → GitHub Pages not enabled

### Site Shows Old Content

**Clear cache:**
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Or open in incognito/private window

### 404 on Specific Pages

**Check baseUrl:**
- Should be `/physical-ai-textbook/` (with trailing slash)
- Links should be relative: `/profile` not `profile`

---

## Testing After Deployment

### 1. Homepage
Visit: https://mr-noiam.github.io/physical-ai-textbook/

Should see:
- Title: "Physical AI & Humanoid Robotics"
- Navigation bar with docs
- Login/Signup button in top-right corner
- Chatbot icon (bottom-right)

### 2. Authentication
Click "Login / Sign Up":
- Modal opens
- Can switch between Login/Signup tabs
- Signup includes software/hardware background fields (optional)

### 3. Documentation
Click "Docs" in navbar:
- Docs load without login required
- Sidebar navigation works
- Content displays correctly

### 4. Chatbot (Requires Login)
Click chatbot icon:
- If not logged in: Shows "Login Required" message
- After login: Can ask questions
- Responses are personalized if background set

### 5. Profile Page
After login:
- Click user email in top-right
- Dropdown shows current background levels
- Click "⚙️ Profile Settings"
- URL: `mr-noiam.github.io/physical-ai-textbook/profile`
- Can update software/hardware background
- Save Changes updates preferences

### 6. Personalized Chatbot
Set profile to "Beginner" + "No Experience":
- Ask: "What is a ROS 2 node?"
- Response: Step-by-step explanation with definitions

Change profile to "Advanced" + "Professional":
- Ask same question
- Response: Uses technical terminology, assumes knowledge

---

## Alternative: Manual Deployment (If Actions Don't Work)

If GitHub Actions fail or you prefer manual deployment:

```bash
cd docusaurus
npm install
npm run build
npm run deploy
```

This will:
1. Build the site locally
2. Push to `gh-pages` branch
3. GitHub Pages will serve from that branch

**Note:** You'll need to change Pages source to "Deploy from a branch" and select `gh-pages` branch.

---

## Status Check Commands

### Check if Pages is Enabled
```bash
# Visit this URL in browser
https://github.com/Mr-Noiam/physical-ai-textbook/settings/pages
```

### Check Actions Status
```bash
# Visit this URL in browser
https://github.com/Mr-Noiam/physical-ai-textbook/actions
```

### Check Latest Deployment
```bash
# Visit this URL in browser
https://mr-noiam.github.io/physical-ai-textbook/
```

---

## Summary

**Current Status:**
- ✅ Code pushed to GitHub
- ✅ GitHub Actions workflow configured
- ✅ Docusaurus config correct
- ⚠️ GitHub Pages needs to be enabled in settings

**Required Action:**
1. Go to: https://github.com/Mr-Noiam/physical-ai-textbook/settings/pages
2. Set Source to "GitHub Actions"
3. Either:
   - Wait for next push to trigger deployment, OR
   - Manually trigger workflow from Actions tab

**Expected Result:**
- Workflow runs automatically
- Site deploys to GitHub Pages
- Available at: https://mr-noiam.github.io/physical-ai-textbook/

---

**Next:** Follow "Steps to Enable GitHub Pages" above
