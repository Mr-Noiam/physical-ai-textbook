# Physical AI & Humanoid Robotics - Interactive Textbook

An AI-native interactive textbook platform for teaching Physical AI & Humanoid Robotics, featuring an embedded RAG chatbot powered by OpenAI, authentication, content personalization, and Urdu translation capabilities.

## 🎯 Project Overview

This project is built for a hackathon with the following features:

- **Base (100 points)**: Docusaurus textbook + RAG chatbot
- **Bonus Features (200 points)**:
  - User authentication with better-auth (50 pts)
  - Content personalization based on user background (50 pts)
  - Urdu translation (50 pts)
  - Reusable Claude Code Intelligence (50 pts)

**Total Maximum Points**: 300

## 📚 Course Structure

The textbook covers **4 modules** across **13 weeks**:

1. **Module 1: ROS 2** (Weeks 1-4)
   - Foundations of Physical AI
   - ROS 2 architecture, nodes, topics, services
   - Building packages with Python
   - URDF for humanoid robots

2. **Module 2: Gazebo & Unity** (Weeks 5-6)
   - Gazebo simulation environments
   - Unity for robot visualization

3. **Module 3: NVIDIA Isaac** (Weeks 7-9)
   - Isaac Sim for synthetic data
   - Isaac ROS for VSLAM
   - Nav2 for bipedal navigation

4. **Module 4: Vision-Language-Action (VLA)** (Weeks 10-13)
   - VLA convergence concepts
   - Voice-to-Action with Whisper
   - Humanoid robot development
   - Capstone project

## 🛠️ Tech Stack

### Frontend
- **Docusaurus 3.x** - Static site generator
- **React 18** + **TypeScript 5.x**
- **TailwindCSS** - Styling
- **Deployment**: GitHub Pages

### Backend
- **FastAPI 0.109+** (Python 3.11)
- **OpenAI API** - GPT-4 for chatbot, text-embedding-3-small for vectors
- **Neon Serverless Postgres** - User data, chat history, caches
- **Qdrant Cloud** - Vector database for RAG
- **better-auth** - TypeScript-first authentication
- **Deployment**: Railway or Render

## 🚀 Quick Start

### Prerequisites

- **Node.js 20 LTS** - For Docusaurus
- **Python 3.11+** - For FastAPI backend
- **Git** - Version control

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book_hackathon
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Frontend Setup (Docusaurus)**
   ```bash
   cd docusaurus
   npm install
   npm start
   ```
   Visit: http://localhost:3000

4. **Backend Setup (FastAPI)**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
   Visit: http://localhost:8000/docs

## 📖 Development Guide

### Project Structure

```
book_hackathon/
├── docusaurus/          # Frontend - Docusaurus site
│   ├── docs/           # Textbook content (Markdown)
│   └── src/            # React components (chatbot, auth, etc.)
├── backend/            # Backend - FastAPI server
│   ├── app/           # Application code
│   │   ├── api/       # API endpoints
│   │   ├── rag/       # RAG implementation
│   │   └── db/        # Database models & connections
│   └── tests/         # Backend tests
└── specs/             # Specification documents
```

### Running Tests

**Frontend**:
```bash
cd docusaurus
npm test
```

**Backend**:
```bash
cd backend
pytest
```

## 🌐 Cloud Services Setup

1. **OpenAI API** - Get API key from https://platform.openai.com/api-keys
2. **Neon Postgres** - Create free database at https://neon.tech
3. **Qdrant Cloud** - Create free cluster at https://cloud.qdrant.io
4. **GitHub Pages** - Enable in repository settings
5. **Railway** - Deploy backend at https://railway.app

See `specs/001-physical-ai-textbook/quickstart.md` for detailed setup instructions.

## 📝 Documentation

- **Feature Specification**: `specs/001-physical-ai-textbook/spec.md`
- **Implementation Plan**: `specs/001-physical-ai-textbook/plan.md`
- **Task Breakdown**: `specs/001-physical-ai-textbook/tasks.md`
- **API Contracts**: `specs/001-physical-ai-textbook/contracts/`
- **Data Model**: `specs/001-physical-ai-textbook/data-model.md`

## 🎓 Learning Outcomes

Students will learn to:
- Build ROS 2 systems for physical robots
- Simulate robots in Gazebo, Unity, and NVIDIA Isaac
- Integrate vision, language, and action for autonomous humanoids
- Deploy AI-powered robotic systems

## 📄 License

This project is created for educational purposes as part of a hackathon.

## 🤝 Contributing

This is a hackathon project with a tight timeline. For questions or issues, please open a GitHub issue.

---

**Built with**:
- Spec-Kit Plus (Spec-Driven Development)
- Claude Code (AI-assisted development)
- Modern web technologies (React, TypeScript, Python, FastAPI)
