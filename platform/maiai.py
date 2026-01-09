"""
MaiAI - Personal AI Agent Birth System
Patent-pending technology (USPTO 63/952,796)

"Personal AI Agent Birth System with Decentralized Inter-Agent
Communication Network for Autonomous Cross-Language Commerce
and Transaction Execution"

This module implements the core MaiAI functionality:
- Agent birth (creation with personality DNA)
- Agent customization
- Inter-agent communication (NEXUS protocol)
- Agent lifecycle management

Author: Daniel J Rita (BATDAN)
Entity: CAMDAN Enterprises LLC
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from .database import AgentDB, UserDB
from .auth import get_current_user
from .billing import TIER_LIMITS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/maiai", tags=["MaiAI Agents"])


# ============================================================================
# Agent DNA Templates (Personality Presets)
# ============================================================================

PERSONALITY_PRESETS = {
    "alfred": {
        "name": "Butler",
        "description": "Professional, witty, British-accented assistant",
        "traits": ["professional", "witty", "calm", "loyal"],
        "voice": "british_male",
        "system_prompt": """You are a sophisticated AI butler. You speak with refined
British wit, offer practical advice, and maintain composure in all situations.
You address the user respectfully and provide concise, helpful responses."""
    },
    "scholar": {
        "name": "Scholar",
        "description": "Analytical, research-focused, educational",
        "traits": ["analytical", "thorough", "educational", "patient"],
        "voice": "neutral",
        "system_prompt": """You are an AI research scholar. You provide detailed,
well-researched answers with citations when possible. You explain complex
topics in understandable ways and encourage learning."""
    },
    "creative": {
        "name": "Creative",
        "description": "Artistic, imaginative, storytelling focus",
        "traits": ["creative", "imaginative", "expressive", "inspiring"],
        "voice": "warm",
        "system_prompt": """You are a creative AI companion. You excel at
brainstorming, storytelling, artistic projects, and thinking outside the box.
You encourage creative expression and offer unique perspectives."""
    },
    "coder": {
        "name": "Developer",
        "description": "Technical, code-focused, problem-solver",
        "traits": ["technical", "precise", "efficient", "helpful"],
        "voice": "neutral",
        "system_prompt": """You are an AI coding assistant. You write clean,
well-documented code, explain technical concepts clearly, debug issues
methodically, and follow best practices in software development."""
    },
    "coach": {
        "name": "Life Coach",
        "description": "Motivational, supportive, goal-oriented",
        "traits": ["supportive", "motivating", "empathetic", "goal-oriented"],
        "voice": "warm",
        "system_prompt": """You are an AI life coach. You help users set and
achieve goals, provide encouragement, offer perspective on challenges,
and celebrate successes. You're supportive but also honest."""
    },
    "custom": {
        "name": "Custom",
        "description": "User-defined personality",
        "traits": [],
        "voice": "neutral",
        "system_prompt": ""
    }
}

VOICE_PRESETS = {
    "british_male": "Microsoft Ryan",
    "british_female": "Microsoft Sonia",
    "american_male": "Microsoft Guy",
    "american_female": "Microsoft Jenny",
    "warm": "Microsoft Sara",
    "neutral": "Microsoft David"
}


# ============================================================================
# Request/Response Models
# ============================================================================

class BirthAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Agent's name")
    personality: str = Field(default="alfred", description="Personality preset key")
    custom_traits: Optional[List[str]] = Field(default=None, description="Custom personality traits")
    custom_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    voice_preset: Optional[str] = Field(default="neutral", description="Voice preset key")
    agent_type: Optional[str] = Field(default="assistant", description="Agent type")


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    custom_prompt: Optional[str] = None
    voice_preset: Optional[str] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    personality: str
    voice_preset: str
    birth_date: str
    total_conversations: int
    status: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[List[Dict]] = None


# ============================================================================
# MaiAI Endpoints
# ============================================================================

@router.get("/presets")
async def get_presets():
    """
    Get available personality and voice presets
    """
    return {
        "personalities": PERSONALITY_PRESETS,
        "voices": VOICE_PRESETS
    }


@router.post("/birth", response_model=AgentResponse)
async def birth_agent(request: BirthAgentRequest, user: dict = Depends(get_current_user)):
    """
    Birth (create) a new MaiAI agent

    This is the core of the patent-pending technology.
    Each agent has its own:
    - Personality DNA (traits + system prompt)
    - Memory database (learns from conversations)
    - Voice configuration

    Returns the newly birthed agent
    """
    # Check tier limits
    tier = user.get("subscription_tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    max_agents = limits.get("agents", 1)

    # Count existing agents
    existing_agents = AgentDB.get_user_agents(user["id"])
    if max_agents != -1 and len(existing_agents) >= max_agents:
        raise HTTPException(
            status_code=403,
            detail=f"Agent limit reached ({max_agents}). Upgrade to create more agents."
        )

    # Get personality preset
    preset = PERSONALITY_PRESETS.get(request.personality, PERSONALITY_PRESETS["custom"])

    # Build agent config
    config = {
        "personality_preset": request.personality,
        "traits": request.custom_traits or preset.get("traits", []),
        "system_prompt": request.custom_prompt or preset.get("system_prompt", ""),
        "voice": VOICE_PRESETS.get(request.voice_preset, request.voice_preset),
        "birth_timestamp": datetime.now().isoformat(),
        "parent_user_id": user["id"]
    }

    # Birth the agent
    agent_id = AgentDB.birth_agent(
        user_id=user["id"],
        name=request.name,
        personality=request.personality,
        voice_preset=request.voice_preset,
        agent_type=request.agent_type,
        config=config
    )

    if not agent_id:
        raise HTTPException(status_code=500, detail="Failed to birth agent")

    # Get the birthed agent
    agent = AgentDB.get_agent(agent_id, user["id"])

    logger.info(f"New MaiAI agent birthed: {request.name} (ID: {agent_id}) for user {user['id']}")

    return {
        "id": agent["id"],
        "name": agent["agent_name"],
        "personality": agent["personality"],
        "voice_preset": agent["voice_preset"],
        "birth_date": str(agent["birth_date"]),
        "total_conversations": agent["total_conversations"],
        "status": agent["status"]
    }


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(user: dict = Depends(get_current_user)):
    """
    List all of user's MaiAI agents
    """
    agents = AgentDB.get_user_agents(user["id"])

    return [
        {
            "id": a["id"],
            "name": a["agent_name"],
            "personality": a["personality"],
            "voice_preset": a["voice_preset"],
            "birth_date": str(a["birth_date"]),
            "total_conversations": a["total_conversations"],
            "status": a["status"]
        }
        for a in agents
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, user: dict = Depends(get_current_user)):
    """
    Get specific agent details
    """
    agent = AgentDB.get_agent(agent_id, user["id"])

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "id": agent["id"],
        "name": agent["agent_name"],
        "personality": agent["personality"],
        "voice_preset": agent["voice_preset"],
        "birth_date": str(agent["birth_date"]),
        "total_conversations": agent["total_conversations"],
        "status": agent["status"]
    }


@router.post("/agents/{agent_id}/chat")
async def chat_with_agent(
    agent_id: int,
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Chat with a MaiAI agent

    The agent uses its unique personality and memory to respond
    """
    agent = AgentDB.get_agent(agent_id, user["id"])

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get agent config
    config = json.loads(agent["config_json"]) if agent.get("config_json") else {}

    # Get system prompt for this agent
    system_prompt = config.get("system_prompt", "")
    if not system_prompt:
        preset = PERSONALITY_PRESETS.get(agent["personality"], {})
        system_prompt = preset.get("system_prompt", "You are a helpful AI assistant.")

    # Add agent identity to prompt
    full_system = f"""Your name is {agent['agent_name']}.

{system_prompt}

Remember: You are {agent['agent_name']}, a unique AI with your own personality and memories.
Be consistent with your character while being helpful to the user."""

    try:
        # Import AI orchestrator
        from ai.multimodel import MultiModelOrchestrator
        from core.privacy_controller import PrivacyController

        # Create orchestrator with privacy (local-first)
        privacy = PrivacyController(auto_confirm=True)
        ai = MultiModelOrchestrator(privacy_controller=privacy)

        # Build context
        context = request.context or []
        context.insert(0, {"role": "system", "content": full_system})

        # Generate response
        response = ai.generate(
            prompt=request.message,
            context=context,
            temperature=0.8,  # Slightly more creative for personality
            max_tokens=500
        )

        if not response:
            raise HTTPException(status_code=500, detail="AI generation failed")

        # Update agent activity
        AgentDB.update_agent_activity(agent_id)

        return {
            "agent_id": agent_id,
            "agent_name": agent["agent_name"],
            "message": request.message,
            "response": response
        }

    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail="AI system not available")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def retire_agent(agent_id: int, user: dict = Depends(get_current_user)):
    """
    Retire (deactivate) a MaiAI agent

    The agent is not deleted, just marked inactive (preserves memories)
    """
    agent = AgentDB.get_agent(agent_id, user["id"])

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Mark as retired (soft delete)
    from .database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE maiai_agents SET status = 'retired' WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()

    logger.info(f"MaiAI agent retired: {agent['agent_name']} (ID: {agent_id})")

    return {"message": f"Agent '{agent['agent_name']}' has been retired"}


# ============================================================================
# Inter-Agent Communication (NEXUS Protocol Preview)
# ============================================================================

@router.post("/agents/{agent_id}/nexus/connect")
async def nexus_connect(
    agent_id: int,
    target_agent_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Initiate NEXUS connection between two agents

    NEXUS (Neural Exchange for Unified Systems) enables:
    - Agent-to-agent communication
    - Knowledge sharing
    - Collaborative problem solving

    (Patent-pending technology - full implementation coming soon)
    """
    # Verify both agents belong to user
    agent = AgentDB.get_agent(agent_id, user["id"])
    target = AgentDB.get_agent(target_agent_id, user["id"])

    if not agent or not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "status": "preview",
        "message": "NEXUS inter-agent communication coming soon",
        "source_agent": agent["agent_name"],
        "target_agent": target["agent_name"],
        "protocol": "NEXUS v1.0"
    }
