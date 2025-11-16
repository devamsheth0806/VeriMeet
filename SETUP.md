# 🚀 VeriMeet Setup Guide

This guide will help you set up VeriMeet to join Google Meet meetings, fact-check in real-time, and save summaries to Notion.

## Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`
- API keys for:
  - Meetstream.ai
  - OpenAI
  - Notion
  - Web Search API (Serper, Tavily, or Google Custom Search)
- ngrok (for local development)

## Installation

### 1. Clone and Navigate

```bash
cd verimeet
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
# Meetstream API
MEETSTREAM_API_KEY=your_meetstream_api_key_here
MEETSTREAM_API_URL=https://api.meetstream.ai

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Notion
NOTION_API_KEY=your_notion_integration_token_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Web Search (choose one)
SERPER_API_KEY=your_serper_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here
# GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
# GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here

# Server Configuration
NGROK_URL=https://your-ngrok-url.ngrok.io
SERVER_PORT=8000
SERVER_HOST=0.0.0.0
```

## Getting API Keys

### Meetstream.ai
1. Sign up at [meetstream.ai](https://meetstream.ai)
2. Get your API key from the dashboard
3. See the [Meetstream docs](http://docs.meetstream.ai/) for detailed setup

### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an API key in your account settings

### Notion
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the "Internal Integration Token"
4. Create a database in Notion and share it with your integration
5. Copy the database ID from the URL

### Web Search API (choose one)

**Option 1: Serper (Recommended)**
- Sign up at [serper.dev](https://serper.dev)
- Get your API key

**Option 2: Tavily**
- Sign up at [tavily.com](https://tavily.com)
- Get your API key

**Option 3: Google Custom Search**
- Create a Custom Search Engine at [programmablesearchengine.google.com](https://programmablesearchengine.google.com)
- Get API key from [Google Cloud Console](https://console.cloud.google.com)

## Setting Up ngrok

For local development, you need a public URL for Meetstream webhooks:

```bash
# Install ngrok
# Visit https://ngrok.com/download

# Expose local server
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and set it as `NGROK_URL` in your `.env` file.

## Running VeriMeet

### Start the Server

```bash
# Using uv
uv run python server.py

# Or using python directly
python server.py
```

The server will start on `http://localhost:8000`.

### Send Bot to a Meeting

Send a POST request to create a bot:

```bash
curl -X POST http://localhost:8000/api/create-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
    "bot_name": "VeriMeet Assistant"
  }'
```

Or use the Meetstream dashboard to send a bot.

## How It Works

1. **Bot Joins Meeting**: VeriMeet bot joins the Google Meet via Meetstream API
2. **Real-time Transcription**: Meetstream sends transcript events to your webhook
3. **Fact Detection**: VeriMeet detects factual statements in speech
4. **Fact Verification**: Each fact is verified via web search
5. **Chat Posting**: Fact-check results are posted to the meeting chat
6. **Summarization**: Rolling summaries are generated throughout the meeting
7. **Notion Save**: Final summary with verified facts is saved to Notion when meeting ends

## Testing

### Health Check
```bash
curl http://localhost:8000/
```

### Get Current Summary
```bash
curl http://localhost:8000/api/summary
```

## Troubleshooting

### Bot Not Joining Meeting
- Check that your Meetstream API key is correct
- Verify the meeting URL is a valid Google Meet link
- Ensure your ngrok URL is publicly accessible
- Check server logs for error messages

### Fact Checks Not Appearing in Chat
- Verify the bot_id is set correctly
- Check that the bot has chat permissions in the meeting
- Review Meetstream API documentation for chat message format

### Notion Integration Failing
- Verify your Notion integration token
- Check that the database is shared with your integration
- Ensure the database ID is correct (from the Notion URL)

### Web Search Not Working
- Verify at least one web search API key is set in `.env`
- Check API quotas/limits for your search provider
- Review error logs for specific API errors

## Architecture

VeriMeet uses **MCP (Model Context Protocol) servers** built with `fastmcp`:

- **Notion MCP Server** (`mcp/notion_mcp.py`): Saves summaries to Notion
- **Meetstream MCP Server** (`mcp/meetstream_mcp.py`): Manages bots and chat posting
- **Web Search MCP Server** (`mcp/web_search_mcp.py`): Verifies facts via web search

The main agent (`agent.py`) orchestrates all these integrations, and the FastAPI server (`server.py`) handles webhooks from Meetstream.

## Next Steps

- Review the [Meetstream documentation](http://docs.meetstream.ai/) for advanced features
- Check the [Loom demos](https://www.loom.com/share/66fa2d79e03349afbc8ef96757cb0d51) shared by Meetstream engineers
- Explore the codebase to understand the MCP server architecture

