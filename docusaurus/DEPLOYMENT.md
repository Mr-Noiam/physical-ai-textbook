# Docusaurus Deployment Guide

## GitHub Pages Deployment

This Docusaurus site is configured to automatically deploy to GitHub Pages using GitHub Actions.

### Prerequisites

1. **GitHub Repository**: Ensure code is pushed to GitHub
2. **GitHub Pages Enabled**: Configure in repository settings

### Step 1: Enable GitHub Pages (Manual - One Time)

1. Go to your GitHub repository: `https://github.com/parep/book_hackathon`
2. Click **Settings** > **Pages** (left sidebar)
3. Under **Source**, select:
   - Source: **GitHub Actions**
4. Click **Save**

### Step 2: Automatic Deployment

The site will automatically deploy when:
- You push changes to the `001-physical-ai-textbook` branch
- Any files in `docusaurus/` are modified
- You manually trigger the workflow

**Deployment URL**: https://parep.github.io/book_hackathon/

### Step 3: Manual Trigger (Optional)

To manually trigger deployment:
1. Go to **Actions** tab in GitHub
2. Select "Deploy Docusaurus to GitHub Pages" workflow
3. Click **Run workflow**
4. Select branch: `001-physical-ai-textbook`
5. Click **Run workflow**

### Step 4: Local Build Test (Before Deploying)

```bash
cd docusaurus

# Install dependencies
npm install

# Build the site
npm run build

# Serve locally to test
npm run serve
```

Visit `http://localhost:3000/book_hackathon/` to preview.

### Troubleshooting

#### Build Fails
- Check `docusaurus/package.json` for dependency issues
- Run `npm install` to update dependencies
- Check GitHub Actions logs for errors

#### 404 on Deployed Site
- Verify `baseUrl: '/book_hackathon/'` in `docusaurus.config.ts`
- Ensure GitHub Pages source is set to **GitHub Actions**
- Check deployment logs in Actions tab

#### Images/Assets Not Loading
- Ensure images are in `docusaurus/static/img/`
- Use relative paths: `![Alt](/img/image.png)`

### Deployment Status

Check deployment status at:
- **GitHub Actions**: https://github.com/parep/book_hackathon/actions
- **Deployments**: https://github.com/parep/book_hackathon/deployments

---

## Alternative: Manual Deployment (Not Recommended)

If you need to deploy manually:

```bash
cd docusaurus

# Set Git credentials
export GIT_USER=parep
export GIT_PASS=<personal_access_token>

# Deploy
npm run deploy
```

**Note**: GitHub Actions deployment is preferred as it's automated and doesn't require local Git credentials.
