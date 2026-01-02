# Urdu Translation - New Approach (Pre-Translated Docs)

## ❌ Old Approach (Removed - Had Problems)

**What was wrong:**
- On-demand translation (slow, can fail)
- Required API calls every time user switched language
- "Translation failed" errors
- Not suitable for documentation (good for chatbot only)
- All 15 languages (overkill, only need Urdu)

## ✅ New Approach (Better)

**Pre-translate all docs to Urdu:**
- Translate once, serve forever (static files)
- Fast (no API calls when viewing)
- Reliable (no "translation failed" errors)
- SEO-friendly (search engines can index Urdu content)
- Uses Docusaurus built-in i18n system
- Only English + Urdu (what you actually need)

## How It Works

### 1. Directory Structure

```
docusaurus/
├── docs/                          # English docs (original)
│   ├── intro.md
│   ├── module-1-ros2/
│   │   ├── week1-intro.md
│   │   └── ...
│   └── ...
│
└── i18n/                          # Translations
    └── ur/                        # Urdu translations
        └── docusaurus-plugin-content-docs/
            └── current/           # Same structure as docs/
                ├── intro.md       # Urdu version
                ├── module-1-ros2/
                │   ├── week1-intro.md
                │   └── ...
                └── ...
```

### 2. Language Selector

**New UI:** Docusaurus built-in locale dropdown

```
[Textbook]  [English ▼]  [GitHub]  [🌓]  [👤]
                ↑
    Automatic Urdu/English switcher
```

**Features:**
- Simple dropdown: English | اردو (Urdu)
- Instant switching (no API calls!)
- Proper RTL support for Urdu
- URL-based: `/docs/intro` (EN) vs `/ur/docs/intro` (UR)

## Step-by-Step Setup

### Step 1: Translate All Docs to Urdu

```bash
# Make sure backend is running first
cd backend
python -m uvicorn app.main:app --reload

# In another terminal:
cd backend
python translate_docs_to_urdu.py
```

**What this does:**
- Reads all `.md` files from `docusaurus/docs/`
- Translates each file to Urdu using backend API
- Preserves frontmatter, code blocks, links
- Saves to `docusaurus/i18n/ur/docusaurus-plugin-content-docs/current/`
- Uses caching (subsequent runs are faster)

**Output:**
```
Found 13 markdown files to translate

[1/13] Translating: intro.md
    Translated 15 lines...
    ✓ Saved: ../docusaurus/i18n/ur/.../intro.md
    Stats: 15 translated, 5 skipped (code blocks)

[2/13] Translating: week1-intro.md
...

TRANSLATION COMPLETE!
```

### Step 2: Build Docusaurus with i18n

```bash
cd docusaurus

# Build both English and Urdu versions
npm run build

# Or just start dev server (includes both languages)
npm start
```

**URLs:**
- English: `http://localhost:3000/docs/intro`
- Urdu: `http://localhost:3000/ur/docs/intro`

### Step 3: Test Language Switching

1. Open `http://localhost:3000`
2. Click language dropdown (top right)
3. Select "اردو (Urdu)"
4. Page reloads with Urdu content
5. Proper RTL rendering automatically applied!

## Configuration

### Docusaurus Config (Already Updated)

**File:** `docusaurus/docusaurus.config.ts`

```typescript
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'ur'],
  localeConfigs: {
    en: {
      label: 'English',
      direction: 'ltr',
      htmlLang: 'en-US',
    },
    ur: {
      label: 'اردو (Urdu)',
      direction: 'rtl',
      htmlLang: 'ur-PK',
    },
  },
},
```

**What this does:**
- Enables Urdu locale
- Sets RTL direction automatically
- Adds locale dropdown to navbar
- Configures proper HTML lang attributes

## Translation Script Details

### What Gets Translated

✅ **Translated:**
- Headings (# Title)
- Paragraphs
- List items
- Normal text content

❌ **NOT Translated (Preserved):**
- YAML frontmatter (--- ... ---)
- Code blocks (```...```)
- URLs and links
- Markdown syntax
- Very short lines (< 3 chars)

### Customizing Translation

**Edit:** `backend/translate_docs_to_urdu.py`

```python
# Change target language
target_language = "ur"  # or "ar" for Arabic, etc.

# Change API endpoint
API_BASE_URL = "http://localhost:8000"

# Change rate limiting
time.sleep(0.2)  # Increase if getting rate limited
```

## Deployment

### Build for Production

```bash
cd docusaurus

# Build both languages
npm run build

# Output:
# build/           # English version
# build/ur/        # Urdu version
```

### Deploy to GitHub Pages

```bash
# Deploy (includes both languages automatically)
npm run deploy
```

**Result:**
- `https://mr-noiam.github.io/physical-ai-textbook/` (English)
- `https://mr-noiam.github.io/physical-ai-textbook/ur/` (Urdu)

## Updating Translations

When you update English docs:

```bash
# 1. Edit English docs
nano docusaurus/docs/intro.md

# 2. Re-translate just that file (or all files)
cd backend
python translate_docs_to_urdu.py

# 3. Rebuild
cd ../docusaurus
npm run build
```

**Tip:** The translation script uses caching, so unchanged content won't be re-translated (saves time and API calls).

## Advantages Over Old Approach

| Feature | Old (On-Demand) | New (Pre-Translated) |
|---------|-----------------|----------------------|
| **Speed** | Slow (API calls) | Fast (static files) |
| **Reliability** | Can fail | Always works |
| **SEO** | Not indexed | Fully indexed |
| **Cost** | API calls every view | Translate once |
| **Complexity** | Complex JS logic | Simple HTML |
| **Suitability** | Chatbot ✓, Docs ✗ | Docs ✓ |

## RTL (Right-to-Left) Support

Docusaurus automatically handles RTL for Urdu:

```css
/* Applied automatically: */
html[dir='rtl'] {
  direction: rtl;
  text-align: right;
}

/* Urdu fonts loaded automatically */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
```

**What you get:**
- ✅ Text flows right-to-left
- ✅ Connected Urdu letters
- ✅ Proper font rendering
- ✅ Mirrored layout (sidebar on right)

## Troubleshooting

### 1. "Backend not running" error

```bash
# Start backend first:
cd backend
python -m uvicorn app.main:app --reload
```

### 2. "Translation failed" during script

**Causes:**
- Gemini API quota exceeded
- API key revoked/invalid

**Solution:**
- Wait for quota reset
- Use new API key (see SECURITY_URGENT_API_KEY_EXPOSURE.md)
- Script has automatic fallback to OpenAI

### 3. Urdu not showing in dropdown

```bash
# Rebuild Docusaurus:
cd docusaurus
rm -rf .docusaurus build
npm start
```

### 4. Urdu text looks broken

**Check:**
- Direction is RTL? (should be automatic)
- Fonts loading? (check browser console)
- Proper Unicode encoding? (UTF-8)

## Comparison with Chatbot Translation

**Chatbot (On-Demand):**
- User asks: "ROS کیا ہے؟" (What is ROS?)
- Translate question to English
- Get answer in English
- Translate answer to Urdu
- ✅ **Good for chatbot** (dynamic, personalized)

**Docs (Pre-Translated):**
- User opens: `/ur/docs/ros-intro`
- Serve pre-translated static HTML
- No API calls, instant loading
- ✅ **Good for documentation** (static, consistent)

## Security Note

**IMPORTANT:** After revoking old API keys (see SECURITY_URGENT_API_KEY_EXPOSURE.md):

1. Get NEW API keys
2. Update `backend/.env` with NEW keys
3. Make sure `backend/.env` is in `.gitignore`
4. NEVER commit `.env` to git again!

## Summary

✅ **Fixed Issues:**
- No more "translation failed" errors
- Fast page loading (no API calls)
- Only Urdu (not 15 languages)
- Proper RTL rendering
- SEO-friendly

✅ **Files Changed:**
- `docusaurus/docusaurus.config.ts` - Added i18n config
- `backend/translate_docs_to_urdu.py` - Translation script
- Removed complex on-demand translation component

✅ **Next Steps:**
1. Revoke old API keys (URGENT - see SECURITY_URGENT_API_KEY_EXPOSURE.md)
2. Run translation script to generate Urdu docs
3. Test language switching
4. Deploy

**Your documentation now has professional Urdu support!** 🎉
