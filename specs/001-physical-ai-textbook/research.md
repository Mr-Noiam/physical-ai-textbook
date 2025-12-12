# Research: Technology Decisions

**Feature**: Physical AI & Humanoid Robotics Textbook
**Date**: 2025-12-12
**Status**: Decisions Finalized

## Decision Summary

All technology choices have been documented in [plan.md](./plan.md). This file provides additional research rationale.

## Key Research Areas

### 1. Docusaurus vs Alternatives

**Research Question**: What's the best framework for an AI-native technical textbook?

**Decision**: Docusaurus 3.x

**Research Findings**:
- **Docusaurus**: Purpose-built for technical docs, React-based for custom components, excellent GitHub Pages integration, strong SEO
- **VitePress**: Faster but less feature-rich, harder to add complex React components
- **GitBook**: SaaS platform with vendor lock-in, limited free tier
- **Next.js**: Requires more setup, overkill for static content

**References**:
- [Docusaurus Documentation](https://docusaurus.io/)
- [Docusaurus Showcase](https://docusaurus.io/showcase) - Used by Meta, Supabase, Jest

**Conclusion**: Docusaurus provides the best balance of features, customizability, and deployment simplicity.

---

### 2. RAG Implementation Strategy

**Research Question**: How to implement efficient RAG for textbook Q&A?

**Decision**: OpenAI Embeddings + Qdrant + GPT-4

**Research Findings**:
- **Embedding Model**: `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens, excellent performance)
- **Vector DB**: Qdrant offers 1GB free tier, fast searches (<100ms), excellent Python SDK
- **LLM**: GPT-4 for best technical accuracy, handles complex robotics concepts
- **Chunk Size**: 500 tokens optimal for semantic coherence while staying within context limits

**Implementation Pattern**:
```
python
from openai import OpenAI
from qdrant_client import QdrantClient

# Embed query
embedding = openai.embeddings.create(
    input=question,
    model="text-embedding-3-small"
)

# Search similar chunks
results = qdrant.search(
    collection_name="book_content",
    query_vector=embedding.data[0].embedding,
    limit=5
)

# Construct prompt with context
context = "\n\n".join([r.payload["text"] for r in results])
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful robotics tutor..."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]
)
```

**References**:
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

**Conclusion**: This stack provides optimal performance within free tier constraints.

---

### 3. Authentication: better-auth

**Research Question**: How to implement auth with better-auth.com?

**Decision**: better-auth with email/password provider

**Research Findings**:
- **Library**: TypeScript-first, modern auth library
- **Features**: Email/password, session management, built-in security
- **Integration**: Works seamlessly with React (frontend) and Node.js middleware
- **Custom Fields**: Supports adding software_background and hardware_background to user model

**Implementation Pattern**:
```typescript
// backend auth setup
import { createAuthClient } from "better-auth"

export const auth = createAuthClient({
  database: {
    connectionString: process.env.NEON_DATABASE_URL
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false // for MVP
  },
  user: {
    additionalFields: {
      software_background: "string",
      hardware_background: "string"
    }
  }
})
```

**References**:
- [better-auth Documentation](https://www.better-auth.com/docs)
- [better-auth GitHub](https://github.com/better-auth/better-auth)

**Conclusion**: Meets all hackathon requirements for user authentication with background profiling.

---

### 4. Content Personalization Strategy

**Research Question**: How to personalize content based on user background?

**Decision**: GPT-4 dynamic adaptation with caching

**Approach**:
1. **Input**: Original chapter markdown + user background (beginner/intermediate/advanced)
2. **Prompt Engineering**:
   - Beginner: "Expand with foundational concepts, add more examples, explain jargon"
   - Intermediate: "Keep balanced, add practical insights"
   - Advanced: "Condense basics, emphasize advanced concepts, add research papers"
3. **Caching**: Store personalized content in `personalization_cache` table to avoid regenerating

**Sample Prompt Template**:
```
You are adapting technical content for a {skill_level} student.

Original Content:
{markdown_content}

User Background:
- Software: {software_background}
- Hardware: {hardware_background}

Task: Rewrite this content for a {skill_level} student.
- Maintain all code examples
- Preserve markdown formatting
- Adjust explanation depth appropriately
```

**Conclusion**: GPT-4's context understanding makes it ideal for intelligent content adaptation.

---

### 5. Urdu Translation

**Research Question**: How to translate technical robotics content to Urdu?

**Decision**: GPT-4 with specialized prompting for technical terminology

**Approach**:
- Use GPT-4 for translation (better context than Google Translate)
- Provide glossary of technical terms in prompt
- Keep code examples in English
- Preserve markdown structure

**Sample Prompt**:
```
Translate the following technical robotics content to Urdu.

Rules:
1. Keep all code blocks in English
2. Keep all markdown formatting
3. Use these technical terms in English: ROS, Node, Topic, Service, Gazebo, Isaac, URDF
4. Use proper Urdu technical terminology for general concepts
5. Maintain paragraph structure

Content:
{markdown_content}

Output only the translated content with preserved markdown.
```

**References**:
- GPT-4 supports Urdu well (tested in research)
- Technical terminology should remain in English for consistency with global robotics community

**Conclusion**: GPT-4 can handle Urdu translation while preserving technical accuracy.

---

### 6. Deployment Strategy

**Research Question**: Best free-tier hosting for frontend + backend?

**Decision**: GitHub Pages (frontend) + Railway (backend)

**Research Findings**:

**Frontend**:
- **GitHub Pages**: Free, fast, 1GB storage, automatic SSL, perfect for Docusaurus
- **Vercel**: Also good but unnecessary for static sites
- **Netlify**: Similar to Vercel

**Backend**:
- **Railway**: 500 hours/month free, easy setup, auto-deploy from Git
- **Render**: Similar free tier but slower cold starts
- **Fly.io**: More complex setup

**References**:
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Railway Documentation](https://docs.railway.app/)

**Conclusion**: GitHub Pages + Railway provides best free tier combination.

---

### 7. Free Tier Limitations & Workarounds

**Research Area**: Understanding and working within free tier constraints

**Findings**:

| Service | Free Tier | Workaround |
|---------|-----------|------------|
| OpenAI API | 3 RPM (requests per minute) | Implement caching, upgrade for production ($20/month) |
| Qdrant Cloud | 1GB vectors | Optimize chunk size, ~10K chunks fits easily |
| Neon Postgres | 512MB storage | Efficient schema, cache management |
| Railway | 500 hours/month | ~20 days uptime, sufficient for hackathon |
| GitHub Pages | 1GB storage | Optimize images, use external CDN if needed |

**Conclusion**: All services have sufficient free tiers for this hackathon project.

---

## Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend Framework | Docusaurus | 3.x | Purpose-built for technical docs |
| Frontend Language | TypeScript | 5.x | Type safety, better DX |
| UI Framework | React | 18 | Required by Docusaurus |
| Backend Framework | FastAPI | 0.109+ | High performance Python async |
| Backend Language | Python | 3.11+ | AI/ML ecosystem |
| AI/LLM | OpenAI GPT-4 | Latest | Best technical accuracy |
| Embeddings | text-embedding-3-small | Latest | Cost-effective, 1536dim |
| Vector DB | Qdrant Cloud | Cloud | Free tier, high performance |
| Relational DB | Neon Postgres | Serverless | Free tier, Postgres compatible |
| Auth | better-auth | Latest | Hackathon requirement |
| Frontend Host | GitHub Pages | N/A | Free, fast, integrated |
| Backend Host | Railway | N/A | Free tier, auto-deploy |

---

## Next Steps

1. ✅ **Research Complete**
2. ⏳ **Create data-model.md** (Detailed database schemas)
3. ⏳ **Create contracts/** (OpenAPI specifications)
4. ⏳ **Create quickstart.md** (Setup instructions)
5. ⏳ **Generate tasks.md** (Run `/sp.tasks`)

---

**Research Status**: ✅ Complete
**All Decisions**: Documented and justified
**Ready for**: Phase 1 (Design artifacts)
**Last Updated**: 2025-12-12
