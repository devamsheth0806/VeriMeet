# 🔐 Google OAuth Setup Guide

This guide will help you set up Google OAuth tokens for Calendar and Gmail integration.

---

## 📋 Prerequisites

1. Google account
2. Access to [Google Cloud Console](https://console.cloud.google.com)
3. Basic understanding of OAuth 2.0

---

## 🚀 Quick Setup (For Testing)

### Option 1: OAuth 2.0 Playground (Easiest for Testing)

1. **Go to OAuth 2.0 Playground**
   - Visit: https://developers.google.com/oauthplayground/

2. **Configure OAuth Playground**
   - Click the gear icon (⚙️) in top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret (from step below)

3. **Get Your Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable APIs:
     - Google Calendar API
     - Gmail API
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: `https://developers.google.com/oauthplayground`
   - Copy Client ID and Client Secret

4. **Get Access Tokens**
   - In OAuth Playground, select scopes:
     - `https://www.googleapis.com/auth/calendar`
     - `https://www.googleapis.com/auth/gmail.send`
   - Click "Authorize APIs"
   - Sign in and grant permissions
   - Click "Exchange authorization code for tokens"
   - Copy the "Access token"

5. **Add to .env**
   ```env
   GOOGLE_CALENDAR_TOKEN=your_access_token_here
   GOOGLE_GMAIL_TOKEN=your_access_token_here
   GMAIL_SENDER_EMAIL=your_email@gmail.com
   ```

**Note:** These tokens expire after 1 hour. For production, use refresh tokens (see below).

---

## 🔧 Production Setup (With Refresh Tokens)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Create Project"
3. Name it (e.g., "VeriMeet")
4. Click "Create"

### Step 2: Enable APIs

1. Go to "APIs & Services" → "Library"
2. Search and enable:
   - **Google Calendar API**
   - **Gmail API**
3. Click "Enable" for each

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Configure consent screen (if first time):
   - User Type: External
   - App name: VeriMeet
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Add `calendar` and `gmail.send`
   - Test users: Add your email
   - Click "Save and Continue"
4. Create OAuth Client:
   - Application type: "Web application"
   - Name: "VeriMeet Web Client"
   - Authorized redirect URIs:
     - `http://localhost:8000/oauth/callback` (for local dev)
     - `https://your-domain.com/oauth/callback` (for production)
   - Click "Create"
5. **Save these values:**
   - Client ID
   - Client Secret

### Step 4: Get Refresh Token (Python Script)

Create a file `get_google_tokens.py`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_tokens():
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    print(f"Access Token: {creds.token}")
    print(f"Refresh Token: {creds.refresh_token}")
    return creds

if __name__ == '__main__':
    get_tokens()
```

**Run it:**
1. Download `credentials.json` from Google Cloud Console (OAuth 2.0 Client)
2. Install: `pip install google-auth google-auth-oauthlib google-auth-httplib2`
3. Run: `python get_google_tokens.py`
4. Browser opens → Sign in → Grant permissions
5. Copy the tokens to `.env`

---

## 🔄 Using Refresh Tokens (Recommended)

For production, implement token refresh in the MCP modules:

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def refresh_token(refresh_token_str):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token_str,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret
    )
    creds.refresh(Request())
    return creds.token
```

---

## 📝 Environment Variables

Add to your `.env`:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# Access Tokens (or use refresh tokens)
GOOGLE_CALENDAR_TOKEN=your_calendar_token_here
GOOGLE_GMAIL_TOKEN=your_gmail_token_here
GOOGLE_CALENDAR_ID=primary
GMAIL_SENDER_EMAIL=your_email@gmail.com

# Optional: Refresh Tokens (for automatic renewal)
GOOGLE_CALENDAR_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_GMAIL_REFRESH_TOKEN=your_refresh_token_here
```

---

## 🧪 Testing Your Setup

1. **Test Calendar:**
   ```python
   from mcp.calendar_mcp import create_calendar_event
   result = create_calendar_event(
       title="Test Event",
       date="2024-01-20",
       time="14:00"
   )
   print(result)
   ```

2. **Test Gmail:**
   ```python
   from mcp.gmail_mcp import send_simple_email
   result = send_simple_email(
       recipients=["your-email@gmail.com"],
       subject="Test Email",
       body="This is a test"
   )
   print(result)
   ```

3. **Run the test script:**
   ```bash
   python test_implementation.py
   ```

---

## ⚠️ Important Notes

1. **Token Expiration**: Access tokens expire after 1 hour. Use refresh tokens for long-term use.

2. **Security**: Never commit tokens to version control. They're already in `.gitignore`.

3. **Scopes**: The current implementation uses:
   - `calendar` - Full calendar access
   - `gmail.send` - Send emails only

4. **Rate Limits**: Google APIs have rate limits. Be mindful of:
   - Calendar API: 1,000,000 queries/day
   - Gmail API: 1,000,000 queries/day

5. **Service Accounts**: For server-to-server communication, consider using service accounts instead of OAuth.

---

## 🆘 Troubleshooting

### "Invalid Credentials"
- Check that tokens are correct
- Verify tokens haven't expired
- Re-generate tokens if needed

### "Insufficient Permissions"
- Check that required APIs are enabled
- Verify OAuth scopes include calendar and gmail.send
- Re-authorize with correct scopes

### "Token Expired"
- Access tokens expire after 1 hour
- Use refresh tokens for automatic renewal
- Or re-generate access tokens

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Calendar API Guide](https://developers.google.com/calendar/api/guides/overview)
- [Gmail API Guide](https://developers.google.com/gmail/api/guides)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

---

*For quick testing, use OAuth Playground. For production, implement refresh token flow.*

