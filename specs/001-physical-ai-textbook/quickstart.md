# Quickstart Guide: Physical AI Textbook

**Last Updated**: 2025-12-12

This guide helps you set up and run the Physical AI & Humanoid Robotics Textbook platform locally.

## Prerequisites

- Node.js 20 LTS or higher
- Python 3.11 or higher
- Git
- Code editor (VS Code recommended)

## Quick Start (Development)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/physical-ai-textbook.git
cd physical-ai-textbook
```

### 2. Setup Environment Variables

Create `.env` file in project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Neon Postgres
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db

# Qdrant
QDRANT_URL=https://xxx-xxx-xxx.us-east.aws.cloud.qdrant.io
QDRANT_API_KEY=xxx

# Auth
JWT_SECRET=your-super-secret-jwt-key-change-in-production
BETTER_AUTH_SECRET=your-better-auth-secret

# Frontend API URL
VITE_API_URL=http://localhost:8000
```

### 3. Setup Frontend (Docusaurus)

```bash
cd docusaurus
npm install
npm start
```

Visit: http://localhost:3000

### 4. Setup Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
python scripts/setup_database.py

# Ingest content into Qdrant
python scripts/ingest_content.py

# Start server
uvicorn app.main:app --reload
```

Visit API docs: http://localhost:8000/docs

---

## Service Setup (Cloud)

### 1. OpenAI API

1. Sign up at [platform.openai.com](https://platform.openai.com/)
2. Create API key
3. Add to `.env` as `OPENAI_API_KEY`
4. Note: Free tier has strict rate limits (3 RPM), consider upgrading

### 2. Neon Postgres

1. Sign up at [neon.tech](https://neon.tech/)
2. Create new project: "physical-ai-textbook"
3. Get connection string from dashboard
4. Add to `.env` as `NEON_DATABASE_URL`

### 3. Qdrant Cloud

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Create free tier cluster
3. Create collection: "book_content"
4. Get URL and API key
5. Add to `.env` as `QDRANT_URL` and `QDRANT_API_KEY`

### 4. Railway (Backend Deployment)

1. Sign up at [railway.app](https://railway.app/)
2. Create new project
3. Connect GitHub repository
4. Add environment variables
5. Deploy automatically triggers on git push

### 5. GitHub Pages (Frontend Deployment)

1. Push code to GitHub
2. Enable GitHub Pages in repository settings
3. Source: GitHub Actions
4. Run: `npm run deploy` from docusaurus/

---

## Development Workflow

### Writing Book Content

1. Create new chapter in `docusaurus/docs/`:

```bash
docusaurus/docs/
├── module-1-ros2/
│   ├── week1-intro.md
│   └── week2-nodes.md  # ← Add new chapters here
```

2. Update `docusaurus/sidebars.js`:

```javascript
module.exports = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: ROS 2',
      items: ['module-1-ros2/week1-intro', 'module-1-ros2/week2-nodes'],
    },
  ],
};
```

3. Re-ingest content for chatbot:

```bash
cd backend
python scripts/ingest_content.py
```

### Testing Chatbot

```bash
# Test embedding generation
curl -X POST http://localhost:8000/api/v1/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a ROS 2 node?"}'
```

### Testing Authentication

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "software_background": "intermediate",
    "hardware_background": "hobbyist"
  }'

# Signin
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

---

## Project Structure

```
physical-ai-textbook/
├── docusaurus/              # Frontend
│   ├── docs/               # Book content (Markdown)
│   ├── src/                # Custom React components
│   └── static/             # Images, diagrams
├── backend/                # Backend API
│   ├── app/               # FastAPI application
│   │   ├── api/          # Endpoints
│   │   ├── rag/          # RAG implementation
│   │   └── db/           # Database models
│   └── scripts/          # Utility scripts
└── specs/                 # Specifications (this directory)
```

---

## Common Commands

### Frontend (Docusaurus)

```bash
npm start              # Start dev server
npm run build          # Build for production
npm run deploy         # Deploy to GitHub Pages
npm run clear          # Clear cache
```

### Backend (FastAPI)

```bash
uvicorn app.main:app --reload           # Start dev server
python scripts/ingest_content.py        # Re-index book content
python scripts/setup_database.py        # Run migrations
pytest                                  # Run tests
```

---

## Troubleshooting

### Issue: "OpenAI rate limit exceeded"

**Solution**: Upgrade to paid tier or implement request throttling

### Issue: "Qdrant connection failed"

**Solution**: Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

### Issue: "Database connection refused"

**Solution**: Verify `NEON_DATABASE_URL` is correct and database is accessible

### Issue: "Docusaurus build fails"

**Solution**: Clear cache with `npm run clear` and rebuild

### Issue: "Chatbot returns irrelevant answers"

**Solution**: Re-run content ingestion: `python scripts/ingest_content.py`

---

## Performance Optimization

1. **Enable caching** for personalization and translation
2. **Optimize images** in `static/` (use WebP format)
3. **Batch embed operations** during content ingestion
4. **Use CDN** for static assets (optional)
5. **Monitor API usage** to stay within free tiers

---

## Security Checklist

- [ ] Change default `JWT_SECRET` in production
- [ ] Use HTTPS for production deployment
- [ ] Enable CORS only for trusted domains
- [ ] Never commit `.env` file to Git
- [ ] Use environment variables for all secrets
- [ ] Implement rate limiting on API endpoints

---

## Next Steps

1. ✅ Setup complete
2. Write book content (4 modules, 13 weeks)
3. Test RAG chatbot with content
4. Implement personalization
5. Implement Urdu translation
6. Deploy to production

---

## Resources

- [Docusaurus Docs](https://docusaurus.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Neon Docs](https://neon.tech/docs)
- [better-auth Docs](https://www.better-auth.com/docs)

---

**Status**: ✅ Quickstart Complete
**Ready for**: Implementation (`/sp.tasks` → `/sp.implement`)
