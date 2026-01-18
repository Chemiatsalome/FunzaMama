# Set Together AI API Key for Chatbot

## Problem

The chatbot is showing static fallback responses because the Together AI API key is invalid or not set.

**Error in logs:**
```
Error code: 401 - Invalid API key provided
```

## Solution

### 1. Get Together AI API Key

1. **Go to**: https://api.together.ai/settings/api-keys
2. **Sign up** or **log in** to your Together AI account
3. **Create a new API key** (or use existing one)
4. **Copy the API key** (starts with letters/numbers)

### 2. Set in Railway

**Go to Railway Dashboard → Your Project → Web Service → Variables**

**Add this variable:**
- **Name**: `TOGETHER_API_KEY`
- **Value**: `your_actual_api_key_here` (paste the key you copied)

### 3. Verify

After setting the variable:
1. Railway will auto-redeploy
2. Check Railway logs - should see:
   ```
   ✅ Together AI client initialized
   ```
3. Test chatbot - should give dynamic AI responses

## What Changed

### Before:
- ❌ Hardcoded invalid API key
- ❌ Always falls back to static responses
- ❌ Generic responses don't answer specific questions

### After:
- ✅ Uses environment variable `TOGETHER_API_KEY`
- ✅ Falls back gracefully if key not set
- ✅ Improved fallback responses for specific questions:
  - Emergency contacts (Kenya)
  - Medical procedures (lymphography, etc.)
  - Urgent medical concerns
  - Casual greetings

## Improved Fallback Responses

Even when AI is unavailable, the fallback now handles:

1. **Emergency Contacts**: "what is kenya's contact for emergencies"
   - Returns Kenya emergency numbers (999, 112, Red Cross)

2. **Medical Procedures**: "what is hynphography therapy"
   - Explains lymphography and pregnancy considerations

3. **Urgent Medical**: "I am losing blood"
   - Shows urgent warning with emergency contacts

4. **Greetings**: "hey", "hi"
   - Friendly greeting with helpful information

## Testing

After setting `TOGETHER_API_KEY`:

1. **Test with API key**:
   - Should get dynamic AI responses
   - Responses should be context-aware
   - HTML formatting should work

2. **Test without API key** (if you want to test fallback):
   - Should get improved fallback responses
   - Should handle specific questions better

## Troubleshooting

### Still Getting 401 Error?

1. **Check API key**: Make sure it's correct in Railway Variables
2. **Check key format**: Should be a long string (no spaces)
3. **Redeploy**: Railway should auto-redeploy when variables change
4. **Check logs**: Look for "Together AI client initialized" message

### Still Getting Static Responses?

1. **Check if API key is set**: Look for warning in logs
2. **Verify Together AI account**: Make sure account is active
3. **Check API quota**: Together AI has usage limits

---

**Once `TOGETHER_API_KEY` is set, the chatbot will use real AI (Llama 3.1) for dynamic responses!** 🚀
