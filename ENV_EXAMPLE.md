# 📝 How to Add Google Tokens to .env File

## Location in .env File

The Google Calendar and Gmail settings are at the **bottom** of your `.env` file (around lines 50-60).

## Current State (Commented Out)

Currently, these lines are commented out with `#`:

```env
# GOOGLE_CALENDAR_TOKEN=your_google_calendar_oauth_token_here
# GOOGLE_CALENDAR_ID=primary
# GOOGLE_GMAIL_TOKEN=your_google_gmail_oauth_token_here
# GMAIL_SENDER_EMAIL=your_email@gmail.com
```

## What You Need to Do

### Step 1: Remove the `#` symbols

Remove the `#` at the beginning of each line to uncomment them.

### Step 2: Replace with your actual values

Replace the placeholder text with your real tokens and email.

## Example (After Editing)

Here's what it should look like after you add your values:

```env
# ============================================================================
# Google Calendar Integration (Optional)
# Get OAuth token from: https://console.cloud.google.com
# Enable Google Calendar API and create OAuth credentials
# ============================================================================
GOOGLE_CALENDAR_TOKEN=ya29.a0AfH6SMBx...your_actual_token_here
GOOGLE_CALENDAR_ID=primary

# ============================================================================
# Gmail Integration (Optional)
# Get OAuth token from: https://console.cloud.google.com
# Enable Gmail API and create OAuth credentials
# ============================================================================
GOOGLE_GMAIL_TOKEN=ya29.a0AfH6SMBx...your_actual_token_here
GMAIL_SENDER_EMAIL=yourname@gmail.com
```

## Quick Edit Instructions

1. Open `.env` file in your editor
2. Scroll to the bottom (last 15-20 lines)
3. Find the Google Calendar section
4. Remove `#` from these lines:
   - `# GOOGLE_CALENDAR_TOKEN=...` → `GOOGLE_CALENDAR_TOKEN=your_token`
   - `# GOOGLE_CALENDAR_ID=...` → `GOOGLE_CALENDAR_ID=primary` (or your calendar ID)
5. Find the Gmail section
6. Remove `#` from these lines:
   - `# GOOGLE_GMAIL_TOKEN=...` → `GOOGLE_GMAIL_TOKEN=your_token`
   - `# GMAIL_SENDER_EMAIL=...` → `GMAIL_SENDER_EMAIL=your_email@gmail.com`

## Values to Fill In

| Variable | What to Put | Example |
|----------|-------------|---------|
| `GOOGLE_CALENDAR_TOKEN` | Your Google Calendar OAuth access token | `ya29.a0AfH6SMBx...` |
| `GOOGLE_CALENDAR_ID` | Calendar ID (usually "primary") | `primary` |
| `GOOGLE_GMAIL_TOKEN` | Your Gmail OAuth access token | `ya29.a0AfH6SMBx...` |
| `GMAIL_SENDER_EMAIL` | Your Gmail address | `yourname@gmail.com` |

## Notes

- **GOOGLE_CALENDAR_ID**: Usually just `primary` (your main calendar)
- **Tokens**: Get these from OAuth Playground or Google Cloud Console (see `GOOGLE_OAUTH_SETUP.md`)
- **No quotes needed**: Don't put quotes around the values
- **No spaces**: Make sure there are no spaces around the `=` sign

## Example of Correct Format

✅ **Correct:**
```env
GOOGLE_CALENDAR_TOKEN=ya29.a0AfH6SMBx123456789
GOOGLE_CALENDAR_ID=primary
GOOGLE_GMAIL_TOKEN=ya29.a0AfH6SMBx987654321
GMAIL_SENDER_EMAIL=john.doe@gmail.com
```

❌ **Wrong:**
```env
GOOGLE_CALENDAR_TOKEN = "ya29.a0AfH6SMBx..."  # Spaces and quotes
GOOGLE_CALENDAR_ID='primary'  # Quotes not needed
```

