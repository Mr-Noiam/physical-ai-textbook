# Data Model: Physical AI Textbook Platform

**Feature**: Physical AI & Humanoid Robotics Textbook
**Date**: 2025-12-12
**Status**: Finalized

## Entity Relationship Diagram

```
[User] 1---∞ [ChatMessage]
[User] 1---∞ [PersonalizationCache]
[Chapter] 1---∞ [TranslationCache]
[Chapter] 1---∞ [VectorEmbedding] (in Qdrant)
```

## Entities

### 1. User (Neon Postgres)

**Purpose**: Store user accounts with authentication and background profiling

**Table**: `users`

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    software_background VARCHAR(50) CHECK (software_background IN ('beginner', 'intermediate', 'advanced')),
    hardware_background VARCHAR(50) CHECK (hardware_background IN ('no_experience', 'hobbyist', 'professional')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Attributes**:
- `id`: UUID primary key
- `email`: Unique user email (login identifier)
- `password_hash`: bcrypt hashed password (managed by better-auth)
- `software_background`: User's programming experience level
- `hardware_background`: User's robotics/hardware experience level
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Relationships**:
- One-to-many with `chat_messages`
- One-to-many with `personalization_cache`

**Validation Rules**:
- Email must be valid format
- Password minimum 8 characters (enforced by better-auth)
- Background fields must be one of enum values

---

### 2. ChatMessage (Neon Postgres)

**Purpose**: Store chatbot conversations for history and analytics

**Table**: `chat_messages`

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]',
    selected_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_chat_created ON chat_messages(created_at DESC);
```

**Attributes**:
- `id`: UUID primary key
- `user_id`: Foreign key to users (nullable for anonymous users)
- `question`: User's question text
- `answer`: RAG chatbot's response
- `sources`: JSONB array of source references `[{chapter, module, file_path, heading}]`
- `selected_text`: Optional text user selected before asking (for context)
- `created_at`: Conversation timestamp

**Relationships**:
- Many-to-one with `users`

**Sample Data**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-uuid",
  "question": "What is a ROS 2 node?",
  "answer": "A ROS 2 node is a process that performs computation...",
  "sources": [
    {
      "chapter": "week2-nodes",
      "module": "module-1-ros2",
      "file_path": "module-1-ros2/week2-nodes.md",
      "heading": "Understanding ROS 2 Nodes"
    }
  ],
  "selected_text": null,
  "created_at": "2025-12-12T10:30:00Z"
}
```

---

### 3. PersonalizationCache (Neon Postgres)

**Purpose**: Cache personalized content to avoid regenerating with GPT-4

**Table**: `personalization_cache`

```sql
CREATE TABLE personalization_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_path VARCHAR(255) NOT NULL,
    skill_level VARCHAR(50) NOT NULL CHECK (skill_level IN ('beginner', 'intermediate', 'advanced')),
    personalized_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, chapter_path, skill_level)
);

CREATE INDEX idx_personalization ON personalization_cache(user_id, chapter_path);
```

**Attributes**:
- `id`: UUID primary key
- `user_id`: Foreign key to users
- `chapter_path`: Relative path to chapter (e.g., `module-1-ros2/week2-nodes.md`)
- `skill_level`: Personalization level (beginner/intermediate/advanced)
- `personalized_content`: Generated markdown content
- `created_at`: Cache timestamp

**Relationships**:
- Many-to-one with `users`

**Cache Strategy**:
- Unique constraint prevents duplicate entries
- TTL: No expiration (content is static)
- Invalidation: Manual if chapter content changes

---

### 4. TranslationCache (Neon Postgres)

**Purpose**: Cache translated content to reduce API calls

**Table**: `translation_cache`

```sql
CREATE TABLE translation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_path VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL DEFAULT 'urdu',
    translated_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chapter_path, language_code)
);

CREATE INDEX idx_translation ON translation_cache(chapter_path, language_code);
```

**Attributes**:
- `id`: UUID primary key
- `chapter_path`: Relative path to chapter
- `language_code`: Target language (`urdu` for this project)
- `translated_content`: Translated markdown content
- `created_at`: Cache timestamp

**Relationships**:
- Standalone (not user-specific)

**Cache Strategy**:
- Shared across all users (translations don't vary per user)
- TTL: No expiration
- Invalidation: Manual if chapter content changes

---

### 5. VectorEmbedding (Qdrant Cloud)

**Purpose**: Store semantic embeddings of book content for RAG retrieval

**Collection**: `book_content`

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="book_content",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-3-small
        distance=Distance.COSINE
    )
)
```

**Payload Schema**:
```python
{
    "id": "unique-chunk-id",
    "vector": [0.123, -0.456, ...],  # 1536 dimensions
    "payload": {
        "text": "Original text chunk content...",
        "chapter": "week2-nodes",
        "module": "module-1-ros2",
        "week": 2,
        "file_path": "module-1-ros2/week2-nodes.md",
        "heading": "Understanding ROS 2 Nodes",
        "chunk_index": 0  # Position within chapter
    }
}
```

**Attributes**:
- `text`: Original text chunk (~500 tokens)
- `chapter`: Chapter identifier
- `module`: Module identifier
- `week`: Week number (1-13)
- `file_path`: Relative path to source file
- `heading`: Section heading
- `chunk_index`: Ordinal position for maintaining context

**Indexing Strategy**:
- HNSW (Hierarchical Navigable Small World) for fast similarity search
- Cosine distance for semantic similarity
- Filters on `module` and `week` for scoped searches

---

## Database Migration Strategy

### Initial Setup

1. **Create Neon Project**:
   - Sign up at neon.tech
   - Create project: "physical-ai-textbook"
   - Get connection string

2. **Run Schema Creation**:
```bash
# Using psql or your preferred tool
psql $NEON_DATABASE_URL < migrations/001_initial_schema.sql
```

3. **Create Qdrant Collection**:
```bash
python backend/scripts/setup_qdrant.py
```

### Seed Data (for testing)

```sql
-- Test user
INSERT INTO users (email, password_hash, software_background, hardware_background)
VALUES ('test@example.com', '$2b$12$...', 'intermediate', 'hobbyist');
```

---

## Data Access Patterns

### 1. User Authentication
```sql
-- Login
SELECT id, email, software_background, hardware_background
FROM users
WHERE email = ? AND password_hash = ?;
```

### 2. Chatbot RAG Query
```python
# 1. Get embedding
embedding = openai.embeddings.create(input=question)

# 2. Search Qdrant
results = qdrant.search(
    collection_name="book_content",
    query_vector=embedding.data[0].embedding,
    limit=5
)

# 3. Save conversation
INSERT INTO chat_messages (user_id, question, answer, sources)
VALUES (?, ?, ?, ?);
```

### 3. Personalization with Cache
```sql
-- Check cache
SELECT personalized_content
FROM personalization_cache
WHERE user_id = ? AND chapter_path = ? AND skill_level = ?;

-- If miss, generate and cache
INSERT INTO personalization_cache (user_id, chapter_path, skill_level, personalized_content)
VALUES (?, ?, ?, ?)
ON CONFLICT (user_id, chapter_path, skill_level) DO NOTHING;
```

### 4. Translation with Cache
```sql
-- Check cache
SELECT translated_content
FROM translation_cache
WHERE chapter_path = ? AND language_code = 'urdu';

-- If miss, translate and cache
INSERT INTO translation_cache (chapter_path, language_code, translated_content)
VALUES (?, 'urdu', ?)
ON CONFLICT (chapter_path, language_code) DO NOTHING;
```

---

## Storage Estimates

| Entity | Avg Size | Count | Total |
|--------|----------|-------|-------|
| User | 500 bytes | 500 users | 250 KB |
| ChatMessage | 2 KB | 10K messages | 20 MB |
| PersonalizationCache | 20 KB | 500 users × 13 chapters | 130 MB |
| TranslationCache | 20 KB | 13 chapters | 260 KB |
| **Total (Postgres)** | | | **~150 MB** (fits in 512MB free tier) |
| VectorEmbedding | 6 KB | 10K chunks | 60 MB (vectors + metadata) |
| **Total (Qdrant)** | | | **~60 MB** (fits in 1GB free tier) |

---

## Security Considerations

1. **Password Storage**: Use bcrypt via better-auth (never store plain text)
2. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
3. **User Data**: No PII beyond email; GDPR-compliant deletion via CASCADE
4. **API Keys**: Store in environment variables, never in database

---

## Data Model Status

**Status**: ✅ Finalized
**Next**: Create API contracts
**Last Updated**: 2025-12-12
