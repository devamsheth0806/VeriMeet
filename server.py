"""FastAPI server entry point for VeriMeet - handles Meetstream WebSocket callbacks."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import json
import logging
from typing import Dict, Any
from agent import get_or_create_agent
from core.utils import setup_logging, log_external_call
from mcp.meetstream_mcp import create_bot

logger = setup_logging()
app = FastAPI(title="VeriMeet API", version="0.1.0")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "VeriMeet"}


@app.post("/webhook/meetstream")
async def meetstream_webhook(request: Request):
    """
    Webhook endpoint for Meetstream callbacks.
    Handles transcript events, bot status updates, etc.
    """
    try:
        body = await request.json()
        event_type = body.get("event_type")
        
        log_external_call("Meetstream", "webhook_event", {"event_type": event_type})
        logger.info(f"Received Meetstream webhook: {event_type}")
        
        # Handle different event types
        if event_type == "transcript":
            # Process transcript
            transcript = body.get("transcript", "")
            bot_id = body.get("bot_id")
            meeting_id = body.get("meeting_id")
            
            if transcript:
                agent = get_or_create_agent(bot_id=bot_id)
                result = agent.process_transcript(transcript, meeting_id=meeting_id)
                logger.info(f"Processed transcript: {result}")
        
        elif event_type == "meeting_ended":
            # Finalize meeting
            bot_id = body.get("bot_id")
            meeting_title = body.get("meeting_title")
            
            agent = get_or_create_agent(bot_id=bot_id)
            result = agent.finalize_meeting(meeting_title=meeting_title)
            logger.info(f"Finalized meeting: {result}")
        
        elif event_type == "bot_joined":
            # Bot successfully joined
            bot_id = body.get("bot_id")
            meeting_url = body.get("meeting_url")
            logger.info(f"Bot joined meeting: {bot_id} - {meeting_url}")
            
            # Initialize agent with bot_id
            agent = get_or_create_agent(bot_id=bot_id)
            agent.set_bot_id(bot_id)
        
        return JSONResponse({"status": "received"})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


@app.post("/api/create-bot")
async def create_meeting_bot(request: Request):
    """
    API endpoint to create a bot and send it to a meeting.
    
    Expected body:
    {
        "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
        "bot_name": "VeriMeet Assistant"
    }
    """
    try:
        body = await request.json()
        meeting_url = body.get("meeting_url")
        bot_name = body.get("bot_name", "VeriMeet Assistant")
        
        if not meeting_url:
            return JSONResponse(
                {"success": False, "error": "meeting_url is required"},
                status_code=400
            )
        
        # Create bot via Meetstream MCP
        result = create_bot(meeting_url, bot_name)
        
        if result.get("success"):
            bot_id = result.get("bot_id")
            # Initialize agent with bot_id
            agent = get_or_create_agent(bot_id=bot_id)
            agent.set_bot_id(bot_id)
            
            return JSONResponse({
                "success": True,
                "bot_id": bot_id,
                "status": result.get("status"),
                "meeting_url": meeting_url
            })
        else:
            return JSONResponse(
                {"success": False, "error": result.get("error")},
                status_code=500
            )
    
    except Exception as e:
        logger.error(f"Error creating bot: {e}", exc_info=True)
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.get("/api/summary")
async def get_current_summary():
    """Get the current rolling summary."""
    from agent import current_agent
    if current_agent:
        return JSONResponse({
            "success": True,
            "summary": current_agent.get_current_summary()
        })
    else:
        return JSONResponse({
            "success": False,
            "error": "No active meeting session"
        })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication (if needed).
    Currently, Meetstream uses webhooks, but this can be used for client connections.
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages if needed
            await websocket.send_json({"status": "received", "message": message})
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


if __name__ == "__main__":
    import uvicorn
    from core.config import settings
    
    logger.info(f"Starting VeriMeet server on {settings.server_host}:{settings.server_port}")
    uvicorn.run(
        "server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )

