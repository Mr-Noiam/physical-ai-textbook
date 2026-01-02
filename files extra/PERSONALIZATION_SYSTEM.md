# Personalization System - Complete Documentation

**Status:** ✅ FULLY IMPLEMENTED
**Commit:** f8318e7
**Date:** 2024-12-24

---

## Overview

The Physical AI Textbook now includes a comprehensive personalization system that adapts content and chatbot responses to match each user's experience level. This creates an adaptive learning environment tailored to individual backgrounds.

---

## Features Implemented

### 1. User Profile Management

**Endpoint:** `PUT /api/v1/auth/profile`

Users can set two dimensions of experience:

#### Software/Programming Background
- **Beginner** - New to programming, needs step-by-step explanations
- **Intermediate** - Understands basic programming, can learn advanced patterns
- **Advanced** - Experienced programmer, ready for design patterns and optimization

#### Hardware/Electronics Background
- **No Experience** - Never worked with hardware, needs component explanations
- **Hobbyist** - Some DIY projects, familiar with basic electronics
- **Professional** - Works with hardware regularly, ready for technical specs

---

## How Personalization Works

### Backend Intelligence

When a user asks the chatbot a question, the system:

1. **Retrieves user profile** from database
2. **Extracts background levels** (software + hardware)
3. **Builds personalized system prompt** based on experience
4. **Generates tailored response** using GPT-4 with customized instructions

### Personalization Examples

#### Example 1: Beginner User
```
User Profile:
- Software: Beginner
- Hardware: No Experience

Question: "What is a ROS 2 node?"

System Prompt Includes:
- "Programming: Beginner level - explain code step-by-step, define technical terms"
- "Hardware: No prior experience - explain physical components clearly"

Response Style:
- Defines what ROS 2 is first
- Explains nodes in simple terms
- Shows code with line-by-line comments
- Avoids jargon or defines it when used
```

#### Example 2: Advanced User
```
User Profile:
- Software: Advanced
- Hardware: Professional

Question: "What is a ROS 2 node?"

System Prompt Includes:
- "Programming: Advanced level - discuss design patterns and best practices"
- "Hardware: Professional level - dive into technical specs and integration"

Response Style:
- Assumes knowledge of message-passing systems
- Discusses architectural patterns (pub/sub, services)
- References performance considerations
- Uses technical terminology directly
```

---

## Implementation Details

### Backend Components

#### 1. Profile Update API (`backend/app/api/v1/auth.py`)

```python
@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's personalization settings."""
    if request.software_background is not None:
        current_user.software_background = request.software_background

    if request.hardware_background is not None:
        current_user.hardware_background = request.hardware_background

    db.commit()
    db.refresh(current_user)

    return UserResponse(...)
```

**Request Format:**
```json
{
  "software_background": "intermediate",
  "hardware_background": "hobbyist"
}
```

#### 2. Personalized Chatbot (`backend/app/rag/chatbot.py`)

**System Prompt Builder:**
```python
def build_system_prompt(
    software_level: Optional[str] = None,
    hardware_level: Optional[str] = None
) -> str:
    """Build personalized system prompt based on user background."""

    base_prompt = "You are an expert teaching assistant..."

    if software_level == "beginner":
        personalization += "- Programming: Beginner level - explain code step-by-step..."
    elif software_level == "advanced":
        personalization += "- Programming: Advanced level - discuss design patterns..."

    # Similar for hardware_level

    return base_prompt + personalization + guidelines
```

**Answer Generation:**
```python
def generate_answer(
    question: str,
    selected_text: Optional[str] = None,
    top_k: int = 5,
    software_level: Optional[str] = None,  # NEW
    hardware_level: Optional[str] = None   # NEW
) -> ChatbotResponse:
    """Generate personalized answer using RAG."""

    # Build personalized system prompt
    system_prompt = build_system_prompt(software_level, hardware_level)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {question}..."}
    ]

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        ...
    )

    return ChatbotResponse(...)
```

#### 3. API Integration (`backend/app/api/v1/chatbot.py`)

```python
@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Ask question with personalized response."""

    # Extract user background for personalization
    software_level = current_user.software_background if current_user else None
    hardware_level = current_user.hardware_background if current_user else None

    # Generate answer using RAG (with personalization)
    chatbot_response = generate_answer(
        question=request.question,
        selected_text=request.selected_text,
        software_level=software_level,
        hardware_level=hardware_level
    )

    return AskQuestionResponse(...)
```

---

### Frontend Components

#### 1. User Profile Component (`docusaurus/src/components/UserProfile/`)

**Features:**
- Displays current email (read-only)
- Dropdown selectors for software/hardware background
- Save button with loading state
- Success/error messages
- Info box explaining benefits

**Code Structure:**
```tsx
export default function UserProfile(): JSX.Element {
  const { user, updateProfile, isLoading } = useAuth();
  const [softwareLevel, setSoftwareLevel] = useState<string>(user?.software_background || '');
  const [hardwareLevel, setHardwareLevel] = useState<string>(user?.hardware_background || '');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateProfile(softwareLevel || undefined, hardwareLevel || undefined);
    setSaveMessage('Profile updated successfully!');
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSave}>
        <select value={softwareLevel} onChange={(e) => setSoftwareLevel(e.target.value)}>
          <option value="">Select your level...</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>

        {/* Similar for hardware */}

        <button type="submit">Save Changes</button>
      </form>
    </div>
  );
}
```

#### 2. Profile Page (`docusaurus/src/pages/profile.tsx`)

```tsx
export default function ProfilePage(): JSX.Element {
  return (
    <Layout title="Profile" description="Manage your profile and personalization settings">
      <UserProfile />
    </Layout>
  );
}
```

**URL:** `/profile`

#### 3. Enhanced User Menu (`docusaurus/src/components/UserMenu/`)

**Changes:**
- Added "⚙️ Profile Settings" link in dropdown
- Shows current software/hardware levels if set
- Link navigates to `/profile` page

```tsx
{isOpen && (
  <div className={styles.dropdown}>
    <div className={styles.userInfo}>
      <div className={styles.infoRow}>
        <strong>Email:</strong> {user.email}
      </div>
      {user.software_background && (
        <div className={styles.infoRow}>
          <strong>Software:</strong> {user.software_background}
        </div>
      )}
      {user.hardware_background && (
        <div className={styles.infoRow}>
          <strong>Hardware:</strong> {user.hardware_background}
        </div>
      )}
    </div>
    <div className={styles.menuActions}>
      <a href="/profile" className={styles.profileLink}>
        ⚙️ Profile Settings
      </a>
      <button className={styles.logoutButton} onClick={handleLogout}>
        🚪 Logout
      </button>
    </div>
  </div>
)}
```

#### 4. Auth Context Update (`docusaurus/src/contexts/AuthContext.tsx`)

**New Method:**
```tsx
const updateProfile = async (
  software_background?: string,
  hardware_background?: string
) => {
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/auth/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      software_background,
      hardware_background,
    }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || 'Profile update failed');
  }

  const userData = await response.json();
  setUser(userData);
};
```

**Added to Context:**
```tsx
<AuthContext.Provider
  value={{
    user,
    token,
    login,
    signup,
    logout,
    updateProfile,  // NEW
    forgotPassword,
    resetPassword,
    isLoading,
    error,
  }}
>
  {children}
</AuthContext.Provider>
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    -- Personalization fields
    software_background software_level,  -- ENUM: beginner, intermediate, advanced
    hardware_background hardware_level,  -- ENUM: no_experience, hobbyist, professional

    -- Other fields
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**Enums:**
```sql
CREATE TYPE software_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE hardware_level AS ENUM ('no_experience', 'hobbyist', 'professional');
```

---

## User Flow

### 1. New User Signup

```
User visits site → Clicks "Login / Sign Up" → Selects "Sign Up" tab

Form includes:
- Email (required)
- Password (required)
- Software Background (optional)
- Hardware Background (optional)

User can:
- Set preferences now → Get personalized responses immediately
- Skip preferences → Set later via Profile page
```

### 2. Update Preferences

```
User logs in → Clicks user menu (email in navbar) → Selects "⚙️ Profile Settings"

Profile Page shows:
- Current email (read-only)
- Software background dropdown
- Hardware background dropdown
- Save Changes button
- Info box explaining benefits

User selects levels → Clicks Save → Preferences updated
```

### 3. Using Chatbot

```
User asks question → Backend receives request

Backend checks:
- Is user authenticated? → Get user profile
- Extract software_background and hardware_background
- Pass to RAG system

RAG system:
- Builds personalized system prompt
- Generates answer matching user's level
- Returns tailored response

User receives:
- Explanation depth matched to their background
- Terminology appropriate for their level
- Examples relevant to their experience
```

---

## Files Modified/Created

### Backend Files

**Modified:**
1. `backend/app/api/v1/auth.py`
   - Added `UpdateProfileRequest` model
   - Added `update_profile()` endpoint
   - Returns updated `UserResponse` with background fields

2. `backend/app/api/v1/chatbot.py`
   - Extract user background from `current_user`
   - Pass `software_level` and `hardware_level` to RAG functions

3. `backend/app/rag/chatbot.py`
   - Modified `build_system_prompt()` to accept background parameters
   - Modified `generate_answer()` to accept background parameters
   - Modified `get_conversation_response()` to accept background parameters
   - Personalization logic in system prompt builder

### Frontend Files

**Modified:**
1. `docusaurus/src/contexts/AuthContext.tsx`
   - Added `updateProfile()` method
   - Added to `AuthContextType` interface
   - Provided in context value

2. `docusaurus/src/components/UserMenu/index.tsx`
   - Added "Profile Settings" link in dropdown
   - Shows current background levels if set

3. `docusaurus/src/components/UserMenu/styles.module.css`
   - Added `.menuActions` styles
   - Added `.profileLink` styles

**Created:**
1. `docusaurus/src/components/UserProfile/index.tsx`
   - Main profile component with form
   - Handles save logic and state management

2. `docusaurus/src/components/UserProfile/styles.module.css`
   - Styling for profile page
   - Responsive design for mobile

3. `docusaurus/src/pages/profile.tsx`
   - Profile page route
   - Wraps UserProfile in Layout

---

## API Reference

### Update Profile

**Endpoint:** `PUT /api/v1/auth/profile`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "software_background": "intermediate",
  "hardware_background": "hobbyist"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "software_background": "intermediate",
  "hardware_background": "hobbyist",
  "created_at": "2024-01-10T12:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Profile updated successfully
- `401 Unauthorized` - Not authenticated
- `400 Bad Request` - Invalid background values

### Get Current User Profile

**Endpoint:** `GET /api/v1/auth/me`

**Authentication:** Required (Bearer token)

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "software_background": "advanced",
  "hardware_background": "professional",
  "created_at": "2024-01-10T12:00:00Z"
}
```

---

## Testing Guide

### Local Testing

**1. Test Profile Update Endpoint**
```bash
# Start local backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test the endpoint
# First, signup and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Update profile
curl -X PUT http://localhost:8000/api/v1/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"software_background":"beginner","hardware_background":"no_experience"}'

# Expected: Returns user with updated background fields
```

**2. Test Personalized Chatbot**
```bash
# Ask a question as beginner
curl -X POST http://localhost:8000/api/v1/chatbot/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question":"What is a ROS 2 node?"}'

# Expected: Response explains ROS 2 nodes in beginner-friendly language
```

**3. Test Frontend**
```bash
# Start development server
cd docusaurus
npm start

# Visit http://localhost:3000
# Login with test@example.com / password123
# Click user menu → Profile Settings
# Update background levels
# Ask chatbot a question
# Observe personalized response
```

### Production Testing

**1. Railway Backend**
```bash
# Test profile update
TOKEN=$(curl -s -X POST https://physical-ai-textbook-production-d71f.up.railway.app/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"production-test@example.com","password":"password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X PUT https://physical-ai-textbook-production-d71f.up.railway.app/api/v1/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"software_background":"advanced","hardware_background":"professional"}'
```

**2. Deployed Frontend**
```
1. Visit: https://[your-username].github.io/physical-ai-textbook/
2. Create account or login
3. Click user menu (email in top-right)
4. Select "⚙️ Profile Settings"
5. Set background levels:
   - Software: Advanced
   - Hardware: Professional
6. Click "Save Changes"
7. Open chatbot
8. Ask: "What is a ROS 2 node?"
9. Observe: Response uses advanced terminology and assumes knowledge
10. Go back to profile, change to:
    - Software: Beginner
    - Hardware: No Experience
11. Ask same question again
12. Observe: Response explains step-by-step with definitions
```

---

## Deployment

### Current Status

✅ **Code Committed:** f8318e7
✅ **Pushed to GitHub:** 001-physical-ai-textbook branch
⏳ **Railway Deployment:** Auto-deploying (3-5 minutes)
⏳ **Frontend Deployment:** Pending (see below)

### Automatic Deployment

**Railway (Backend):**
- ✅ **Automatically deploys** when you push to GitHub
- Railway watches the `001-physical-ai-textbook` branch
- Rebuilds and deploys backend within 3-5 minutes
- No manual steps required

**GitHub Pages (Frontend):**
- ⚠️ **Depends on your setup:**

#### Option A: GitHub Actions Workflow (Automatic)
If you have `.github/workflows/deploy.yml` configured:
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [001-physical-ai-textbook]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd docusaurus && npm install && npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docusaurus/build
```

**Then:** ✅ Pushing automatically triggers deployment

#### Option B: Manual Deployment (Most Common)
If you DON'T have GitHub Actions workflow:

```bash
# Build and deploy frontend manually
cd docusaurus
npm run build
npm run deploy
```

**This runs:**
1. `npm run build` - Builds static site to `build/` folder
2. `npm run deploy` - Pushes `build/` to `gh-pages` branch
3. GitHub Pages automatically serves from `gh-pages` branch

### How to Check Deployment Status

**Railway:**
```bash
# Option 1: Railway CLI
railway status
railway logs

# Option 2: Railway Dashboard
# Visit: https://railway.app/
# Check deployment status and logs
```

**GitHub Pages:**
```bash
# Option 1: Check GitHub Actions
# Visit: https://github.com/Mr-Noiam/physical-ai-textbook/actions
# See if workflow is running

# Option 2: Check Settings
# Visit: https://github.com/Mr-Noiam/physical-ai-textbook/settings/pages
# See deployment status and URL
```

### Verification

**1. Backend (Railway):**
```bash
# Test profile endpoint
curl https://physical-ai-textbook-production-d71f.up.railway.app/api/v1/auth/health

# Expected: {"status":"healthy"}
```

**2. Frontend (GitHub Pages):**
```
Visit: https://mr-noiam.github.io/physical-ai-textbook/
Expected: Site loads with latest changes
```

---

## Troubleshooting

### Profile Won't Update

**Symptoms:** Save button doesn't work, no success message

**Check:**
1. User is authenticated (token exists in localStorage)
2. Backend is running (check Railway logs)
3. Network tab in browser devtools for errors

**Fix:**
```tsx
// In browser console:
localStorage.getItem('auth_token')  // Should return JWT token
```

### Chatbot Not Personalized

**Symptoms:** Responses don't match user's background level

**Check:**
1. User has set background levels in profile
2. User is logged in (chatbot needs auth to get background)
3. Backend received background fields

**Fix:**
```bash
# Verify user profile
curl https://physical-ai-textbook-production-d71f.up.railway.app/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should show software_background and hardware_background
```

### Profile Page Not Found

**Symptoms:** `/profile` returns 404

**Check:**
1. `docusaurus/src/pages/profile.tsx` exists
2. Docusaurus rebuilt after adding file
3. Deployment included new file

**Fix:**
```bash
cd docusaurus
npm run build
npm run deploy
```

---

## Future Enhancements

### Phase 2 (Optional)

1. **Learning Path Recommendations**
   - Suggest next modules based on background
   - Skip beginner content for advanced users
   - Recommend prerequisite material for new learners

2. **Progress Tracking**
   - Track completed sections
   - Adjust difficulty as user progresses
   - Suggest review topics based on chat history

3. **Content Adaptation**
   - Hide/show advanced sections based on level
   - Adjust code examples complexity
   - Personalized project suggestions

4. **Analytics**
   - Track how personalization affects learning outcomes
   - A/B test different explanation styles
   - Measure engagement by background level

### Phase 3 (Advanced)

1. **Automatic Level Detection**
   - Analyze user questions to infer background
   - Suggest level updates based on usage
   - Dynamic adjustment during conversation

2. **Multi-Modal Personalization**
   - Video vs text preferences
   - Interactive vs reading preferences
   - Pacing preferences (fast/slow)

3. **Collaborative Features**
   - Match users with similar backgrounds
   - Peer learning groups by level
   - Mentor matching (advanced ↔ beginner)

---

## Summary

### What Was Built

✅ Complete personalization system with:
- User profile management (backend + frontend)
- Adaptive chatbot responses based on experience
- Profile settings page with easy-to-use interface
- Seamless integration with existing auth system
- Two-dimensional personalization (software + hardware)

### What It Does

The system automatically adjusts:
- **Technical depth** - Basic for beginners, advanced for experts
- **Terminology** - Defines terms for beginners, uses directly for advanced
- **Examples** - Simple for beginners, complex patterns for advanced
- **Explanations** - Step-by-step vs high-level overviews

### Benefits

**For Students:**
- Content matched to their level
- Less frustration (not too hard or too easy)
- Faster learning (right level of challenge)
- Better engagement (relevant examples)

**For Educators:**
- Scalable personalization without manual intervention
- Data on student backgrounds
- Insights into learning patterns
- Automated adaptive teaching

---

**Status:** ✅ PRODUCTION READY
**Deployment:** Railway (auto) + GitHub Pages (manual build/deploy needed)
**Testing:** Ready for end-to-end testing

---

**End of Documentation**
