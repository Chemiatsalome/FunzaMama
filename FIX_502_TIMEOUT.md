# Fix for 502 Timeout Error on Railway

## Problem

The signup endpoint was returning `502 Bad Gateway` errors due to **Worker Timeout**. The logs showed:

```
[CRITICAL] WORKER TIMEOUT (pid:201)
[ERROR] Worker (pid:201) was sent SIGKILL! Perhaps out of memory?
```

## Root Cause

1. **Gunicorn default timeout**: 30 seconds
2. **Synchronous email sending**: The signup route was waiting for email to send before returning response
3. **Slow SMTP connection**: Gmail SMTP can take several seconds, especially with connection issues
4. **No timeout on SMTP**: Email service had no timeout, allowing it to hang indefinitely

## Solutions Implemented

### 1. Increased Gunicorn Timeout ✅

**File**: `procfile`

```diff
- web: gunicorn app:app --bind 0.0.0.0:$PORT
+ web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync
```

**Changes**:
- `--timeout 120`: Increased from 30 to 120 seconds
- `--workers 2`: Added 2 workers for better concurrency
- `--worker-class sync`: Explicitly use sync workers (default but explicit)

### 2. Made Email Sending Non-Blocking ✅

**Files**: `routes/auth_routes.py`

**Before**: Email sent synchronously, blocking request until complete
```python
if email_service.send_verification_email(...):
    flash('Registration successful! ...')
```

**After**: Email sent in background thread, response returns immediately
```python
def send_email_background():
    """Send email in background thread"""
    try:
        from flask import current_app
        with current_app.app_context():
            email_service_bg = EmailService()
            email_service_bg.send_verification_email(...)
    except Exception as e:
        print(f"Error sending email in background: {e}")

email_thread = threading.Thread(target=send_email_background, daemon=True)
email_thread.start()
flash('Registration successful! ...')  # Returns immediately
```

**Routes Updated**:
- ✅ `/signup` - Signup route (main issue)
- ✅ `/resend-verification` - Resend verification email
- ✅ `/forgot-password` - Password reset email

### 3. Added SMTP Connection Timeout ✅

**File**: `utils/email_service.py`

**Before**: No timeout on SMTP connection
```python
with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
```

**After**: 10-second timeout to prevent hanging
```python
with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
```

**Benefits**:
- Prevents SMTP connection from hanging indefinitely
- Fails fast if SMTP server is unreachable
- Applied to both `send_verification_email()` and `send_password_reset_email()`

## How It Works Now

### Signup Flow (Before)
```
User submits form → Create user → Send email (wait 5-30s) → Return response
                          ↑
                    TIMEOUT HERE (502 error)
```

### Signup Flow (After)
```
User submits form → Create user → Start email thread → Return response immediately ✅
                                    ↓ (background)
                              Send email async
```

## Testing

After deploying to Railway:

1. **Test Signup**: `POST /signup` should return `200` immediately
2. **Check Logs**: Email sending should appear in background (non-blocking)
3. **Verify Email**: User should still receive verification email

## Expected Behavior

- ✅ Signup completes in < 2 seconds (no waiting for email)
- ✅ Email sends in background (doesn't block user)
- ✅ No more 502 errors
- ✅ Users still receive emails (just asynchronously)

## Monitoring

Watch Railway logs for:
- ✅ No more `WORKER TIMEOUT` errors
- ✅ `📧 Attempting to send verification email...` messages (in background)
- ✅ `✅ Verification email sent successfully` (non-blocking)

## Additional Benefits

1. **Better User Experience**: Users don't wait for email to send
2. **More Resilient**: SMTP issues don't break signup
3. **Faster Response Times**: API responds immediately
4. **Better Concurrency**: Multiple workers handle requests better

## Notes

- **Background threads are daemon threads**: They won't prevent server shutdown
- **Email errors are logged**: But don't block user registration
- **Thread safety**: Each thread gets its own Flask app context
- **Timeout is sufficient**: 120 seconds is plenty for slow SMTP, but we don't need it anymore since email is async

## Deployment

After these changes:
1. Commit changes
2. Push to Railway
3. Railway will rebuild and redeploy
4. Test signup endpoint

## Troubleshooting

If you still see timeouts:
1. Check Railway logs for `WORKER TIMEOUT`
2. Verify `procfile` changes are deployed
3. Check if SMTP timeout (10s) is too long (can reduce to 5s)
4. Monitor background thread logs for email errors
