# Tasks: Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-physical-ai-textbook/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, or SETUP)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] [SETUP] Create root project structure with `docusaurus/` and `backend/` directories
- [X] T002 [P] [SETUP] Create `.env.example` file with all required environment variables
- [X] T003 [P] [SETUP] Update root `README.md` with project overview and setup instructions
- [X] T004 [P] [SETUP] Create `.gitignore` entries for `node_modules/`, `venv/`, `.env`, `__pycache__/`

**Checkpoint**: Basic project structure created

---

## Phase 2: Foundational - Frontend Setup (Blocking for US1)

**Purpose**: Core Docusaurus infrastructure that MUST be complete before content can be written

**⚠️ CRITICAL**: No content work can begin until this phase is complete

- [X] T005 [SETUP] Initialize Docusaurus project in `docusaurus/` directory using `npx create-docusaurus@latest`
- [X] T006 [SETUP] Configure `docusaurus/docusaurus.config.js` with site title "Physical AI & Humanoid Robotics", GitHub Pages deployment settings
- [X] T007 [SETUP] Create module directories in `docusaurus/docs/`: `module-1-ros2/`, `module-2-gazebo/`, `module-3-isaac/`, `module-4-vla/`
- [X] T008 [SETUP] Configure `docusaurus/sidebars.js` with 4 module categories
- [X] T009 [SETUP] Test Docusaurus build locally with `npm start`

**Checkpoint**: Docusaurus running locally on port 3000

---

## Phase 3: Foundational - Backend Setup (Blocking for US2)

**Purpose**: Core FastAPI infrastructure that MUST be complete before RAG can be implemented

**⚠️ CRITICAL**: No RAG work can begin until this phase is complete

- [X] T010 [SETUP] Create Python virtual environment in `backend/` with `python -m venv venv`
- [X] T011 [SETUP] Create `backend/requirements.txt` with dependencies: fastapi, uvicorn, openai, qdrant-client, psycopg[binary], sqlalchemy, python-jose, passlib, python-multipart, langchain
- [X] T012 [SETUP] Create `backend/app/main.py` with FastAPI app initialization and CORS middleware
- [X] T013 [SETUP] Create `backend/app/config.py` for environment variable management
- [X] T014 [P] [SETUP] Create database connection in `backend/app/db/neon.py` using SQLAlchemy
- [X] T015 [P] [SETUP] Create Qdrant client in `backend/app/db/qdrant.py`
- [X] T016 [SETUP] Create database models in `backend/app/db/models.py` (User, ChatMessage, PersonalizationCache, TranslationCache)
- [X] T017 [SETUP] Create database setup script `backend/scripts/setup_database.py` to create all tables
- [X] T018 [SETUP] Test FastAPI server runs with `uvicorn app.main:app --reload`

**Checkpoint**: FastAPI running locally on port 8000 with /docs accessible

---

## Phase 4: User Story 1 - Basic Textbook (Priority: P1) 🎯 MVP

**Goal**: Deliver core textbook content via Docusaurus

**Independent Test**: Navigate all chapters, view content, verify 4 modules with 13 weeks present

### Content Writing for User Story 1

- [X] T019 [P] [US1] Write `docusaurus/docs/intro.md` - Course overview, learning outcomes, hardware requirements
- [X] T020 [P] [US1] Write `docusaurus/docs/module-1-ros2/week1-intro.md` - Foundations of Physical AI, embodied intelligence
- [X] T021 [P] [US1] Write `docusaurus/docs/module-1-ros2/week2-fundamentals.md` - ROS 2 architecture, nodes, topics, services
- [X] T022 [P] [US1] Write `docusaurus/docs/module-1-ros2/week3-python.md` - Building ROS 2 packages with Python, rclpy
- [X] T023 [P] [US1] Write `docusaurus/docs/module-1-ros2/week4-urdf.md` - URDF for humanoids, robot description
- [X] T024 [P] [US1] Write `docusaurus/docs/module-2-gazebo/week5-simulation.md` - Gazebo environment, physics simulation
- [X] T025 [P] [US1] Write `docusaurus/docs/module-2-gazebo/week6-unity.md` - Unity for robot visualization, sensor simulation
- [X] T026 [P] [US1] Write `docusaurus/docs/module-3-isaac/week7-isaac-sim.md` - NVIDIA Isaac Sim, synthetic data generation
- [X] T027 [P] [US1] Write `docusaurus/docs/module-3-isaac/week8-isaac-ros.md` - Isaac ROS, VSLAM, hardware acceleration
- [X] T028 [P] [US1] Write `docusaurus/docs/module-3-isaac/week9-navigation.md` - Nav2, path planning for bipedal movement
- [X] T029 [P] [US1] Write `docusaurus/docs/module-4-vla/week10-vla-intro.md` - Vision-Language-Action convergence
- [X] T030 [P] [US1] Write `docusaurus/docs/module-4-vla/week11-voice.md` - Voice-to-Action with Whisper, cognitive planning
- [X] T031 [P] [US1] Write `docusaurus/docs/module-4-vla/week12-humanoid.md` - Humanoid robot development, kinematics
- [X] T032 [P] [US1] Write `docusaurus/docs/module-4-vla/week13-capstone.md` - Capstone project: Autonomous humanoid

### Deployment for User Story 1

- [~] T033 [US1] Configure GitHub Pages in repository settings (source: GitHub Actions) - MANUAL: User must enable in GitHub
- [X] T034 [US1] Create `.github/workflows/deploy-docusaurus.yml` for automatic deployment
- [X] T035 [US1] Test deployment by running `npm run deploy` from `docusaurus/` - DOCS: Created DEPLOYMENT.md guide
- [~] T036 [US1] Verify deployed site is accessible at GitHub Pages URL - PENDING: After user enables Pages

**Checkpoint**: All 13 weeks of content published and accessible on GitHub Pages ✅ 50 points

---

## Phase 5: User Story 2 - RAG Chatbot (Priority: P2) 🎯 MVP

**Goal**: Provide AI-powered learning assistance with RAG chatbot

**Independent Test**: Ask questions about book content, verify accurate answers with sources

### RAG Backend Implementation

- [X] T037 [US2] Create `backend/app/rag/embeddings.py` with OpenAI embedding generation function
- [ ] T038 [US2] Create `backend/app/rag/ingestion.py` to read markdown files, split into chunks (~500 tokens), generate embeddings
- [ ] T039 [US2] Create `backend/scripts/ingest_content.py` to batch-process all Docusaurus content into Qdrant
- [ ] T040 [US2] Create Qdrant collection `book_content` with 1536 dimensions, cosine distance
- [ ] T041 [US2] Run content ingestion script to populate Qdrant with book embeddings
- [ ] T042 [US2] Create `backend/app/rag/retrieval.py` with vector similarity search function
- [ ] T043 [US2] Create `backend/app/rag/chatbot.py` with RAG logic: embed question → search → construct prompt → call GPT-4
- [ ] T044 [US2] Create `backend/app/api/v1/chatbot.py` with POST `/api/v1/chatbot/ask` endpoint
- [ ] T045 [US2] Add logic to save conversations to `chat_messages` table
- [ ] T046 [US2] Add support for `selected_text` parameter in chatbot endpoint
- [ ] T047 [US2] Test chatbot API with curl/Postman: ask "What is a ROS 2 node?"

### RAG Frontend Integration

- [ ] T048 [US2] Create React component `docusaurus/src/components/ChatbotWidget/index.tsx` with chat UI
- [ ] T049 [US2] Add text selection handler to enable "Ask about selected text" feature
- [ ] T050 [US2] Style chatbot widget with TailwindCSS (floating button, chat window, message bubbles)
- [ ] T051 [US2] Add API integration to call backend `/api/v1/chatbot/ask` endpoint
- [ ] T052 [US2] Display sources in chatbot responses with links to book sections
- [ ] T053 [US2] Add chatbot widget to Docusaurus by modifying `docusaurus/src/theme/Root.tsx`
- [ ] T054 [US2] Test chatbot end-to-end: ask question → see answer with sources

### Backend Deployment

- [ ] T055 [US2] Create `backend/Dockerfile` for containerizing FastAPI app
- [ ] T056 [US2] Sign up for Railway account and create new project
- [ ] T057 [US2] Connect Railway to GitHub repository
- [ ] T058 [US2] Configure environment variables in Railway: OPENAI_API_KEY, NEON_DATABASE_URL, QDRANT_URL, QDRANT_API_KEY
- [ ] T059 [US2] Deploy backend to Railway and verify /docs endpoint accessible
- [ ] T060 [US2] Update frontend `VITE_API_URL` to point to Railway backend URL
- [ ] T061 [US2] Test deployed chatbot from GitHub Pages site

**Checkpoint**: Working RAG chatbot integrated and deployed ✅ 50 points (Total: 100 points - MVP COMPLETE!)

---

## Phase 6: User Story 3 - Authentication (Priority: P3) 💰 50 Bonus Points

**Goal**: Enable user-specific experiences with authentication

**Independent Test**: Create account, log in, verify profile persistence

### Authentication Backend

- [ ] T062 [US3] Install better-auth library: `npm install better-auth` in backend directory
- [ ] T063 [US3] Create `backend/app/auth/better_auth.py` with better-auth configuration
- [ ] T064 [US3] Create POST `/api/v1/auth/signup` endpoint in `backend/app/api/v1/auth.py`
- [ ] T065 [US3] Add validation for email format and password strength (min 8 chars)
- [ ] T066 [US3] Add fields for software_background and hardware_background in signup
- [ ] T067 [US3] Hash passwords with bcrypt before storing in database
- [ ] T068 [US3] Create POST `/api/v1/auth/signin` endpoint
- [ ] T069 [US3] Generate JWT tokens on successful signin
- [ ] T070 [US3] Create `backend/app/auth/middleware.py` for JWT verification
- [ ] T071 [US3] Test signup/signin with curl: create user → signin → receive token

### Authentication Frontend

- [ ] T072 [US3] Create React component `docusaurus/src/components/AuthModal/index.tsx` with signup/signin forms
- [ ] T073 [US3] Add form fields: email, password, software_background dropdown, hardware_background dropdown
- [ ] T074 [US3] Add form validation and error handling
- [ ] T075 [US3] Integrate with backend auth endpoints
- [ ] T076 [US3] Store JWT token in localStorage on successful signin
- [ ] T077 [US3] Create user profile component showing background info
- [ ] T078 [US3] Add "Sign In" button to Docusaurus navbar
- [ ] T079 [US3] Add "Profile" link for logged-in users
- [ ] T080 [US3] Test auth flow: signup → verify email/password → signin → see profile

**Checkpoint**: Users can create accounts and sign in ✅ 50 bonus points (Total: 150 points)

---

## Phase 7: User Story 4 - Personalization (Priority: P4) 💰 50 Bonus Points

**Goal**: Adapt content to user skill level

**Independent Test**: Log in with different backgrounds, personalize content, verify adaptation

### Personalization Backend

- [ ] T081 [US4] Create `backend/app/services/personalization.py` with GPT-4 content adaptation logic
- [ ] T082 [US4] Implement prompt templates for beginner/intermediate/advanced adaptation
- [ ] T083 [US4] Add cache lookup in `personalization_cache` table before generating
- [ ] T084 [US4] Add cache storage after generating personalized content
- [ ] T085 [US4] Create POST `/api/v1/personalize` endpoint in `backend/app/api/v1/personalize.py`
- [ ] T086 [US4] Protect endpoint with JWT authentication middleware
- [ ] T087 [US4] Test personalization API: send chapter → receive adapted content

### Personalization Frontend

- [ ] T088 [US4] Create React component `docusaurus/src/components/PersonalizeButton/index.tsx`
- [ ] T089 [US4] Add "Personalize Content" button at top of each chapter page
- [ ] T090 [US4] Only show button if user is logged in
- [ ] T091 [US4] On button click, fetch personalized content from backend
- [ ] T092 [US4] Replace chapter content with personalized version
- [ ] T093 [US4] Add "Show Original" toggle to switch back
- [ ] T094 [US4] Add loading spinner while content is being generated
- [ ] T095 [US4] Test with beginner user: verify more detailed explanations
- [ ] T096 [US4] Test with advanced user: verify concise content with advanced topics

**Checkpoint**: Content personalization working for all skill levels ✅ 50 bonus points (Total: 200 points)

---

## Phase 8: User Story 5 - Urdu Translation (Priority: P5) 💰 50 Bonus Points

**Goal**: Make content accessible to Urdu speakers

**Independent Test**: Click translate button, verify Urdu translation with preserved formatting

### Translation Backend

- [ ] T097 [US5] Create `backend/app/services/translation.py` with GPT-4 Urdu translation logic
- [ ] T098 [US5] Implement prompt template with rules: keep code in English, use technical terms properly
- [ ] T099 [US5] Add cache lookup in `translation_cache` table before translating
- [ ] T100 [US5] Add cache storage after translating content
- [ ] T101 [US5] Create POST `/api/v1/translate` endpoint in `backend/app/api/v1/translate.py`
- [ ] T102 [US5] Protect endpoint with JWT authentication middleware
- [ ] T103 [US5] Test translation API: send chapter → receive Urdu content

### Translation Frontend

- [ ] T104 [US5] Create React component `docusaurus/src/components/TranslateButton/index.tsx`
- [ ] T105 [US5] Add "Translate to Urdu" button at top of each chapter page
- [ ] T106 [US5] Only show button if user is logged in
- [ ] T107 [US5] On button click, fetch translated content from backend
- [ ] T108 [US5] Replace chapter content with Urdu version (preserve markdown rendering)
- [ ] T109 [US5] Verify code blocks remain in English
- [ ] T110 [US5] Add "Show English" toggle to switch back
- [ ] T111 [US5] Add loading spinner while content is being translated
- [ ] T112 [US5] Test translation: verify Urdu text quality and technical terminology

**Checkpoint**: Urdu translation working with proper formatting ✅ 50 bonus points (Total: 250 points)

---

## Phase 9: Reusable Intelligence (Bonus) 💰 50 Bonus Points

**Purpose**: Create reusable Claude Code Subagents and Agent Skills

### Claude Code Subagents

- [ ] T113 [P] [BONUS] Create subagent for content generation in `.claude/subagents/content-generator/`
- [ ] T114 [P] [BONUS] Create subagent for code example creation in `.claude/subagents/code-generator/`
- [ ] T115 [P] [BONUS] Create subagent for technical concept explanation in `.claude/subagents/explainer/`
- [ ] T116 [BONUS] Document all subagents with README.md files showing usage examples

### Agent Skills

- [ ] T117 [P] [BONUS] Create skill for markdown formatting in `.claude/skills/markdown-formatter/`
- [ ] T118 [P] [BONUS] Create skill for code syntax validation in `.claude/skills/code-validator/`
- [ ] T119 [P] [BONUS] Create skill for technical writing assistance in `.claude/skills/tech-writer/`
- [ ] T120 [BONUS] Document all skills with examples and reusability guidelines

**Checkpoint**: 3+ subagents and 3+ skills documented ✅ 50 bonus points (Total: 300 points - MAXIMUM!)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T121 [P] [POLISH] Add error handling to all API endpoints
- [ ] T122 [P] [POLISH] Add loading states to all frontend components
- [ ] T123 [P] [POLISH] Optimize images in `docusaurus/static/img/` (convert to WebP)
- [ ] T124 [P] [POLISH] Add rate limiting to backend API to prevent abuse
- [ ] T125 [P] [POLISH] Add API request logging for debugging
- [ ] T126 [POLISH] Test entire application end-to-end on mobile devices
- [ ] T127 [POLISH] Test with 50 concurrent users using load testing tool
- [ ] T128 [POLISH] Verify page load times <2s on standard broadband
- [ ] T129 [POLISH] Verify chatbot response times <3s average
- [ ] T130 [POLISH] Run security audit: check for SQL injection, XSS vulnerabilities
- [ ] T131 [POLISH] Update README.md with complete setup instructions
- [ ] T132 [POLISH] Create comprehensive API documentation in backend
- [ ] T133 [POLISH] Add troubleshooting guide to quickstart.md

**Checkpoint**: Production-ready application

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Frontend Foundational (Phase 2)**: Depends on Setup completion - BLOCKS US1
- **Backend Foundational (Phase 3)**: Depends on Setup completion - BLOCKS US2
- **User Story 1 (Phase 4)**: Depends on Frontend Foundational (Phase 2)
- **User Story 2 (Phase 5)**: Depends on Backend Foundational (Phase 3)
- **User Story 3 (Phase 6)**: Depends on Backend Foundational (Phase 3)
- **User Story 4 (Phase 7)**: Depends on User Story 3 (authentication required)
- **User Story 5 (Phase 8)**: Depends on User Story 3 (authentication required)
- **Reusable Intelligence (Phase 9)**: Can run in parallel with other phases
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### Critical Path (Minimum for 100 points)

1. Phase 1: Setup (T001-T004)
2. Phase 2: Frontend Foundational (T005-T009)
3. Phase 3: Backend Foundational (T010-T018)
4. Phase 4: User Story 1 Content (T019-T036) → 50 points
5. Phase 5: User Story 2 RAG Chatbot (T037-T061) → +50 points = **100 points MVP**

### Bonus Features Path (for 300 points)

After critical path:
6. Phase 6: User Story 3 Authentication (T062-T080) → +50 = 150 points
7. Phase 7: User Story 4 Personalization (T081-T096) → +50 = 200 points
8. Phase 8: User Story 5 Translation (T097-T112) → +50 = 250 points
9. Phase 9: Reusable Intelligence (T113-T120) → +50 = **300 points MAXIMUM**

### Within Each User Story

- **Setup tasks** can run in parallel if marked [P]
- **Content writing** (T019-T032) can all run in parallel [P]
- **Backend before Frontend**: API endpoints must exist before UI integration
- **Core before Features**: MVP (US1+US2) before bonus features (US3-US5)

---

## Parallel Opportunities

**Phase 1 Setup**: All tasks T001-T004 can run in parallel

**Phase 4 Content Writing**: All tasks T019-T032 can run in parallel (14 chapters simultaneously)

**Phase 5 RAG Backend vs Frontend**: After T047 (backend tested), T048-T054 (frontend) can proceed in parallel with backend deployment (T055-T061)

**Phase 6-8**: After Phase 3 complete, US3, US4, US5 backends can be developed in parallel

**Phase 9**: All subagents and skills (T113-T120) can be created in parallel with any other phase

---

## Implementation Strategy

### MVP First (100 Base Points)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Frontend Foundational (T005-T009)
3. Complete Phase 3: Backend Foundational (T010-T018)
4. Complete Phase 4: User Story 1 (T019-T036) → 50 points
5. Complete Phase 5: User Story 2 (T037-T061) → 100 points total
6. **STOP and VALIDATE**: Test entire MVP independently
7. Deploy and demo if ready

### Incremental Delivery (Maximum Points)

1. Complete MVP (100 points) → Deploy
2. Add User Story 3: Authentication (T062-T080) → 150 points → Deploy
3. Add User Story 4: Personalization (T081-T096) → 200 points → Deploy
4. Add User Story 5: Translation (T097-T112) → 250 points → Deploy
5. Add Reusable Intelligence (T113-T120) → 300 points → Deploy
6. Polish and optimize (T121-T133) → Production ready

---

## Task Statistics

**Total Tasks**: 133 tasks
- Setup: 18 tasks (T001-T018)
- US1 Content: 18 tasks (T019-T036) → 50 points
- US2 Chatbot: 25 tasks (T037-T061) → 50 points
- US3 Auth: 19 tasks (T062-T080) → 50 points
- US4 Personalize: 16 tasks (T081-T096) → 50 points
- US5 Translate: 16 tasks (T097-T112) → 50 points
- Bonus Intelligence: 8 tasks (T113-T120) → 50 points
- Polish: 13 tasks (T121-T133)

**Parallelizable Tasks**: 35 tasks marked [P]
**Sequential Tasks**: 98 tasks

**Estimated Effort**:
- MVP (T001-T061): ~40-60 hours (critical path)
- All Bonus Features (T062-T120): ~30-40 hours
- Polish (T121-T133): ~10-15 hours
- **Total**: ~80-115 hours

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each completed task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Tasks Status**: ✅ Complete (133 tasks defined)
**Next Command**: `/sp.implement` to begin execution
**Ready For**: Implementation phase
**Last Updated**: 2025-12-12
