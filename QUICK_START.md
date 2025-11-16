# 🚀 VeriMeet Quick Start Guide

## ✅ What's Been Implemented

All missing features are now complete:
- ✅ Intent Parser - Detects scheduling and email requests
- ✅ Calendar Integration - Creates events automatically
- ✅ Gmail Integration - Sends email summaries
- ✅ Full agent integration - Everything works together

---

## 🧪 Step 1: Test the Implementation

### Run the Test Script

```bash
# Make sure you're in the project directory
cd /Users/balashivanisp/PycharmProjects/VeriMeet

# Install dependencies if needed
pip install -r requirements.txt
# or
uv sync

# Run the test script
python3 test_implementation.py
```

This will test:
- ✅ Configuration loading
- ✅ Intent Parser functionality
- ✅ Agent integration
- ✅ Calendar MCP availability
- ✅ Gmail MCP availability

**Expected Output:**
```
🚀 VeriMeet Implementation Test Suite
============================================================
✅ Configuration loaded
✅ Intent Parser loaded successfully
✅ Agent created successfully
✅ Calendar MCP functions are available
✅ Gmail MCP functions are available
🎉 All tests passed! Implementation is ready.
```

---

## 🔧 Step 2: Set Up Google OAuth (Optional)

For Calendar and Gmail to work, you need Google OAuth tokens.

### Quick Method (For Testing):

1. **Use OAuth 2.0 Playground:**
   - Go to: https://developers.google.com/oauthplayground/
   - Follow instructions in `GOOGLE_OAUTH_SETUP.md`

2. **Add tokens to `.env`:**
   ```env
   GOOGLE_CALENDAR_TOKEN=your_token_here
   GOOGLE_GMAIL_TOKEN=your_token_here
   GMAIL_SENDER_EMAIL=your_email@gmail.com
   ```

**Note:** The system works without Google tokens - intents will be detected but Calendar/Gmail actions will be skipped gracefully.

---

## 🎯 Step 3: Test Intent Detection

### Test with Python REPL:

```python
from core.intent_parser import IntentParser

parser = IntentParser()

# Test scheduling intent
transcript = "Let's schedule a follow-up meeting next Friday at 2pm"
intents = parser.detect_intents(transcript)
print(intents)

# Test email intent
transcript2 = "Can you email the summary to the team?"
intents2 = parser.detect_intents(transcript2)
print(intents2)
```

### Test Full Agent Flow:

```python
from agent import VeriMeetAgent

agent = VeriMeetAgent()

# Process a transcript with intents
transcript = "We should schedule a follow-up next week. Also, please email the summary."
result = agent.process_transcript(transcript)

print(f"Intents detected: {result['intents_detected']}")
print(f"Facts detected: {result['facts_detected']}")
print(f"Detected intents: {agent.detected_intents}")
```

---

## 🚀 Step 4: Start the Server

```bash
# Start the FastAPI server
python3 server.py

# Or with uvicorn directly
uvicorn server:app --reload --port 8000
```

The server will start on `http://localhost:8000`

---

## 📝 Step 5: Test in a Real Meeting

1. **Set up ngrok** (for webhook callbacks):
   ```bash
   ngrok http 8000
   # Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   # Add it to .env as NGROK_URL
   ```

2. **Create a bot and send to meeting:**
   ```bash
   curl -X POST http://localhost:8000/api/create-bot \
     -H "Content-Type: application/json" \
     -d '{
       "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
       "bot_name": "VeriMeet Assistant"
     }'
   ```

3. **Try these phrases in the meeting:**
   - "Let's schedule a follow-up meeting next Friday at 2pm"
   - "Can you email the summary to john@example.com?"
   - "Book a call for tomorrow at 10am"

4. **Watch the bot:**
   - Detect intents automatically
   - Create calendar events (if tokens configured)
   - Send emails (if tokens configured)
   - Post confirmations to chat

---

## 📊 What Works Without Google Tokens

Even without Google OAuth tokens:
- ✅ Intent detection works perfectly
- ✅ Intents are logged and tracked
- ✅ Fact-checking works
- ✅ Summarization works
- ✅ Notion integration works
- ⚠️ Calendar events won't be created (graceful error)
- ⚠️ Emails won't be sent (graceful error)

---

## 🔍 Verify Everything

### Check Configuration:
```python
from core.config import settings

print(f"OpenAI: {'✅' if settings.openai_api_key else '❌'}")
print(f"Meetstream: {'✅' if settings.meetstream_api_key else '❌'}")
print(f"Notion: {'✅' if settings.notion_api_key else '❌'}")
print(f"Calendar: {'✅' if settings.google_calendar_token else '⚠️ Optional'}")
print(f"Gmail: {'✅' if settings.google_gmail_token else '⚠️ Optional'}")
```

### Check Intent Detection:
```python
from agent import VeriMeetAgent

agent = VeriMeetAgent()
test = "Schedule a meeting next Friday at 2pm"
result = agent.process_transcript(test)
print(f"Intents: {result['intents_detected']}")
```

---

## 📚 Documentation

- **`GOOGLE_OAUTH_SETUP.md`** - Detailed OAuth setup guide
- **`IMPLEMENTATION_SUMMARY.md`** - What was implemented
- **`PROJECT_STATUS.md`** - Full project status
- **`SETUP.md`** - Original setup guide

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Configuration errors"
- Check that `.env` file exists
- Verify all required API keys are set
- Run `python3 test_implementation.py` to check config

### "Intent detection not working"
- Verify OpenAI API key is set
- Check that you have API credits
- Review logs for errors

### "Calendar/Gmail not working"
- Check `GOOGLE_OAUTH_SETUP.md` for token setup
- Verify tokens are valid and not expired
- Check that APIs are enabled in Google Cloud Console

---

## ✅ Next Steps

1. ✅ Run `python3 test_implementation.py` to verify setup
2. ✅ Fill in API keys in `.env` file
3. ✅ (Optional) Set up Google OAuth tokens
4. ✅ Start the server: `python3 server.py`
5. ✅ Test with a real meeting!

---

*Everything is ready to go! 🎉*

