# ChatbotWidget Component

AI-powered teaching assistant for the Physical AI & Humanoid Robotics textbook.

## Features

✅ **RAG-Powered Answers** - Retrieves relevant content from textbook and generates accurate answers
✅ **Text Selection** - Select any text and ask "What does this mean?"
✅ **Conversation History** - Maintains context across multiple questions
✅ **Source Citations** - Shows which sections of the textbook were used
✅ **Mobile Responsive** - Works perfectly on phones and tablets
✅ **Dark Mode Support** - Adapts to Docusaurus theme
✅ **Floating UI** - Non-intrusive button in bottom-right corner

## How It Works

### 1. User Experience

```
User clicks chat button → Chat window opens
User types question → Backend retrieves relevant chunks from Qdrant
Backend sends chunks to GPT-4 → GPT-4 generates answer
Answer displayed with source links → User can click to read more
```

### 2. Text Selection Feature

```
User selects text on page → "Ask about this" button appears
User clicks button → Chat opens with pre-filled question
Answer explains the selected text
```

### 3. Conversation Flow

```typescript
Message[] = [
  { role: 'user', content: 'What is a ROS 2 node?' },
  { role: 'assistant', content: 'A ROS 2 node is...', sources: [...] },
  { role: 'user', content: 'How do I create one?' },  // Uses history!
  { role: 'assistant', content: 'To create a ROS 2 node...', sources: [...] }
]
```

## Files

- **index.tsx** - Main React component (300+ lines)
- **styles.module.css** - CSS modules styling (350+ lines)
- **README.md** - This file

## API Integration

### Endpoint: POST /api/v1/chatbot/ask

**Request:**
```json
{
  "question": "What is a ROS 2 node?",
  "selected_text": null,
  "conversation_history": [
    { "role": "user", "content": "Previous question" },
    { "role": "assistant", "content": "Previous answer" }
  ]
}
```

**Response:**
```json
{
  "answer": "A ROS 2 node is a fundamental building block...",
  "sources": [
    {
      "file": "module-1-ros2/week2-fundamentals.md",
      "section": "Week 2: ROS 2 Fundamentals - Nodes",
      "url": "/docs/module-1-ros2/week2-fundamentals"
    }
  ],
  "timestamp": "2025-01-10T12:00:00"
}
```

## Configuration

### Environment Variables

Create `docusaurus/.env`:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000  # Development
# REACT_APP_API_URL=https://your-app.railway.app  # Production
```

### Customization

**Change colors:**
```css
/* styles.module.css */
.chatButton {
  background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

**Change position:**
```css
.chatButton {
  bottom: 24px;  /* Change this */
  right: 24px;   /* Change this */
}
```

**Change window size:**
```css
.chatWindow {
  width: 400px;   /* Change this */
  height: 600px;  /* Change this */
}
```

## Development

### Local Testing

1. **Start backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Docusaurus:**
   ```bash
   cd docusaurus
   npm start
   ```

3. **Test chatbot:**
   - Open http://localhost:3000
   - Click chat button (bottom-right)
   - Ask: "What is a ROS 2 node?"
   - Verify answer appears with sources

### Testing Text Selection

1. Select any text on a docs page
2. "Ask about this" button should appear
3. Click it
4. Chat opens with pre-filled question
5. Answer should reference the selected text

## Styling Details

### CSS Modules

Uses CSS Modules for scoped styling. Class names are automatically namespaced:

```tsx
<div className={styles.chatButton} />
// Becomes: <div class="ChatbotWidget_chatButton__abc123" />
```

### Responsive Breakpoints

- **Desktop (> 768px):** Floating window, 400px wide
- **Mobile (≤ 768px):** Full-screen overlay

### Animations

- **slideIn:** Text selection button
- **slideUp:** Chat window opening
- **fadeIn:** New messages
- **bounce:** Loading dots

### Dark Mode

Automatically adapts using Docusaurus CSS variables:

```css
[data-theme='dark'] .chatWindow {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}
```

## Accessibility

✅ **ARIA labels** on buttons
✅ **Keyboard navigation** (Tab, Enter)
✅ **Focus management** (auto-focus input)
✅ **Screen reader friendly** (semantic HTML)
✅ **Color contrast** (WCAG AA compliant)

## Performance

### Optimizations

1. **Lazy loading:** Component only loads on demand
2. **Auto-scroll:** Smooth, debounced scrolling
3. **Input debouncing:** Prevents rapid API calls
4. **CSS animations:** GPU-accelerated transforms
5. **Message batching:** Efficient re-renders

### Bundle Size

- **Component:** ~8 KB (minified)
- **Styles:** ~12 KB (minified)
- **Total:** ~20 KB (gzipped: ~6 KB)

## Troubleshooting

### "Chat button doesn't appear"

Check if Root.tsx is properly configured:
```tsx
// docusaurus/src/theme/Root.tsx
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
```

### "API calls fail (CORS error)"

Backend CORS must allow Docusaurus origin:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### "Sources don't link correctly"

Verify URL format in response:
```json
{
  "url": "/docs/module-1-ros2/week2-fundamentals"  // ✅ Correct
  "url": "module-1-ros2/week2-fundamentals.md"     // ❌ Wrong
}
```

### "Styling looks broken"

Check if CSS module is imported:
```tsx
import styles from './styles.module.css';  // ✅ Correct
import './styles.module.css';              // ❌ Wrong (no styles object)
```

## Future Enhancements

Potential improvements:

- [ ] Voice input (Whisper API)
- [ ] Chat history persistence (localStorage)
- [ ] Markdown rendering in messages
- [ ] Code block syntax highlighting
- [ ] Typing indicators (WebSocket)
- [ ] Multi-language support (i18n)
- [ ] Suggested questions
- [ ] Rating system (👍/👎)
- [ ] Export chat as PDF
- [ ] Keyboard shortcuts (Ctrl+K to open)

## Testing Checklist

Before deploying:

- [ ] Chat opens/closes smoothly
- [ ] Messages send and receive correctly
- [ ] Sources link to correct pages
- [ ] Text selection feature works
- [ ] Conversation history is maintained
- [ ] Loading states display properly
- [ ] Error messages show for API failures
- [ ] Mobile responsive (test on phone)
- [ ] Dark mode looks good
- [ ] Accessibility (test with keyboard only)

## Credits

Built with:
- **React** - UI framework
- **TypeScript** - Type safety
- **CSS Modules** - Scoped styling
- **Docusaurus** - Documentation platform
- **OpenAI GPT-4** - Answer generation
- **Qdrant** - Vector search
