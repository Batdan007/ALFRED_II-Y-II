"""
Alfred API Server - OpenAI-Compatible REST API
Allows M5Stack devices and other clients to communicate with Alfred

Compatible with M5Stack ModuleLLM-OpenAI-Plugin:
https://github.com/m5stack/ModuleLLM-OpenAI-Plugin

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
import uvicorn
import json

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController
from ai.multimodel import MultiModelOrchestrator

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Alfred components
brain = AlfredBrain()
privacy = PrivacyController(auto_confirm=True)
ai = MultiModelOrchestrator(privacy_controller=privacy)

# FastAPI app
app = FastAPI(
    title="Alfred API Server",
    description="OpenAI-compatible API for M5Stack and other devices",
    version="1.0.0"
)

# Enable CORS for M5Stack devices and mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for IoT devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for PWA web interface
STATIC_DIR = Path(__file__).parent / "web" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================================
# OpenAI-Compatible Models
# ============================================================================

class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: str = Field(default="alfred", description="Model name")
    messages: List[Message] = Field(..., description="Conversation messages")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=500, ge=1)
    stream: Optional[bool] = Field(default=False)


class CompletionRequest(BaseModel):
    """OpenAI-compatible text completion request"""
    model: str = Field(default="alfred", description="Model name")
    prompt: str = Field(..., description="Text prompt")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=500, ge=1)
    stream: Optional[bool] = Field(default=False)


class TTSRequest(BaseModel):
    """Text-to-speech request"""
    model: str = Field(default="alfred-voice", description="TTS model")
    input: str = Field(..., description="Text to speak")
    voice: Optional[str] = Field(default="alfred", description="Voice preset")


# ============================================================================
# OpenAI-Compatible Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Serve PWA web interface"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    # Fallback to API info if no web UI
    return HTMLResponse(content="""
        <html><body style="background:#1a1a2e;color:white;font-family:sans-serif;text-align:center;padding:50px;">
        <h1>ALFRED API Server</h1>
        <p>Web UI not found. API is running on /v1/chat/completions</p>
        </body></html>
    """)


@app.get("/api")
async def api_info():
    """API info endpoint"""
    return {
        "name": "Alfred API Server",
        "version": "1.0.0",
        "description": "OpenAI-compatible API for Alfred AI Assistant",
        "compatible_with": "M5Stack ModuleLLM-OpenAI-Plugin",
        "endpoints": [
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/models",
            "/v1/audio/speech",
            "/health"
        ],
        "brain_stats": brain.get_stats()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_available = ai.ollama.is_available() if ai.ollama else False
    claude_available = ai.claude.is_available() if ai.claude else False

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "brain": "operational",
            "ollama": "available" if ollama_available else "unavailable",
            "claude": "available" if claude_available else "unavailable"
        },
        "memory": brain.get_stats()
    }


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    models = []

    # Alfred's main model
    models.append({
        "id": "alfred",
        "object": "model",
        "created": 1699000000,
        "owned_by": "alfred-ubx",
        "permission": [],
        "root": "alfred",
        "parent": None
    })

    # Ollama models if available
    if ai.ollama and ai.ollama.is_available():
        models.append({
            "id": f"ollama/{ai.ollama.model}",
            "object": "model",
            "created": 1699000000,
            "owned_by": "ollama",
            "permission": [],
            "root": ai.ollama.model,
            "parent": None
        })

    # Claude if available
    if ai.claude and ai.claude.is_available():
        models.append({
            "id": "claude/sonnet-4.5",
            "object": "model",
            "created": 1699000000,
            "owned_by": "anthropic",
            "permission": [],
            "root": "claude",
            "parent": None
        })

    return {
        "object": "list",
        "data": models
    }


@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint
    Compatible with M5Stack ModuleLLM plugin
    """
    try:
        logger.info(f"Chat request from M5Stack: {len(request.messages)} messages")

        # Extract user message (last message in conversation)
        user_message = request.messages[-1].content if request.messages else ""

        # Build context from previous messages
        context = []
        for msg in request.messages[:-1]:  # All except last
            context.append({
                "role": msg.role,
                "content": msg.content
            })

        # Get conversation context from brain
        brain_context = brain.get_conversation_context(limit=3)
        if brain_context:
            context = brain_context + context

        # Generate response using Alfred's AI
        logger.info(f"Generating response for: {user_message[:50]}...")
        response_text = ai.generate(
            prompt=user_message,
            context=context,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        if not response_text:
            raise HTTPException(status_code=500, detail="AI generation failed")

        # Store in Alfred's brain
        brain.store_conversation(
            user_input=user_message,
            alfred_response=response_text,
            context={"source": "m5stack", "model": request.model},
            importance=6,
            success=True
        )

        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split())
            }
        }

    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/completions")
async def text_completion(request: CompletionRequest):
    """
    OpenAI-compatible text completions endpoint
    """
    try:
        logger.info(f"Text completion request: {request.prompt[:50]}...")

        # Get context from brain
        context = brain.get_conversation_context(limit=3)

        # Generate response
        response_text = ai.generate(
            prompt=request.prompt,
            context=context,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        if not response_text:
            raise HTTPException(status_code=500, detail="AI generation failed")

        # Store in brain
        brain.store_conversation(
            user_input=request.prompt,
            alfred_response=response_text,
            context={"source": "api", "model": request.model},
            importance=5,
            success=True
        )

        return {
            "id": f"cmpl-{datetime.now().timestamp()}",
            "object": "text_completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "text": response_text,
                    "index": 0,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(request.prompt.split()) + len(response_text.split())
            }
        }

    except Exception as e:
        logger.error(f"Text completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/audio/speech")
async def text_to_speech(request: TTSRequest):
    """
    Text-to-speech endpoint (Alfred voice)
    Returns audio data for M5Stack to play
    """
    try:
        logger.info(f"TTS request: {request.input[:50]}...")

        # Import voice system
        from capabilities.voice.alfred_voice import AlfredVoice, VoicePersonality

        voice = AlfredVoice(privacy_mode=True)

        # Speak the text (returns audio data if configured)
        # For now, just confirm TTS was triggered
        voice.speak(request.input, VoicePersonality.INFORMATION)

        # Return success (actual audio streaming would require additional setup)
        return {
            "status": "success",
            "message": "TTS triggered on server",
            "text": request.input,
            "voice": request.voice
        }

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Alfred-Specific Endpoints
# ============================================================================

@app.get("/alfred/memory/stats")
async def alfred_memory_stats():
    """Get Alfred's memory statistics"""
    return brain.get_stats()


@app.get("/alfred/memory/conversations")
async def alfred_conversations(limit: int = 10):
    """Get recent conversations"""
    return brain.get_conversation_context(limit=limit)


@app.get("/alfred/memory/knowledge/{category}")
async def alfred_knowledge(category: str):
    """Get knowledge by category"""
    return brain.recall_knowledge(category=category)


@app.post("/alfred/memory/store")
async def alfred_store_knowledge(category: str, key: str, value: str, importance: int = 5):
    """Store knowledge in Alfred's brain"""
    brain.store_knowledge(category, key, value, importance=importance)
    return {"status": "success", "category": category, "key": key}


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run Alfred API server"""
    logger.info("Starting Alfred API Server...")
    logger.info("Compatible with M5Stack ModuleLLM-OpenAI-Plugin")
    logger.info("Server will be available at: http://localhost:5000")
    logger.info("")
    logger.info("OpenAI-Compatible Endpoints:")
    logger.info("  POST /v1/chat/completions")
    logger.info("  POST /v1/completions")
    logger.info("  POST /v1/audio/speech")
    logger.info("  GET  /v1/models")
    logger.info("")
    logger.info("Alfred-Specific Endpoints:")
    logger.info("  GET  /alfred/memory/stats")
    logger.info("  GET  /alfred/memory/conversations")
    logger.info("  GET  /alfred/memory/knowledge/{category}")
    logger.info("  POST /alfred/memory/store")
    logger.info("")

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Accept connections from M5Stack devices on network
        port=5000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
