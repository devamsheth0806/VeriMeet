# VeriMeet – Developer Context

## 🧠 Purpose
VeriMeet is a real-time AI meeting copilot that joins online meetings via the **Meetstream.ai unified API**.  
It listens to live audio, understands context, verifies facts, and performs smart actions like scheduling or emailing summaries.

This file defines the **developer context and architecture assumptions** for all source files in this workspace.  
Cursor should use this to reason about the overall system design.

---

## ⚙️ Core Goals

1. **Capture and Summarize Meetings**
   - Stream meeting audio → convert to text → generate rolling summaries.
   - Maintain a sliding context window to avoid overload.
   - Store meeting state in memory or a temporary JSON log.

2. **Fact Verification**
   - Detect numeric or factual statements.
   - Call web or knowledge APIs to verify.
   - Return validation with brief explanation.

3. **Automated Scheduling**
   - Parse intents like “schedule”, “follow-up”, or “meeting next week”.
   - Use the Google Calendar API to create events.

4. **Email Minutes of Meeting**
   - Compile summary, verified facts, and actions.
   - Send via Gmail MCP integration when user requests it.

---

## 🧩 System Overview

```plaintext
Google Meet/Zoom
   ↓
Meetstream API  →  WebSocket stream
   ↓
VeriMeet Core (FastAPI)
   ├── Transcription & summarization
   ├── Fact-checking module
   ├── Intent detection & routing
   ├── MCP connectors (Calendar, Gmail)
   └── Local state manager
🧠 Design Principles
Modular & Testable: Each capability (summarization, verification, automation) lives in its own module under /core or /mcp.

Stateless Execution: Minimal session memory; use short-term caches only.

Transparency: All external actions (calendar, email) should log to console for demo clarity.

Safety: Never expose API keys or user data; use .env for credentials.

Resilience: Gracefully handle failures in API calls with fallback messages.

📁 Suggested Folder Structure
bash
Copy code
verimeet/
│
├── server.py              # Entry point: handles WebSocket from Meetstream
├── agent.py               # AI logic: summarization, reasoning, intent routing
├── core/
│   ├── summarizer.py      # Uses OpenAI for summarization
│   ├── fact_checker.py    # Web-based fact verification
│   ├── intent_parser.py   # Detects scheduling/email intents
│   └── utils.py           # Logging, config, and helper functions
│
├── mcp/
│   ├── calendar_mcp.py    # Google Calendar integration
│   ├── gmail_mcp.py       # Gmail integration
│   └── web_mcp.py         # Web search for fact verification
│
├── data/
│   └── transcripts/       # Temporary transcripts and summaries
│
├── .env                   # API credentials
├── context.md             # Developer & Cursor context (this file)
└── README.md              # Public overview for hackathon submission
💬 Example Internal Flow
server.py

Connects to Meetstream WebSocket.

Receives real-time text/audio events.

Passes transcripts to agent.py.

agent.py

Calls summarizer.summarize() on each batch.

Calls fact_checker.verify() on factual statements.

Detects user intent: schedule / email.

Routes to corresponding MCP.

MCP modules

calendar_mcp.py: creates events via Google Calendar API.

gmail_mcp.py: formats and sends summaries.

web_mcp.py: fetches facts via external search API.

🔐 Credentials Expected
Variable	Purpose
MEETSTREAM_API_KEY	Access to Meetstream API
OPENAI_API_KEY	Summarization & reasoning
GOOGLE_CLIENT_ID / SECRET	OAuth credentials for Calendar & Gmail
NGROK_URL	Public tunnel endpoint for Meetstream agent callbacks

🧩 MVP Targets (for Hackathon)
Bot joins a meeting (confirmed via Meetstream API).

Real-time summary printed in terminal.

Simple fact check demonstration (e.g., “Revenue up 20%”).

Calendar event creation demo via command.

Email summary at end of session.

🧱 Expansion Ideas (Post-Hackathon)
Add Slack or Notion integration for sharing meeting recaps.

Integrate emotion analysis (meeting “vibe score”).

Implement persistent memory for multi-session tracking.

Visual dashboard (React/Next.js frontend).

🧩 Development Notes
Use uv run python server.py for local testing.

Expose via ngrok http 8000 for Meetstream callbacks.

Log all external calls to terminal for mentor review.

Keep everything simple and modular — focus on demonstrable interactions.