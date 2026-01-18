# Set Together AI API Key in Railway

## Quick Setup

### Step 1: Go to Railway Dashboard
1. Open: https://railway.app
2. Select your **FunzaMama** project
3. Click on your **Web Service**

### Step 2: Add Environment Variable
1. Click on the **Variables** tab
2. Click **+ New Variable**
3. Enter:
   - **Variable Name**: `TOGETHER_API_KEY`
   - **Value**: `9075598f252c645841df758d606857135f2adf2111b3e73df7850d304a4380e1`
4. Click **Add**

### Step 3: Verify
Railway will automatically redeploy. After deployment:
1. Check Railway logs - you should see:
   ```
   ✅ Together AI client initialized
   ```
2. Test the chatbot - should give dynamic AI responses instead of static fallback

## Security Note
✅ **Good**: The key is set as an environment variable in Railway (secure)
❌ **Bad**: Never commit API keys to git or share them publicly

## Testing
After setting the variable, test the chatbot:
- Ask: "What is folic acid?"
- Should get a dynamic AI response (not static fallback)
- Should be context-aware and conversational

---

**Your API key is ready to use!** 🚀
