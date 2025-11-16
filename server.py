"""FastAPI server entry point for VeriMeet - handles Meetstream WebSocket callbacks."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import logging
from typing import Dict, Any, List
from agent import get_or_create_agent
from core.utils import setup_logging, log_external_call
from mcp.meetstream_mcp import create_bot

logger = setup_logging()
app = FastAPI(title="VeriMeet API", version="0.1.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

async def broadcast_message(message: Dict[str, Any]):
    """Broadcast a message to all connected WebSocket clients."""
    if active_connections:
        message_json = json.dumps(message)
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            if conn in active_connections:
                active_connections.remove(conn)


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
                
                # Broadcast to WebSocket clients
                await broadcast_message({
                    "type": "transcript",
                    "data": {"text": transcript, "bot_id": bot_id}
                })
                
                # Broadcast facts if any
                if result.get("facts_verified", 0) > 0:
                    for fact in agent.verified_facts[-result.get("facts_verified", 0):]:
                        await broadcast_message({
                            "type": "fact",
                            "data": fact
                        })
                
                # Broadcast intents if any
                if result.get("intents_detected", 0) > 0:
                    for intent in agent.detected_intents[-result.get("intents_detected", 0):]:
                        await broadcast_message({
                            "type": "intent",
                            "data": intent
                        })
                
                # Broadcast summary update
                if agent.current_summary:
                    await broadcast_message({
                        "type": "summary",
                        "data": {"summary": agent.current_summary}
                    })
        
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
    WebSocket endpoint for real-time communication with frontend.
    Broadcasts meeting events (transcripts, facts, intents, summaries) to connected clients.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connection established. Total connections: {len(active_connections)}")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "status",
            "data": {"status": "connected", "message": "Connected to VeriMeet"}
        })
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle incoming messages if needed
                logger.debug(f"Received WebSocket message: {message}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Remaining connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if websocket in active_connections:
            active_connections.remove(websocket)


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

