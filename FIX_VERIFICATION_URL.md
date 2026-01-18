# Fix Verification Email URL (Localhost → Production)

## Problem

Verification links in emails were using `localhost:10000` instead of the production Railway domain:
```
http://localhost:10000/verify-email/OYfSFN9PsFGxCRlzoFTtUj9lqoU2qiZk
```

This happened because email sending happens in background threads without Flask request context, so `url_for()` falls back to default `localhost`.

## Solution Implemented

### 1. Added `_get_base_url()` Helper Method ✅

**File**: `utils/email_service.py`

Created a smart method that detects the production domain by checking:
1. `SERVER_NAME` from config (if set)
2. Railway environment variables (if available)
3. Current request context (if available)
4. Railway production detection (checks `PORT` env var)
5. Hardcoded Railway domain fallback (last resort)

### 2. Updated URL Generation ✅

**Files**: `utils/email_service.py`

All email URL generation now uses `_get_base_url()` instead of hardcoded `localhost`:

- ✅ `send_verification_email()` - Uses `_get_base_url()`
- ✅ `send_password_reset_email()` - Uses `_get_base_url()`

### 3. Auto-detect HTTPS in Production ✅

**File**: `config.py`

Updated `PREFERRED_URL_SCHEME` to automatically use `https` when `PORT` is set (Railway production).

## How It Works

### Before Fix
```python
# Fallback to localhost
base_url = current_app.config.get('SERVER_NAME', 'localhost:10000')
verification_url = f"{scheme}://{base_url}/verify-email/{token}"
# Result: http://localhost:10000/verify-email/...
```

### After Fix
```python
# Smart detection
base_url = self._get_base_url()  # Detects production domain
verification_url = f"{base_url}/verify-email/{token}"
# Result: https://funzamama-app-production.up.railway.app/verify-email/...
```

## URL Detection Priority

The `_get_base_url()` method checks in this order:

1. **`SERVER_NAME` from config** (if set in Railway Variables)
2. **Railway environment variables** (`RAILWAY_STATIC_URL`, `RAILWAY_PUBLIC_DOMAIN`)
3. **Current request context** (if in a request, use `request.host`)
4. **Railway production detection** (checks `PORT` env var + `RAILWAY_ENVIRONMENT`)
5. **Hardcoded fallback**: `https://funzamama-app-production.up.railway.app`
6. **Development fallback**: `http://localhost:10000`

## Optional: Set SERVER_NAME in Railway

For more reliable URL generation, you can set `SERVER_NAME` in Railway:

### Via Railway Dashboard

1. Go to Railway Dashboard → Your Project → Variables
2. Add environment variable:
   - **Name**: `SERVER_NAME`
   - **Value**: `funzamama-app-production.up.railway.app`
3. Optionally also set:
   - **Name**: `PREFERRED_URL_SCHEME`
   - **Value**: `https`

### Via Railway CLI

```bash
railway variables set SERVER_NAME=funzamama-app-production.up.railway.app
railway variables set PREFERRED_URL_SCHEME=https
```

## Testing

After deploying:

1. **Sign up a new user**
2. **Check verification email**
3. **Verify link is production URL**:
   - ✅ `https://funzamama-app-production.up.railway.app/verify-email/...`
   - ❌ NOT `http://localhost:10000/verify-email/...`
4. **Click the link** - should work!

## Expected Results

### Verification Email Link
```
Before: http://localhost:10000/verify-email/TOKEN
After:  https://funzamama-app-production.up.railway.app/verify-email/TOKEN ✅
```

### Password Reset Link
```
Before: http://localhost:10000/reset-password/TOKEN
After:  https://funzamama-app-production.up.railway.app/reset-password/TOKEN ✅
```

## Notes

- **Automatic Detection**: Works without setting `SERVER_NAME` (uses fallback)
- **Background Threads**: Now handles URL generation outside request context
- **Production Ready**: Automatically uses HTTPS in production
- **Development Safe**: Still uses `localhost` for local development

## Troubleshooting

### Still seeing localhost in emails?

1. **Check Railway logs**: Look for `_get_base_url()` output
2. **Verify PORT env var**: Railway should set this automatically
3. **Set SERVER_NAME manually**: Use Railway Variables as described above

### Links not working?

1. **Check HTTPS**: Railway uses HTTPS, not HTTP
2. **Verify domain**: Should be `funzamama-app-production.up.railway.app`
3. **Check token**: Token should be in URL correctly

---

**The fix is automatic** - no Railway environment variables needed, but setting `SERVER_NAME` makes it more reliable.
