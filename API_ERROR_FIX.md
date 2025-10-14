# API Error Diagnosis & Fix Guide

## Error You're Seeing

```
[TUMOR MODEL] LLM call failed for Nanobot X with model llama-3.1-8b-instant: 
Error code: 400 - {'detail': "The requested model does not support Chat Completions API..."}
```

## Root Cause

The model `llama-3.1-8b-instant` is a **GROQ model**, but it's being sent to the **IO.NET API** endpoint instead. This happens because:

### 1. GROQ Client Not Initialized

The GROQ client initialization likely failed due to one of these reasons:

**Option A: GROQ API Key Not Set**
```bash
# Check your .env file
cat .env | grep GROQ_API_KEY
```

If it's missing or commented out:
```bash
# Add to .env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

**Option B: GROQ Library Not Installed**
```bash
# Check if groq is installed
pip list | grep groq

# If missing, install it
pip install groq
```

### 2. How to Get GROQ API Key

1. Visit: https://console.groq.com/
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)
6. Add to your `.env` file:
   ```bash
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

## Verification Steps

### Step 1: Check Backend Logs on Startup

When you start the backend, you should see:
```
✅ GROQ client configured
✅ GAIA client configured
```

If you see:
```
⚠️ groq not installed (pip install groq)
```
Then run: `pip install groq`

If you don't see the GROQ line at all, the API key is missing from `.env`.

### Step 2: Test API Keys Endpoint

```bash
curl http://localhost:8000/api-keys/status
```

Should return:
```json
{
  "success": true,
  "api_keys": {
    "io_secret_key": true,
    "openai_api_key": false,
    "gemini_api_key": false,
    "mistral_api_key": false,
    "groq_api_key": true,     // ← Should be true
    "gaia_api_key": true      // ← Should be true
  },
  "any_llm_available": true
}
```

### Step 3: Test GROQ Model Directly

```python
# test_groq.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY: {'SET' if api_key else 'NOT SET'}")

if api_key:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print(f"Response: {response.choices[0].message.content}")
else:
    print("ERROR: GROQ_API_KEY not found in .env")
```

Run:
```bash
cd backend
python test_groq.py
```

## Fix Summary

### Quick Fix (Choose ONE):

**Option 1: Use GROQ (Recommended - Ultra Fast)**
```bash
# 1. Install GROQ
pip install groq

# 2. Get API key from https://console.groq.com/

# 3. Add to .env
echo "GROQ_API_KEY=gsk_your_key_here" >> .env

# 4. Restart backend
python -m uvicorn main:app --reload --port 8000
```

**Option 2: Use Different Model**

Change the model in the frontend to one that's already working:
- `meta-llama/Llama-3.3-70B-Instruct` (requires IO_SECRET_KEY)
- `mistralai/Mistral-Large-Instruct-2411` (requires MISTRAL_API_KEY)
- `deepseek-ai/DeepSeek-R1-0528` (requires IO_SECRET_KEY)

## Model Routing Logic (How It Works Now)

The code now checks models in this order:

1. **GPT models** (`gpt-4o`, etc.) → OpenAI client
2. **Gemini models** (`gemini-1.5-flash`, etc.) → Google client
3. **Mistral models** (`mistral-large`, etc.) → Mistral client
4. **GROQ models** (`llama-3.1-8b-instant`, `llama-guard-4-12b`) → GROQ client ✨ NEW
5. **GAIA models** (`gemma-3`, `Yi1.5`, `Qwen3`, `MiniCPM-V-2_6`) → GAIA client ✨ NEW
6. **DeepSeek models** (`deepseek-r1-0528`) → IO.NET client
7. **Magistral models** (`Magistral-small-2506`) → IO.NET client
8. **Everything else** → IO.NET client (fallback)

### Important: Client Availability Check

If a model requires a client that isn't available, it now:
1. Logs a clear error message: `"GROQ model requested but GROQ_API_KEY not configured"`
2. Falls back to default behavior (`explore` for nanobots, `random` for ants)
3. Does NOT crash the simulation

## Supported Models by Provider

### GROQ (Fastest - Sub-second inference)
- `llama-3.1-8b-instant` ⚡
- `llama-guard-4-12b` 🛡️

### GAIA (Diverse open models)
- `gemma-3` 💎
- `Yi1.5` 🌸
- `Qwen3` 🌟
- `MiniCPM-V-2_6` 🔬

### IO.NET (Wide selection)
- `meta-llama/Llama-3.3-70B-Instruct`
- `deepseek-ai/DeepSeek-R1-0528`
- `mistralai/Magistral-Small-2506`
- And 12+ more models

## Your Current Setup (Based on Error)

✅ **IO_SECRET_KEY**: SET (working)  
❌ **GROQ_API_KEY**: NOT SET (causing error)  
❓ **GAIA_API_KEY**: Unknown

## Recommended Action

**For fastest results, install GROQ:**

```bash
# Terminal 1 - Install GROQ
cd backend
pip install groq

# Terminal 2 - Get API key
# Visit https://console.groq.com/ and create a free API key

# Terminal 1 - Add to .env
echo "GROQ_API_KEY=gsk_your_actual_key_here" >> ../.env

# Restart backend
python -m uvicorn main:app --reload --port 8000
```

You should then see:
```
✅ GROQ client configured
```

And the `llama-3.1-8b-instant` model will work with sub-second response times!

## Alternative: Use IO.NET Models

If you don't want to set up GROQ, just switch to an IO.NET model in the UI:
- `meta-llama/Llama-3.3-70B-Instruct` (works with your current IO_SECRET_KEY)
- `deepseek-ai/DeepSeek-R1-0528` (works with your current IO_SECRET_KEY)

---

**Last Updated:** October 14, 2025  
**Status:** Diagnosis Complete ✅

