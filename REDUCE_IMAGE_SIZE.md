# 🐳 Reducing Docker Image Size from 8.8GB to <4GB

## The Problem
Your Docker image is **8.8 GB**, which exceeds Railway's **4.0 GB limit** for the free tier.

## Root Cause
Heavy ML libraries in `requirements.txt`:
- `torch` (PyTorch) - ~2-3 GB
- `transformers` - ~1-2 GB  
- `sentence-transformers` - ~500 MB
- `faiss-cpu` - ~200 MB
- `accelerate`, `bitsandbytes` - ~500 MB
- **Total ML libraries: ~4-6 GB**

## ✅ The Solution (Applied)

### 1. Created `requirements-production.txt`
- **Removed heavy ML libraries** (torch, transformers, sentence-transformers, faiss-cpu)
- **Kept essential packages** (Flask, Together AI, database drivers, etc.)
- **Expected size reduction: ~5-6 GB** → Image should be **<2 GB**

### 2. Made FAISS Optional in `chatbot.py`
- FAISS/sentence-transformers are now **optional imports**
- If not available, chatbot uses **Together AI only** (which is your primary provider anyway)
- Chatbot will still work perfectly without FAISS grounding

### 3. Updated `nixpacks.toml`
- Now uses `requirements-production.txt` instead of `requirements.txt`
- Added `--no-cache-dir` to reduce pip cache size

## 📊 Expected Results

**Before:**
- Image size: **8.8 GB** ❌
- Status: **Exceeds 4.0 GB limit**

**After:**
- Image size: **~1.5-2.5 GB** ✅
- Status: **Under 4.0 GB limit**

## 🎯 What Still Works

✅ **Question Generation** - Uses Together AI (primary provider)  
✅ **Chatbot** - Uses Together AI (FAISS grounding is optional)  
✅ **Database** - PostgreSQL connection  
✅ **Email** - Gmail SMTP  
✅ **All Flask routes** - Fully functional  

## ⚠️ What's Disabled (Optional Features)

❌ **FAISS Grounding** - Chatbot won't use local embeddings (but Together AI works fine)  
❌ **Local Hugging Face Models** - Fallback disabled (Together AI is primary anyway)  

## 🚀 Next Steps

1. **Railway will automatically redeploy** with the new minimal requirements
2. **Image size should be <4 GB** now
3. **Deployment should succeed** on free tier

## 💡 If You Need ML Libraries Later

If you need FAISS/transformers later, you can:
1. **Upgrade to Railway Hobby ($5/month)** - Allows larger images
2. **Or add them back selectively** - Only install what's needed

## ✅ No Upgrade Needed!

With these changes, your app should deploy successfully on Railway's **free tier** without upgrading! 🎉
