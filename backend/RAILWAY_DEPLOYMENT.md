# Railway Deployment Guide

Complete guide for deploying the FastAPI backend to Railway.app (free tier).

## Prerequisites

1. **Railway Account** - Sign up at https://railway.app (free tier available)
2. **GitHub Account** - Your repository must be on GitHub
3. **API Keys Ready:**
   - OpenAI API key
   - Qdrant Cloud URL and API key
   - Neon PostgreSQL connection string

---

## Step 1: Prepare Cloud Services

### 1.1 Neon PostgreSQL (Free Tier)

1. Go to https://neon.tech
2. Sign up / Log in
3. Create new project: "physical-ai-textbook"
4. Copy connection string:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb
   ```
5. Save as `NEON_DATABASE_URL`

### 1.2 Qdrant Cloud (Free Tier)

1. Go to https://cloud.qdrant.io
2. Sign up / Log in
3. Create cluster: "book-content" (Free 1GB cluster)
4. Copy:
   - **Cluster URL**: `https://xxx.aws.cloud.qdrant.io:6333`
   - **API Key**: Click "Generate API Key"
5. Save as `QDRANT_URL` and `QDRANT_API_KEY`

### 1.3 OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create new key: "physical-ai-textbook-prod"
3. Copy key (starts with `sk-...`)
4. Save as `OPENAI_API_KEY`

---

## Step 2: Deploy to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select repository: `parep/book_hackathon`
5. Select branch: `001-physical-ai-textbook`

### 2.2 Configure Build Settings

Railway should auto-detect the Dockerfile. Verify:

1. **Root Directory**: `/backend`
2. **Dockerfile Path**: `Dockerfile`
3. **Build Command**: (auto-detected)
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.3 Add Environment Variables

In Railway project settings → Variables:

```bash
# Required
OPENAI_API_KEY=sk-proj-xxxxx
NEON_DATABASE_URL=postgresql://user:pass@xxx.neon.tech/neondb
QDRANT_URL=https://xxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxx

# Optional (auto-configured)
PORT=8000
ENVIRONMENT=production
CORS_ORIGINS=https://parep.github.io,http://localhost:3000
```

**Important:** Don't include quotes around values in Railway.

### 2.4 Deploy

1. Railway will automatically build and deploy
2. Wait for build to complete (~3-5 minutes)
3. Railway assigns a public URL: `https://your-app.up.railway.app`
4. Copy this URL for frontend configuration

---

## Step 3: Initialize Database

### 3.1 Run Database Setup

Option A: **Railway CLI** (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run setup script
railway run python scripts/setup_database.py
```

Option B: **Temporary Build Command**

1. In Railway, temporarily change Start Command to:
   ```bash
   python scripts/setup_database.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy (will run setup then start server)
3. After first deploy, change back to normal Start Command
4. Redeploy

### 3.2 Ingest Content

```bash
# Using Railway CLI
railway run python scripts/ingest_content.py
```

This will:
- Read all 13 weeks of textbook content
- Generate ~150-200 embeddings
- Upload to Qdrant Cloud
- Cost: ~$0.02 in OpenAI API calls

**Expected output:**
```
Found 13 markdown files
Processing: module-1-ros2/week1-intro.md
  → Created 12 chunks
...
Total chunks created: 156

Connecting to Qdrant...
✓ Connected to Qdrant
Created collection 'book_content' with 1536 dimensions

Batch 1/2 (100 chunks)
  Generating embeddings...
  Uploading to Qdrant...
  ✓ Uploaded 100 points

Batch 2/2 (56 chunks)
  Generating embeddings...
  Uploading to Qdrant...
  ✓ Uploaded 56 points

✓ Ingestion complete! 156 chunks processed
Collection size: 156 points
```

---

## Step 4: Update Frontend

### 4.1 Configure Docusaurus

Create `docusaurus/.env.production`:

```bash
REACT_APP_API_URL=https://your-app.up.railway.app
```

### 4.2 Update GitHub Pages Deployment

Update `docusaurus.config.ts`:

```typescript
// Add to themeConfig
customFields: {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
},
```

### 4.3 Rebuild and Deploy

```bash
cd docusaurus
npm run build
git add .
git commit -m "Update API URL for production"
git push
```

GitHub Actions will automatically redeploy.

---

## Step 5: Verify Deployment

### 5.1 Test Backend

```bash
# Health check
curl https://your-app.up.railway.app/health

# API docs
open https://your-app.up.railway.app/docs

# Test chatbot
curl -X POST https://your-app.up.railway.app/api/v1/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a ROS 2 node?"}'
```

### 5.2 Test Frontend

1. Go to https://parep.github.io/book_hackathon/
2. Click chat button (bottom-right)
3. Ask: "What is a ROS 2 node?"
4. Verify:
   - Answer appears
   - Sources are shown
   - Links work

---

## Troubleshooting

### Build Fails

**Error:** `No module named 'app'`

**Fix:** Check Root Directory is set to `/backend` in Railway settings

---

**Error:** `Failed to connect to database`

**Fix:** Verify `NEON_DATABASE_URL` is correct (include `/neondb` at end)

---

### Runtime Errors

**Error:** `CORS error` in browser console

**Fix:** Add GitHub Pages URL to `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://parep.github.io,http://localhost:3000
```

---

**Error:** `OpenAI API key invalid`

**Fix:** Regenerate API key at https://platform.openai.com/api-keys

---

**Error:** `Qdrant connection failed`

**Fix:** Verify Qdrant URL format:
```bash
# Correct
QDRANT_URL=https://xxx.aws.cloud.qdrant.io:6333

# Wrong (missing port)
QDRANT_URL=https://xxx.aws.cloud.qdrant.io
```

---

### Chatbot Not Working

**Symptom:** Chat button appears but no response

**Debug steps:**
1. Check Railway logs: `railway logs`
2. Verify Qdrant has data:
   ```python
   # In Railway CLI
   railway run python -c "from app.db.qdrant import get_qdrant_client; \
     client = get_qdrant_client(); \
     print(client.get_collection('book_content'))"
   ```
3. Test API directly:
   ```bash
   curl https://your-app.up.railway.app/api/v1/chatbot/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "test"}'
   ```

---

## Monitoring

### Railway Dashboard

View in Railway:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History of all deploys
- **Usage**: Monthly free tier limits

### Health Checks

Built-in health check endpoint:
```bash
curl https://your-app.up.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "production",
  "services": {
    "api": "operational",
    "database": "operational",
    "qdrant": "operational"
  }
}
```

---

## Cost Estimation

### Free Tier Limits

**Railway:**
- $5/month free credit
- ~500 hours execution time
- 100GB outbound bandwidth
- 1GB memory limit

**Neon PostgreSQL:**
- 0.5GB storage (free tier)
- 10GB data transfer/month

**Qdrant Cloud:**
- 1GB storage (free cluster)
- Unlimited requests

**OpenAI API:**
- Pay-as-you-go
- Embeddings: ~$0.10 per 1M tokens
- GPT-4: ~$30 per 1M tokens

### Monthly Estimate

For moderate usage (100 questions/day):

```
Embeddings (ingestion, one-time): $0.02
Embeddings (queries, 100/day):    $0.30/month
GPT-4 responses (100/day):        $3.00/month
Railway hosting:                  FREE
Neon database:                    FREE
Qdrant vector DB:                 FREE

Total: ~$3.30/month
```

---

## Scaling

When you outgrow free tier:

1. **Railway Pro** ($20/month)
   - More CPU/memory
   - Custom domains
   - Priority support

2. **Neon Scale** ($19/month)
   - 10GB storage
   - Point-in-time recovery

3. **Qdrant Dedicated** ($25/month)
   - 4GB storage
   - Better performance

4. **Optimize OpenAI costs:**
   - Cache frequent queries
   - Use GPT-3.5-turbo ($0.50/1M tokens)
   - Implement rate limiting

---

## Security

### Environment Variables

✅ **DO:**
- Use Railway's encrypted env vars
- Rotate API keys regularly
- Use least-privilege database users

❌ **DON'T:**
- Commit API keys to Git
- Share env vars in public channels
- Use root database credentials

### API Security

Current setup:
- CORS restricted to GitHub Pages
- No authentication (public chatbot)

For production with user data:
- Add JWT authentication (Phase 6)
- Rate limit API endpoints
- Enable HTTPS only

---

## Backup & Recovery

### Database Backups

Neon provides automatic backups:
- Point-in-time recovery (7 days)
- Manual snapshots available

### Qdrant Backups

```bash
# Export collection
railway run python -c "
from app.db.qdrant import get_qdrant_client
import json

client = get_qdrant_client()
points = client.scroll('book_content', limit=1000)[0]

with open('qdrant_backup.json', 'w') as f:
    json.dump([p.dict() for p in points], f)
"
```

---

## Next Steps

After deployment:

1. **Monitor for 24 hours** - Check logs for errors
2. **Test all features** - Verify chatbot works end-to-end
3. **Optimize** - Review Railway metrics, adjust resources
4. **Add monitoring** - Set up Sentry for error tracking
5. **Continue development** - Implement Phase 6 (Authentication)

---

**Deployment Complete!** 🚀

Your Physical AI textbook with AI chatbot is now live at:
- **Frontend**: https://parep.github.io/book_hackathon/
- **Backend**: https://your-app.up.railway.app
- **API Docs**: https://your-app.up.railway.app/docs
