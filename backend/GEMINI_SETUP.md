# Setting Up Free Gemini API for Translations

## Why Gemini Instead of OpenAI?

**Cost Comparison:**
- **Gemini (FREE)**: 1,500 requests/day, 15 RPM, 1M tokens/month = $0
- **OpenAI (PAID)**: ~$0.0003 per translation = adds up quickly!

With Gemini, you save money while getting excellent translation quality.

## Setup Instructions

### Step 1: Get Your Free Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Click "Create API key in new project" (or select existing project)
5. Copy the API key (starts with "AIza...")

### Step 2: Update .env File

Open `backend/.env` and update:

```bash
# Replace YOUR_GEMINI_API_KEY_HERE with your actual API key
GEMINI_API_KEY=AIzaSy...your-actual-key-here
TRANSLATION_PROVIDER=gemini  # Keep this as "gemini" to use free tier
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Test Translation

```bash
# Start the backend
python -m uvicorn app.main:app --reload

# In another terminal, run the test
python test_gemini_translation.py
```

## Gemini API Limits (Free Tier)

- **Requests per day**: 1,500
- **Requests per minute**: 15 RPM
- **Free tokens**: 1M tokens/month
- **Model**: gemini-2.0-flash-exp (latest fast model)

This is more than enough for most translation needs!

## Switching Between Providers

To switch back to OpenAI (if needed):

```bash
# In backend/.env
TRANSLATION_PROVIDER=openai  # Uses OpenAI (paid)
```

To use Gemini again:

```bash
# In backend/.env
TRANSLATION_PROVIDER=gemini  # Uses Gemini (free)
```

## Troubleshooting

### Error: "Gemini client not initialized"

Make sure you:
1. Set `GEMINI_API_KEY` in `.env`
2. Restarted the backend server
3. Installed `google-generativeai` package

### Error: "API key not valid"

1. Double-check your API key from https://aistudio.google.com/app/apikey
2. Make sure there are no extra spaces in the `.env` file
3. Ensure the key starts with "AIza"

### Still not working?

The system will automatically fall back to OpenAI if Gemini fails. Check the server logs for detailed error messages.

## Benefits of Gemini

✅ **Completely FREE** (1M tokens/month)
✅ **Fast** (gemini-2.0-flash-exp model)
✅ **High quality** translations
✅ **Automatic caching** (reduces API calls further)
✅ **15 supported languages** (Urdu, Arabic, Hindi, etc.)

Enjoy free translations! 🎉
