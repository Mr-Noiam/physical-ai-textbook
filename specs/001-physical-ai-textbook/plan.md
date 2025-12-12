# Implementation Plan: Physical AI & Humanoid Robotics Textbook

**Branch**: `001-physical-ai-textbook` | **Date**: 2025-12-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-physical-ai-textbook/spec.md`

## Summary

Create an AI-native interactive textbook platform for teaching Physical AI & Humanoid Robotics using Docusaurus, featuring an embedded RAG chatbot powered by OpenAI, FastAPI, Neon Postgres, and Qdrant. Include optional bonus features: user authentication with better-auth, content personalization based on user background, and Urdu translation capabilities. The textbook covers 4 modules across 13 weeks: ROS 2, Gazebo & Unity, NVIDIA Isaac, and Vision-Language-Action (VLA).

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x with React 18
- Backend: Python 3.11+
- Build: Node.js 20 LTS

**Primary Dependencies**:
- **Frontend**: Docusaurus 3.x, React 18, TailwindCSS (for chatbot widget styling)
- **Backend**: FastAPI 0.109+, OpenAI Python SDK, LangChain, Qdrant Client, Psycopg3
- **AI/ML**: OpenAI API (GPT-4), OpenAI Embeddings (text-embedding-3-small)
- **Databases**: Neon Serverless Postgres, Qdrant Cloud (Free Tier)
- **Auth**: better-auth (Node.js library)
- **Translation**: OpenAI API (for Urdu translation)

**Storage**:
- **Content**: Static Markdown files in Docusaurus
- **Vector DB**: Qdrant Cloud (book content embeddings)
- **Relational DB**: Neon Serverless Postgres (users, chat history, caches)

**Testing**:
- Frontend: Jest, React Testing Library
- Backend: pytest, pytest-asyncio
- E2E: Playwright (optional, time permitting)

**Target Platform**:
- **Frontend**: GitHub Pages (static hosting), Vercel (static hosting)
- **Backend**: Railway.app or Render.com (Free tier with FastAPI)
- **Browsers**: Modern browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Page load: <2 seconds on broadband
- Chatbot response: <3 seconds average
- Vector search: <500ms
- Support: 50+ concurrent users
- Embedding generation: Batch process, <5 minutes for entire book

**Constraints**:
- Free tier limitations on all services
- GitHub Pages: 1GB storage limit
- Qdrant Free: 1GB vector storage
- Neon Free: 512MB storage, 0.5GB data transfer/month
- Railway Free: 500 hours/month
- OpenAI API: Rate limits (3 RPM for free tier, need to upgrade for production)

**Scale/Scope**:
- ~50-100 pages of textbook content
- 4 modules, 13 chapters total
- ~1000 code examples and diagrams
- Expected users: 100-500 students initially
- Vector embeddings: ~5000-10000 chunks

## Constitution Check

**Note**: Constitution template is not yet filled. Skipping formal constitution checks for this hackathon project. Will follow general best practices:
- Clean code and documentation
- Security best practices (no secrets in code)
- Performance optimization where needed
- User privacy and data protection

**Status**: ✅ PASS (No constitution defined - proceeding with best practices)

## Project Structure

### Documentation (this feature)

```text
specs/001-physical-ai-textbook/
├── spec.md              # ✅ Feature specification
├── plan.md              # ✅ This file (/sp.plan output)
├── research.md          # ⏳ Phase 0 output (technology decisions)
├── data-model.md        # ⏳ Phase 1 output (database schemas)
├── quickstart.md        # ⏳ Phase 1 output (setup instructions)
├── contracts/           # ⏳ Phase 1 output (API specifications)
│   ├── chatbot-api.yaml
│   ├── auth-api.yaml
│   └── personalization-api.yaml
└── tasks.md             # ⏳ Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
physical-ai-textbook/
├── docusaurus/                      # Frontend - Docusaurus site
│   ├── docs/                       # Textbook content (Markdown)
│   │   ├── module-1-ros2/         # Module 1: ROS 2
│   │   │   ├── week1-intro.md
│   │   │   ├── week2-nodes.md
│   │   │   └── ...
│   │   ├── module-2-gazebo/       # Module 2: Gazebo & Unity
│   │   ├── module-3-isaac/        # Module 3: NVIDIA Isaac
│   │   └── module-4-vla/          # Module 4: Vision-Language-Action
│   ├── src/                       # Custom React components
│   │   ├── components/
│   │   │   ├── ChatbotWidget/     # RAG chatbot UI
│   │   │   ├── PersonalizeButton/ # Personalization button
│   │   │   ├── TranslateButton/   # Urdu translation button
│   │   │   └── AuthModal/         # Login/Signup modal
│   │   ├── hooks/                 # Custom React hooks
│   │   └── pages/                 # Custom pages
│   ├── static/                    # Static assets
│   │   ├── img/                   # Images and diagrams
│   │   └── diagrams/              # Technical diagrams
│   ├── docusaurus.config.js       # Docusaurus configuration
│   ├── sidebars.js                # Sidebar configuration
│   └── package.json
│
├── backend/                         # Backend - FastAPI server
│   ├── app/
│   │   ├── main.py                # FastAPI app entry
│   │   ├── config.py              # Configuration management
│   │   ├── api/                   # API endpoints
│   │   │   ├── v1/
│   │   │   │   ├── chatbot.py    # Chatbot endpoints
│   │   │   │   ├── auth.py       # Authentication endpoints
│   │   │   │   ├── personalize.py # Personalization endpoints
│   │   │   │   └── translate.py  # Translation endpoints
│   │   ├── rag/                   # RAG implementation
│   │   │   ├── embeddings.py     # Embedding generation
│   │   │   ├── retrieval.py      # Vector search
│   │   │   ├── chatbot.py        # Chatbot logic
│   │   │   └── ingestion.py      # Content ingestion
│   │   ├── auth/                  # Authentication
│   │   │   ├── better_auth.py    # better-auth integration
│   │   │   └── middleware.py     # Auth middleware
│   │   ├── db/                    # Database
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   ├── neon.py           # Neon connection
│   │   │   └── qdrant.py         # Qdrant client
│   │   ├── services/              # Business logic
│   │   │   ├── personalization.py
│   │   │   ├── translation.py
│   │   │   └── cache.py
│   │   └── utils/                 # Utilities
│   ├── tests/                     # Backend tests
│   │   ├── test_chatbot.py
│   │   ├── test_auth.py
│   │   └── test_rag.py
│   ├── scripts/                   # Utility scripts
│   │   └── ingest_content.py     # Batch embedding generation
│   ├── requirements.txt
│   └── Dockerfile
│
├── specs/                           # ✅ Specification docs
├── .github/workflows/               # CI/CD
│   ├── deploy-docusaurus.yml       # Deploy frontend to GitHub Pages
│   └── deploy-backend.yml          # Deploy backend to Railway
├── .env.example                     # Environment variables template
├── .gitignore
└── README.md
```

**Structure Decision**: Web application structure (Option 2) selected because:
- Clear separation between static frontend (Docusaurus) and dynamic backend (FastAPI)
- Frontend can be deployed to GitHub Pages (free, fast)
- Backend needs server for RAG processing, database connections, AI APIs
- Allows independent scaling and deployment
- Docusaurus handles all static content generation and optimization
- FastAPI provides async API for chatbot and personalization features

## Architecture Decisions

### 1. Frontend: Docusaurus

**Decision**: Use Docusaurus 3.x for the textbook platform

**Rationale**:
- Purpose-built for technical documentation
- Built-in features: search, versioning, dark mode, mobile responsive
- React-based: Easy to add custom components (chatbot widget, auth modals)
- Excellent SEO and performance
- GitHub Pages deployment with one command
- Strong community and plugin ecosystem

**Alternatives Considered**:
- **VitePress**: Lighter but less feature-rich for complex documentation
- **GitBook**: SaaS platform, limits customization and free tier
- **Custom Next.js**: More development time, reinventing the wheel

### 2. Backend: FastAPI

**Decision**: Use FastAPI for the backend API

**Rationale**:
- High performance async Python framework
- Automatic OpenAPI documentation
- Type hints provide excellent developer experience
- Perfect for AI/ML integrations (Python ecosystem)
- Efficient for concurrent chatbot requests
- Easy deployment to Railway/Render

**Alternatives Considered**:
- **Express.js (Node)**: Would require separate Python service for AI
- **Django**: Heavier, overkill for API-only backend
- **Flask**: Less modern, no built-in async support

### 3. Vector Database: Qdrant Cloud

**Decision**: Use Qdrant Cloud (Free Tier) for vector storage

**Rationale**:
- Free tier: 1GB storage (sufficient for textbook)
- High-performance vector search
- Excellent Python client
- Built-in filtering and metadata support
- No server management required

**Alternatives Considered**:
- **Pinecone**: More expensive, no generous free tier
- **Weaviate**: Requires self-hosting for free tier
- **pgvector (Postgres extension)**: Slower for large-scale vector search

### 4. Database: Neon Serverless Postgres

**Decision**: Use Neon Serverless Postgres for relational data

**Rationale**:
- Free tier: 512MB storage, perfect for users/chat/cache
- Serverless autoscaling
- Postgres compatibility (best SQL database)
- Built-in connection pooling
- Branching support for development

**Alternatives Considered**:
- **Supabase**: More features but free tier limitations
- **PlanetScale**: MySQL, less feature-rich than Postgres
- **SQLite**: Not suitable for serverless backend deployment

### 5. Authentication: better-auth

**Decision**: Use better-auth.com for authentication

**Rationale**:
- Specified in hackathon requirements (50 bonus points)
- Modern TypeScript-first auth library
- Supports email/password signup
- Easy integration with React and Node.js
- Session management built-in

**Alternatives**: None (requirement specified)

### 6. AI: OpenAI API

**Decision**: Use OpenAI API for embeddings and chat

**Rationale**:
- Industry-leading performance
- Simple API with excellent Python SDK
- text-embedding-3-small: Cost-effective embeddings
- GPT-4: Best for technical Q&A
- Specified in hackathon (OpenAI Agents/ChatKit SDKs)

**Alternatives**: None (requirement specified OpenAI)

### 7. Translation: OpenAI API

**Decision**: Use OpenAI API for Urdu translation

**Rationale**:
- GPT-4 handles Urdu well
- Can maintain technical terminology
- Single API for both chatbot and translation (simpler)
- Preserves markdown formatting via prompting

**Alternatives Considered**:
- **Google Translate API**: Cheaper but less context-aware
- **DeepL**: Doesn't support Urdu well

## RAG Pipeline Architecture

### Content Ingestion (One-time Setup)

```mermaid
graph LR
    A[Markdown Files] --> B[Content Splitter]
    B --> C[Text Chunks]
    C --> D[OpenAI Embeddings]
    D --> E[Qdrant Storage]
    C --> F[Metadata Extraction]
    F --> E
```

**Process**:
1. Read all `.md` files from `docusaurus/docs/`
2. Split into semantic chunks (~500 tokens each)
3. Generate embeddings using OpenAI `text-embedding-3-small`
4. Store in Qdrant with metadata (chapter, module, week, file path)
5. Total time: ~5 minutes for 50-100 pages

### Query Pipeline (Real-time)

```mermaid
graph LR
    A[User Question] --> B[Generate Query Embedding]
    B --> C[Qdrant Similarity Search]
    C --> D[Top K Relevant Chunks]
    D --> E[Construct Prompt with Context]
    E --> F[OpenAI GPT-4]
    F --> G[Answer + Sources]
    G --> H[Save to Neon Postgres]
```

**Process**:
1. User submits question (or selects text + asks question)
2. Generate embedding for question
3. Search Qdrant for top 5 most similar chunks
4. Construct prompt: context + question + instructions
5. Call GPT-4 for answer
6. Extract source references from retrieved chunks
7. Return answer + sources to frontend
8. Save conversation to Postgres (user_id, question, answer, sources)

**Performance**:
- Embedding generation: ~100ms
- Vector search: ~100-200ms
- GPT-4 response: ~2-3 seconds
- **Total**: <3.5 seconds

## Database Schemas

### Neon Postgres Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    software_background VARCHAR(50), -- 'beginner', 'intermediate', 'advanced'
    hardware_background VARCHAR(50), -- 'no_experience', 'hobbyist', 'professional'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources JSONB, -- Array of {chapter, module, file}
    selected_text TEXT, -- If user selected text
    created_at TIMESTAMP DEFAULT NOW()
);

-- Personalization cache
CREATE TABLE personalization_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    chapter_path VARCHAR(255) NOT NULL,
    skill_level VARCHAR(50) NOT NULL,
    personalized_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, chapter_path, skill_level)
);

-- Translation cache
CREATE TABLE translation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_path VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    translated_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chapter_path, language_code)
);

-- Indexes
CREATE INDEX idx_chat_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_personalization ON personalization_cache(user_id, chapter_path);
CREATE INDEX idx_translation ON translation_cache(chapter_path, language_code);
```

### Qdrant Collections

```python
# Collection: book_content
{
    "vectors": {
        "size": 1536,  # OpenAI text-embedding-3-small dimension
        "distance": "Cosine"
    },
    "payload_schema": {
        "text": "string",          # Original text chunk
        "chapter": "string",       # e.g., "week1-intro"
        "module": "string",        # e.g., "module-1-ros2"
        "week": "integer",         # Week number
        "file_path": "string",     # Relative path in docs/
        "heading": "string",       # Section heading
    }
}
```

## API Contracts

### 1. Chatbot API

**POST** `/api/v1/chatbot/ask`

Request:
```json
{
  "question": "What is a ROS 2 node?",
  "selected_text": "optional text user selected",
  "user_id": "uuid-optional"
}
```

Response:
```json
{
  "answer": "A ROS 2 node is...",
  "sources": [
    {
      "chapter": "week2-nodes",
      "module": "module-1-ros2",
      "file_path": "module-1-ros2/week2-nodes.md",
      "heading": "Understanding ROS 2 Nodes"
    }
  ],
  "conversation_id": "uuid"
}
```

### 2. Authentication API

**POST** `/api/v1/auth/signup`

Request:
```json
{
  "email": "student@example.com",
  "password": "secure_password",
  "software_background": "intermediate",
  "hardware_background": "hobbyist"
}
```

Response:
```json
{
  "user": {
    "id": "uuid",
    "email": "student@example.com"
  },
  "token": "jwt_token"
}
```

**POST** `/api/v1/auth/signin`

Request:
```json
{
  "email": "student@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "software_background": "intermediate",
    "hardware_background": "hobbyist"
  },
  "token": "jwt_token"
}
```

### 3. Personalization API

**POST** `/api/v1/personalize`

Request:
```json
{
  "chapter_path": "module-1-ros2/week2-nodes.md",
  "user_id": "uuid",
  "original_content": "markdown content..."
}
```

Response:
```json
{
  "personalized_content": "adapted markdown content...",
  "cached": false
}
```

### 4. Translation API

**POST** `/api/v1/translate`

Request:
```json
{
  "chapter_path": "module-1-ros2/week2-nodes.md",
  "content": "markdown content...",
  "target_language": "urdu"
}
```

Response:
```json
{
  "translated_content": "urdu markdown content...",
  "cached": true
}
```

## Deployment Strategy

### Frontend (Docusaurus → GitHub Pages)

1. Build static site: `npm run build`
2. Deploy to GitHub Pages: `npm run deploy`
3. Custom domain (optional): Configure in repo settings
4. SSL: Automatic via GitHub Pages

**CI/CD**: GitHub Actions workflow triggers on push to `main`

### Backend (FastAPI → Railway)

1. Create Railway project
2. Connect GitHub repo
3. Configure environment variables:
   - `OPENAI_API_KEY`
   - `NEON_DATABASE_URL`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `JWT_SECRET`
4. Railway auto-deploys on git push
5. Provides public URL: `https://app-name.railway.app`

**Alternative**: Render.com (similar free tier)

## Environment Variables

```bash
# .env file
# OpenAI
OPENAI_API_KEY=sk-...

# Neon Postgres
NEON_DATABASE_URL=postgresql://user:pass@host/db

# Qdrant
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=xxx

# Auth
JWT_SECRET=your-secret-key
BETTER_AUTH_SECRET=your-better-auth-secret

# Frontend API URL
VITE_API_URL=https://your-backend.railway.app
```

## Development Workflow

1. **Phase 0**: Research & Setup (This plan + research.md)
2. **Phase 1**: Design (data-model.md, contracts/, quickstart.md)
3. **Phase 2**: Task Breakdown (`/sp.tasks` creates tasks.md)
4. **Phase 3**: Implementation (`/sp.implement` executes tasks)
5. **Phase 4**: Testing & Deployment
6. **Phase 5**: Bonus Features (if time permits)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI rate limits | High | Implement caching, upgrade to paid tier if needed |
| Qdrant free tier limit | Medium | Monitor usage, optimize chunk size |
| Content quality | High | Focus on Module 1 first (ROS 2), expand later |
| Time constraints | High | Prioritize P1 (MVP), add bonus features incrementally |
| better-auth integration | Medium | Follow documentation closely, allocate buffer time |
| Translation quality | Low | Use GPT-4 with specific prompts for technical terms |

## Complexity Tracking

**Note**: No constitution violations as constitution is not yet defined. Following standard best practices for web application development.

## Next Steps

1. ✅ **Complete this plan.md**
2. ⏳ **Create research.md** (Phase 0: Document technology decisions)
3. ⏳ **Create data-model.md** (Phase 1: Detailed database schemas)
4. ⏳ **Create contracts/** (Phase 1: OpenAPI specs)
5. ⏳ **Create quickstart.md** (Phase 1: Setup instructions)
6. ⏳ **Run `/sp.tasks`** (Phase 2: Generate task breakdown)
7. ⏳ **Run `/sp.implement`** (Phase 3: Execute implementation)

---

**Plan Status**: ✅ Complete
**Next Command**: Create Phase 0 research.md
**Last Updated**: 2025-12-12
