"""
Alfred Sync Server - Brain Synchronization for M5Stack Devices
OpenAI-compatible API + Brain sync for "Alfred Everywhere"

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX Patent-Pending System
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController
from ai.multimodel import MultiModelOrchestrator

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Alfred components
brain = AlfredBrain()
privacy = PrivacyController(auto_confirm=True)
ai = MultiModelOrchestrator(privacy_controller=privacy)

# Device registry (in-memory for now, will move to brain DB)
device_registry: Dict[str, Dict[str, Any]] = {}

# FastAPI app
app = FastAPI(
    title="Alfred Sync Server",
    description="Brain synchronization and OpenAI-compatible API for M5Stack devices",
    version="1.0.0"
)

# Enable CORS for M5Stack WiFi access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for IoT devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable Gzip compression for brain sync (reduce data usage)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ============================================================================
# Pydantic Models
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


class DeviceRegistration(BaseModel):
    """Device registration"""
    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(default="m5stack-mini", description="Device type")
    firmware_version: Optional[str] = Field(None, description="Firmware version")
    capabilities: Optional[List[str]] = Field(default_factory=list, description="Device capabilities")


class ConversationUpload(BaseModel):
    """Offline conversation upload"""
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    user_input: str = Field(..., description="User input")
    alfred_response: str = Field(..., description="Alfred's response")
    source: str = Field(default="offline", description="Source: offline, hotspot, wifi")
    importance: int = Field(default=5, ge=1, le=10)
    topics: Optional[List[str]] = Field(default_factory=list)


class KnowledgeUpload(BaseModel):
    """Knowledge update upload"""
    category: str = Field(..., description="Knowledge category")
    key: str = Field(..., description="Knowledge key")
    value: str = Field(..., description="Knowledge value")
    importance: int = Field(default=5, ge=1, le=10)
    learned_at: str = Field(..., description="ISO 8601 timestamp when learned")


class BrainSyncRequest(BaseModel):
    """Brain synchronization request"""
    device_id: str = Field(..., description="Device identifier")
    last_sync: Optional[str] = Field(None, description="Last sync timestamp (ISO 8601)")
    conversations: List[ConversationUpload] = Field(default_factory=list)
    knowledge_updates: List[KnowledgeUpload] = Field(default_factory=list)


# ============================================================================
# Root & Health Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    stats = brain.get_stats()
    ollama_available = ai.ollama.is_available() if ai.ollama else False
    claude_available = ai.claude.is_available() if ai.claude else False

    return {
        "name": "Alfred Sync Server",
        "version": "1.0.0",
        "description": "Brain synchronization and OpenAI-compatible API for M5Stack devices",
        "tagline": "Alfred Everywhere - Your AI butler, anywhere you go",
        "endpoints": {
            "openai_compatible": [
                "/v1/chat/completions",
                "/v1/completions",
                "/v1/models"
            ],
            "brain_sync": [
                "/sync/register",
                "/sync/upload",
                "/sync/download",
                "/sync/status"
            ],
            "health": "/health"
        },
        "brain_stats": stats,
        "ai_backends": {
            "ollama": ollama_available,
            "claude": claude_available
        },
        "registered_devices": len(device_registry)
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
            "claude": "available" if claude_available else "unavailable",
            "sync_server": "operational"
        },
        "memory": brain.get_stats(),
        "devices": {
            "registered": len(device_registry),
            "active": len([d for d in device_registry.values() if d.get("active", False)])
        }
    }


# ============================================================================
# OpenAI-Compatible Endpoints
# ============================================================================

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
    For M5Stack online mode (hotspot/WiFi)
    """
    try:
        logger.info(f"Chat request: {len(request.messages)} messages")

        # Extract user message (last message)
        user_message = request.messages[-1].content if request.messages else ""

        # Build context from previous messages
        context = []
        for msg in request.messages[:-1]:
            context.append({
                "role": msg.role,
                "content": msg.content
            })

        # Get conversation context from brain (last 3 conversations)
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
            context={"source": "m5stack_online", "model": request.model},
            importance=6,
            success=True
        )

        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{int(datetime.now().timestamp())}",
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
    """OpenAI-compatible text completions endpoint"""
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
            "id": f"cmpl-{int(datetime.now().timestamp())}",
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


# ============================================================================
# Brain Sync Endpoints (M5Stack Offline → Online)
# ============================================================================

@app.post("/sync/register")
async def register_device(device: DeviceRegistration):
    """
    Register M5Stack device with sync server
    First-time setup for new devices
    """
    try:
        device_id = device.device_id

        # Check if device already registered
        if device_id in device_registry:
            logger.info(f"Device {device_id} already registered, updating info")
        else:
            logger.info(f"Registering new device: {device_id}")

        # Register device
        device_registry[device_id] = {
            "device_id": device_id,
            "device_type": device.device_type,
            "firmware_version": device.firmware_version,
            "capabilities": device.capabilities,
            "registered_at": datetime.now().isoformat(),
            "last_sync": None,
            "active": True
        }

        # Store in brain as knowledge
        brain.store_knowledge(
            category="devices",
            key=device_id,
            value=f"{device.device_type} registered at {datetime.now().isoformat()}",
            importance=7
        )

        return {
            "status": "success",
            "device_id": device_id,
            "message": "Device registered successfully",
            "server_time": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Device registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/upload")
async def upload_brain_data(sync_request: BrainSyncRequest):
    """
    Upload offline conversations and knowledge from M5Stack
    This is the core of "Alfred Everywhere" - offline learning sync
    """
    try:
        device_id = sync_request.device_id

        # Verify device is registered
        if device_id not in device_registry:
            logger.warning(f"Unregistered device attempting sync: {device_id}")
            # Auto-register for convenience
            device_registry[device_id] = {
                "device_id": device_id,
                "device_type": "m5stack-auto",
                "registered_at": datetime.now().isoformat(),
                "active": True
            }

        logger.info(f"Syncing brain data from device: {device_id}")
        logger.info(f"  Conversations: {len(sync_request.conversations)}")
        logger.info(f"  Knowledge updates: {len(sync_request.knowledge_updates)}")

        upload_results = {
            "conversations_uploaded": 0,
            "knowledge_uploaded": 0,
            "conflicts": []
        }

        # Upload conversations
        for conv in sync_request.conversations:
            try:
                brain.store_conversation(
                    user_input=conv.user_input,
                    alfred_response=conv.alfred_response,
                    context={
                        "source": conv.source,
                        "device_id": device_id,
                        "offline_timestamp": conv.timestamp
                    },
                    topics=conv.topics if conv.topics else None,
                    importance=conv.importance,
                    success=True
                )
                upload_results["conversations_uploaded"] += 1
            except Exception as e:
                logger.error(f"Error uploading conversation: {e}")
                upload_results["conflicts"].append({
                    "type": "conversation",
                    "error": str(e),
                    "data": conv.user_input[:50]
                })

        # Upload knowledge updates
        for knowledge in sync_request.knowledge_updates:
            try:
                # Check for conflicts (existing knowledge with different value)
                existing = brain.recall_knowledge(knowledge.category, knowledge.key)

                if existing and existing.get("value") != knowledge.value:
                    # Conflict detected - use importance to resolve
                    existing_importance = existing.get("importance", 0)
                    if knowledge.importance >= existing_importance:
                        # New knowledge wins
                        brain.store_knowledge(
                            category=knowledge.category,
                            key=knowledge.key,
                            value=knowledge.value,
                            importance=knowledge.importance
                        )
                        upload_results["knowledge_uploaded"] += 1
                        logger.info(f"Resolved conflict: {knowledge.category}/{knowledge.key} (new wins)")
                    else:
                        # Keep existing
                        upload_results["conflicts"].append({
                            "type": "knowledge",
                            "category": knowledge.category,
                            "key": knowledge.key,
                            "reason": "existing knowledge has higher importance",
                            "existing_importance": existing_importance,
                            "new_importance": knowledge.importance
                        })
                        logger.info(f"Resolved conflict: {knowledge.category}/{knowledge.key} (existing wins)")
                else:
                    # No conflict, store normally
                    brain.store_knowledge(
                        category=knowledge.category,
                        key=knowledge.key,
                        value=knowledge.value,
                        importance=knowledge.importance
                    )
                    upload_results["knowledge_uploaded"] += 1

            except Exception as e:
                logger.error(f"Error uploading knowledge: {e}")
                upload_results["conflicts"].append({
                    "type": "knowledge",
                    "error": str(e),
                    "data": f"{knowledge.category}/{knowledge.key}"
                })

        # Update device last sync time
        device_registry[device_id]["last_sync"] = datetime.now().isoformat()

        logger.info(f"Sync complete for {device_id}: {upload_results}")

        return {
            "status": "success",
            "device_id": device_id,
            "results": upload_results,
            "server_time": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/download")
async def download_brain_updates(device_id: str, since: Optional[str] = None):
    """
    Download brain updates from server to M5Stack
    Delta sync: only send updates since last sync
    """
    try:
        logger.info(f"Brain download request from device: {device_id}")
        if since:
            logger.info(f"  Delta sync since: {since}")

        # Get recent conversations (limit to last 10 for M5Stack storage)
        conversations = brain.get_conversation_context(limit=10)

        # Get important knowledge (top 20 by importance)
        # TODO: Add get_top_knowledge method to brain
        # For now, return empty list
        knowledge_updates = []

        # Get topics for context
        topics = brain.get_topics_by_importance()[:5]  # Top 5 topics

        download_data = {
            "conversations": conversations if conversations else [],
            "knowledge_updates": knowledge_updates,
            "topics": [t.get("topic_name") for t in topics] if topics else [],
            "server_time": datetime.now().isoformat(),
            "sync_metadata": {
                "total_conversations": len(conversations) if conversations else 0,
                "total_knowledge": len(knowledge_updates),
                "is_delta_sync": since is not None
            }
        }

        logger.info(f"Sending {len(download_data['conversations'])} conversations to {device_id}")

        return download_data

    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/status")
async def sync_status(device_id: str):
    """Get sync status for a device"""
    try:
        if device_id not in device_registry:
            raise HTTPException(status_code=404, detail="Device not registered")

        device_info = device_registry[device_id]

        return {
            "device_id": device_id,
            "registered": True,
            "last_sync": device_info.get("last_sync"),
            "active": device_info.get("active", False),
            "device_type": device_info.get("device_type"),
            "brain_stats": brain.get_stats(),
            "server_time": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run Alfred Sync Server"""
    logger.info("=" * 70)
    logger.info("Alfred Sync Server - Brain Synchronization for M5Stack")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Server will be available at: http://0.0.0.0:5000")
    logger.info("M5Stack devices can connect via WiFi or mobile hotspot")
    logger.info("")
    logger.info("OpenAI-Compatible Endpoints:")
    logger.info("  POST /v1/chat/completions")
    logger.info("  POST /v1/completions")
    logger.info("  GET  /v1/models")
    logger.info("")
    logger.info("Brain Sync Endpoints:")
    logger.info("  POST /sync/register - Register M5Stack device")
    logger.info("  POST /sync/upload - Upload offline conversations/knowledge")
    logger.info("  GET  /sync/download - Download brain updates")
    logger.info("  GET  /sync/status - Get device sync status")
    logger.info("")
    logger.info(f"Brain Database: {brain.db_path}")
    logger.info(f"Privacy Mode: {privacy.get_status()['mode']}")
    logger.info("")
    logger.info("Press Ctrl+C to stop server")
    logger.info("=" * 70)

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Accept connections from M5Stack on network
        port=5000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
