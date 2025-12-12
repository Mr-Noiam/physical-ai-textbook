# Project Overview

## About This Project

This is a **Spec-Driven Development (SDD) Framework** project initialized from the Specify template. It's set up to guide structured feature development using AI-assisted workflows.

## Core Structure

### 1. Gemini CLI Commands (`.gemini/commands/`)

The framework provides the following slash commands:

- **`/sp.specify`** - Create feature specifications from natural language
- **`/sp.clarify`** - Ask targeted questions to clarify ambiguous requirements
- **`/sp.plan`** - Generate technical implementation plans
- **`/sp.tasks`** - Break down features into dependency-ordered tasks
- **`/sp.implement`** - Execute the implementation plan
- **`/sp.analyze`** - Check consistency across spec/plan/tasks
- **`/sp.checklist`** - Generate quality validation checklists
- **`/sp.adr`** - Document architectural decisions
- **`/sp.phr`** - Record prompt history for learning
- **`/sp.git.commit_pr`** - Autonomous git workflow agent
- **`/sp.constitution`** - Define project principles

### 2. Templates (`.specify/templates/`)

Pre-built templates for structured documentation:

- `spec-template.md` - Feature specification structure
- `plan-template.md` - Technical implementation plan
- `tasks-template.md` - Task breakdown with user story organization
- `adr-template.md` - Architecture decision records
- `phr-template.prompt.md` - Prompt history records
- `checklist-template.md` - Quality validation checklists

### 3. PowerShell Automation (`.specify/scripts/powershell/`)

Scripts for workflow automation:

- `create-new-feature.ps1` - Creates numbered feature branches and directories
- `check-prerequisites.ps1` - Validates workflow prerequisites
- `setup-plan.ps1` - Initializes planning phase
- `update-agent-context.ps1` - Updates AI agent context
- `common.ps1` - Shared utility functions

### 4. Constitution (`.specify/memory/constitution.md`)

- Template for defining project principles
- Currently has placeholder values to be filled in

## Key Features

### Workflow Phases

1. **Specify** → Create feature spec from natural language
2. **Clarify** → Resolve ambiguities (max 5 questions)
3. **Plan** → Generate technical architecture
4. **Tasks** → Break into executable tasks organized by user story
5. **Implement** → Execute tasks with checklist validation

### Quality Controls

- Constitution-based governance
- Automated checklist generation
- Cross-artifact consistency analysis
- Architectural decision documentation
- Test-driven development support (optional)

### Unique Aspects

- **User stories are independently testable** - MVP-first approach
- **Tasks organized by priority** - P1, P2, P3 for incremental delivery
- **Parallel execution markers** - [P] indicates tasks that can run concurrently
- **Automated PHR creation** - Prompt History Records for learning and traceability
- **Git workflow automation** - Autonomous commit and PR creation

## Workflow Example

### Phase 1: Specify
```
/sp.specify Add user authentication with email and password
```
Creates a feature branch (e.g., `001-user-auth`) and generates `spec.md`

### Phase 2: Clarify (Optional)
```
/sp.clarify
```
AI asks up to 5 targeted questions to resolve ambiguities

### Phase 3: Plan
```
/sp.plan
```
Generates:
- `plan.md` - Technical architecture
- `research.md` - Design decisions
- `data-model.md` - Entity definitions
- `contracts/` - API specifications
- `quickstart.md` - Integration scenarios

### Phase 4: Tasks
```
/sp.tasks
```
Creates `tasks.md` with:
- Setup phase
- Foundational phase
- User story phases (P1, P2, P3)
- Polish phase

### Phase 5: Implement
```
/sp.implement
```
Executes tasks with:
- Checklist validation
- Test-driven development
- Progress tracking
- Error handling

## Directory Structure

### Feature Organization
```
specs/001-feature-name/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan
├── research.md          # Design decisions
├── data-model.md        # Entity definitions
├── contracts/           # API specifications
├── quickstart.md        # Integration scenarios
├── tasks.md             # Task breakdown
└── checklists/          # Quality checklists
    ├── requirements.md
    ├── ux.md
    └── security.md
```

### History Tracking
```
history/
├── prompts/
│   ├── constitution/    # Constitution updates
│   ├── general/         # General work
│   └── 001-feature-name/  # Feature-specific prompts
└── adr/                 # Architecture Decision Records
```

## Current State

The project is **initialized but empty** - no features have been created yet. It's ready for you to start your first feature with `/sp.specify <feature description>`.

## Getting Started

### Step 1: Define Project Constitution (Optional but Recommended)

Set up your project's core principles:
```
/sp.constitution
```

### Step 2: Create Your First Feature

Start with a natural language description:
```
/sp.specify Build a landing page for a podcast website
```

### Step 3: Follow the Workflow

Proceed through the phases:
1. Clarify requirements if needed
2. Generate implementation plan
3. Create task breakdown
4. Execute implementation

## Best Practices

### User Story Organization

- **P1 (Priority 1)** - MVP features (implement first)
- **P2 (Priority 2)** - Important enhancements
- **P3 (Priority 3)** - Nice-to-have features

Each user story should be:
- Independently implementable
- Independently testable
- Deliverable as a standalone increment

### Task Format

Tasks follow this structure:
```
- [ ] [T001] [P] [US1] Description with file path
```

- `T001` - Sequential task ID
- `[P]` - Parallel execution marker (optional)
- `[US1]` - User story label
- Description includes exact file paths

### Quality Validation

Checklists validate requirements quality, not implementation:

**Wrong:**
- "Verify button clicks correctly" (tests implementation)

**Correct:**
- "Are button interaction requirements defined?" (tests requirements)

## Advanced Features

### Architectural Decision Records (ADRs)

Document significant technical decisions:
- Technology stack choices
- Architecture patterns
- Design tradeoffs

### Prompt History Records (PHRs)

Automatically capture:
- User prompts (verbatim)
- AI responses
- Files modified
- Tests run
- Learning insights

### Constitution-Based Governance

Define and enforce:
- Code quality standards
- Testing requirements
- Security policies
- Performance targets

## Support

For issues or questions:
- Check the Specify documentation
- Review example workflows in `history/`
- Examine template files in `.specify/templates/`

---

**Version:** Initial Setup
**Created:** 2025-12-12
**Status:** Ready for first feature

---

# Current Project: Physical AI & Humanoid Robotics Textbook

## Project Overview

This project is a hackathon submission for **Panaversity** to create an AI-native textbook for teaching Physical AI & Humanoid Robotics. The project aims to build a modern, interactive learning platform that goes beyond traditional textbooks by integrating AI-powered features.

### Hackathon Goals

**Base Requirements (100 points):**
1. Create a comprehensive textbook using Docusaurus
2. Deploy to GitHub Pages
3. Integrate RAG chatbot for intelligent Q&A about book content
4. Support text-selection-based questions

**Bonus Features (up to 200 additional points):**
- Reusable Claude Code Subagents and Agent Skills (50 points)
- User authentication with better-auth.com (50 points)
- Content personalization based on user background (50 points)
- Urdu translation capability (50 points)

## Feature Specification

**Branch:** `001-physical-ai-textbook`
**Specification:** `specs/001-physical-ai-textbook/spec.md`

### User Stories (Priority Order)

#### Priority 1 (P1): Basic Textbook Reading Experience
- **Goal:** Deliver core textbook content via Docusaurus
- **Content:** 4 modules covering 13 weeks of material
  - Module 1: The Robotic Nervous System (ROS 2)
  - Module 2: The Digital Twin (Gazebo & Unity)
  - Module 3: The AI-Robot Brain (NVIDIA Isaac)
  - Module 4: Vision-Language-Action (VLA)
- **Deliverable:** Responsive web-based textbook deployed on GitHub Pages
- **MVP Status:** This is the minimum viable product

#### Priority 2 (P2): Intelligent RAG Chatbot Assistant
- **Goal:** Provide AI-powered learning assistance
- **Technology Stack:**
  - OpenAI Agents/ChatKit SDKs for natural language processing
  - FastAPI for backend API
  - Neon Serverless Postgres for conversation history
  - Qdrant Cloud (Free Tier) for vector storage
- **Features:**
  - Answer questions about book content using RAG retrieval
  - Support text-selection-based questions
  - Provide source references for all answers
  - Handle concurrent users efficiently

#### Priority 3 (P3): User Authentication & Profile Management
- **Goal:** Enable user-specific experiences
- **Technology:** better-auth.com
- **Features:**
  - Signup with email and password
  - Collect software background (beginner/intermediate/advanced)
  - Collect hardware background (no experience/hobbyist/professional)
  - Persist user profiles across sessions

#### Priority 4 (P4): Personalized Content Experience
- **Goal:** Adapt content to user skill level
- **Features:**
  - "Personalize Content" button at chapter start
  - Content adaptation based on user background
  - Beginner: More detailed explanations and foundational concepts
  - Advanced: Concise content with emphasis on advanced topics
  - Cache personalized content for performance

#### Priority 5 (P5): Urdu Translation
- **Goal:** Make content accessible to Urdu-speaking students
- **Features:**
  - "Translate to Urdu" button at chapter start
  - Preserve formatting during translation
  - Keep code examples in English
  - Use proper technical terminology in Urdu
  - Cache translations to reduce API calls

## Course Content Structure

### Weekly Breakdown (13 Weeks)

**Weeks 1-2:** Introduction to Physical AI
- Foundations of Physical AI and embodied intelligence
- From digital AI to robots that understand physical laws
- Overview of humanoid robotics landscape
- Sensor systems: LIDAR, cameras, IMUs, force/torque sensors

**Weeks 3-5:** ROS 2 Fundamentals
- ROS 2 architecture and core concepts
- Nodes, topics, services, and actions
- Building ROS 2 packages with Python
- Launch files and parameter management

**Weeks 6-7:** Robot Simulation with Gazebo
- Gazebo simulation environment setup
- URDF and SDF robot description formats
- Physics simulation and sensor simulation
- Introduction to Unity for robot visualization

**Weeks 8-10:** NVIDIA Isaac Platform
- NVIDIA Isaac SDK and Isaac Sim
- AI-powered perception and manipulation
- Reinforcement learning for robot control
- Sim-to-real transfer techniques

**Weeks 11-12:** Humanoid Robot Development
- Humanoid robot kinematics and dynamics
- Bipedal locomotion and balance control
- Manipulation and grasping with humanoid hands
- Natural human-robot interaction design

**Week 13:** Conversational Robotics
- Integrating GPT models for conversational AI in robots
- Speech recognition and natural language understanding
- Multi-modal interaction: speech, gesture, vision

## Technical Architecture

### Frontend
- **Framework:** Docusaurus (static site generator)
- **Hosting:** GitHub Pages
- **Features:** Responsive design, search, navigation
- **Embedded:** RAG chatbot widget on every page

### Backend
- **API Framework:** FastAPI (Python)
- **AI Integration:** OpenAI Agents/ChatKit SDKs
- **Vector Database:** Qdrant Cloud (Free Tier)
- **Relational Database:** Neon Serverless Postgres
- **Authentication:** better-auth.com

### Data Flow
1. **Content Ingestion:** Book content → Vector embeddings → Qdrant
2. **User Questions:** Question → RAG retrieval → Context + LLM → Answer
3. **Personalization:** User background → Content adapter → Personalized view
4. **Translation:** Chapter content → Translation API → Urdu content

## Key Entities

- **User:** Authentication, background info, preferences
- **Chapter:** Module, week, content, code examples
- **ChatMessage:** Question, answer, sources, timestamp
- **VectorEmbedding:** Chapter reference, content chunk, embedding vector
- **PersonalizationCache:** User, chapter, skill level, generated content
- **TranslationCache:** Chapter, language, translated content

## Success Metrics

### Functionality (100 base points)
- ✓ All 4 modules published to GitHub Pages
- ✓ RAG chatbot answers 90%+ of questions accurately
- ✓ Chatbot response time under 3 seconds
- ✓ Support 50+ concurrent users

### Bonus Features (200 additional points)
- Claude Code Subagents/Skills: 50 points
- Authentication & profiling: 50 points
- Content personalization: 50 points
- Urdu translation: 50 points

## Development Approach

This project follows Spec-Driven Development using:
- Feature specifications with prioritized user stories
- Independent, testable increments (MVP-first)
- Frequent commits at every milestone
- Claude Code and Spec-Kit Plus integration
- Reusable intelligence via Subagents and Skills

## Project Status

**Current Phase:** Specification Complete ✓
**Next Phase:** Implementation Planning
**Branch:** `001-physical-ai-textbook`
**Last Updated:** 2025-12-12
