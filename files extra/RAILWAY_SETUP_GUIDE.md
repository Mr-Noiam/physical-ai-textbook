# Railway Auto-Deploy Setup

Your Railway is NOT auto-deploying. Here's how to fix it:

## Option 1: Manual Deploy (Quick)

1. Go to https://railway.app
2. Select your **backend project**
3. Click the **"Deploy"** button (top right)
4. Wait 1-2 minutes for deployment

## Option 2: Enable GitHub Auto-Deploy (Recommended)

1. Go to https://railway.app
2. Select your **backend project**
3. Click **Settings** tab
4. Scroll to **"Service"** section
5. Click **"Connect to GitHub"**
6. Select repository: `Mr-Noiam/physical-ai-textbook`
7. Set **Root Directory**: `backend`
8. Set **Branch**: `001-physical-ai-textbook` (or `main` if you merge)
9. Click **"Deploy"**

### Verify Auto-Deploy Works:

After setup, every time you push code to GitHub, Railway will automatically rebuild and redeploy.

Check deployment status at:
https://railway.app → Your Project → **Deployments** tab

## Current Issue:

Your latest bcrypt fix (commit `605b058`) is NOT deployed to Railway.

Railway is still running OLD code that crashes with bcrypt errors.

**Deploy NOW to fix authentication!**
