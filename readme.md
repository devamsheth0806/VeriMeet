# 🤖 VeriMeet – The Honest Meeting Copilot

> “Because great meetings deserve clarity, truth, and follow-through.”

VeriMeet is an **AI-powered meeting assistant** built with **Meetstream.ai’s real-time API**, **OpenAI reasoning**, and **productivity integrations**.  
It listens to live meetings, tracks and summarizes discussions, **fact-checks statements in real time**, automates **calendar scheduling**, and — when asked — **emails meeting minutes** to participants.

---

## 🌟 Key Features

| Capability | Description |
|-------------|-------------|
| 🗣️ **Live Understanding** | Captures live meeting audio and generates real-time topic summaries using the Meetstream API and OpenAI. |
| 🔍 **Fact Verification** | Detects factual or numerical claims and verifies them using web search or knowledge APIs. |
| 💬 **Real-time Chat Feedback** | Posts fact-check results directly to the meeting chat window for immediate visibility. |
| 📝 **Notion Integration** | Automatically saves comprehensive meeting summaries with verified facts to Notion. |

---

## 🧩 System Architecture

```mermaid
graph TD
A[Google Meet / Zoom] -->|Audio Stream| B(Meetstream API)
B -->|WebSocket| C[Local VeriMeet Server]
C --> D[OpenAI Model: Summarization + Intent Parsing]
C --> E[Fact Check Module]
C --> F[MCP Servers: Notion + Meetstream + Web Search]
D --> G[Live Transcript & Insights]
E --> H[Verified Facts]
F --> I[Notion Summaries + Chat Fact-Checks]
