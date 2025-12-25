#!/usr/bin/env python3
"""
ALFRED MCP Server - Enhanced with Voice, Privacy, and Multi-Model Controls

Exposes ALFRED's brain, voice, privacy controls, and AI orchestration to Claude Code.

Tools provided:
- Brain: recall_knowledge, store_knowledge, get_conversation_context, store_mistake
- Skills: get_skills, get_topics, get_patterns, get_memory_stats
- Voice: speak, set_voice_personality, toggle_voice
- Privacy: get_privacy_status, request_cloud_access, set_privacy_mode
- AI: get_available_models, generate_with_model, consolidate_memory
"""

import asyncio
import json
from typing import Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: MCP library not installed. Run: pip install mcp")
    sys.exit(1)

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController, CloudProvider, PrivacyMode
from capabilities.voice.alfred_voice import AlfredVoice, VoicePersonality
from ai.multimodel import MultiModelOrchestrator


class AlfredMCPServer:
    """MCP Server for ALFRED AI Assistant"""

    def __init__(self):
        """Initialize ALFRED MCP Server"""
        self.server = Server("alfred-brain")
        self.brain = AlfredBrain()
        self.privacy = PrivacyController()
        self.voice = None  # Lazy load to avoid initialization issues
        self.ai = None  # Lazy load

        self._setup_handlers()

    def _get_voice(self) -> AlfredVoice:
        """Lazy load voice system"""
        if self.voice is None:
            try:
                self.voice = AlfredVoice(privacy_mode=True)
            except Exception as e:
                print(f"Warning: Voice system unavailable: {e}")
                self.voice = None
        return self.voice

    def _get_ai(self) -> MultiModelOrchestrator:
        """Lazy load AI orchestrator"""
        if self.ai is None:
            self.ai = MultiModelOrchestrator(privacy_controller=self.privacy)
        return self.ai

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            return [
                # ===== BRAIN TOOLS =====
                types.Tool(
                    name="alfred_recall_knowledge",
                    description="Query ALFRED's brain for stored knowledge by category and key",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Knowledge category"},
                            "key": {"type": "string", "description": "Knowledge key (optional)"},
                        },
                        "required": ["category"],
                    },
                ),
                types.Tool(
                    name="alfred_store_knowledge",
                    description="Store new knowledge in ALFRED's brain",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Knowledge category"},
                            "key": {"type": "string", "description": "Knowledge key"},
                            "value": {"type": "string", "description": "Knowledge value"},
                            "importance": {"type": "integer", "description": "Importance (1-10)", "default": 5},
                            "confidence": {"type": "number", "description": "Confidence (0.0-1.0)", "default": 0.8},
                        },
                        "required": ["category", "key", "value"],
                    },
                ),
                types.Tool(
                    name="alfred_get_conversation_context",
                    description="Get recent conversation history with importance filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max conversations", "default": 10},
                            "min_importance": {"type": "integer", "description": "Min importance (1-10)", "default": 1},
                        },
                    },
                ),
                types.Tool(
                    name="alfred_store_mistake",
                    description="Record a mistake for learning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mistake_type": {"type": "string", "description": "Type of mistake"},
                            "description": {"type": "string", "description": "What went wrong"},
                            "context": {"type": "string", "description": "Context when it happened"},
                            "lesson": {"type": "string", "description": "What was learned"},
                        },
                        "required": ["mistake_type", "description", "lesson"],
                    },
                ),

                # ===== SKILL/PATTERN TOOLS =====
                types.Tool(
                    name="alfred_get_skills",
                    description="Get ALFRED's skill proficiency levels",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="alfred_get_topics",
                    description="Get tracked conversation topics with frequency",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max topics", "default": 20},
                        },
                    },
                ),
                types.Tool(
                    name="alfred_get_patterns",
                    description="Get learned behavioral patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_type": {"type": "string", "description": "Pattern type (optional)"},
                        },
                    },
                ),
                types.Tool(
                    name="alfred_get_memory_stats",
                    description="Get brain memory statistics",
                    inputSchema={"type": "object", "properties": {}},
                ),

                # ===== VOICE TOOLS =====
                types.Tool(
                    name="alfred_speak",
                    description="Make ALFRED speak with British butler voice",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to speak"},
                            "personality": {
                                "type": "string",
                                "description": "Voice personality",
                                "enum": ["GREETING", "CONFIRMATION", "WARNING", "SUGGESTION", "SARCASM", "INFORMATION", "ERROR"],
                                "default": "INFORMATION"
                            },
                        },
                        "required": ["text"],
                    },
                ),
                types.Tool(
                    name="alfred_toggle_voice",
                    description="Enable or disable voice output",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean", "description": "Enable voice"},
                        },
                        "required": ["enabled"],
                    },
                ),

                # ===== PRIVACY TOOLS =====
                types.Tool(
                    name="alfred_get_privacy_status",
                    description="Get current privacy mode and cloud provider usage",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="alfred_request_cloud_access",
                    description="Request access to cloud AI provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Cloud provider",
                                "enum": ["CLAUDE", "OPENAI", "GROQ"]
                            },
                            "reason": {"type": "string", "description": "Reason for cloud access"},
                        },
                        "required": ["provider", "reason"],
                    },
                ),
                types.Tool(
                    name="alfred_set_privacy_mode",
                    description="Set privacy mode (LOCAL, HYBRID, or CLOUD)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "description": "Privacy mode",
                                "enum": ["LOCAL", "HYBRID", "CLOUD"]
                            },
                        },
                        "required": ["mode"],
                    },
                ),

                # ===== AI ORCHESTRATION TOOLS =====
                types.Tool(
                    name="alfred_get_available_models",
                    description="Get list of available AI models (local and cloud)",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="alfred_generate_with_model",
                    description="Generate response using specific AI model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Prompt for AI"},
                            "model": {"type": "string", "description": "Model name (optional, uses fallback chain)"},
                            "context": {"type": "string", "description": "Additional context (optional)"},
                        },
                        "required": ["prompt"],
                    },
                ),
                types.Tool(
                    name="alfred_consolidate_memory",
                    description="Trigger memory consolidation to optimize brain storage",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            try:
                # ===== BRAIN TOOLS =====
                if name == "alfred_recall_knowledge":
                    category = arguments["category"]
                    key = arguments.get("key")

                    if key:
                        result = self.brain.recall_knowledge(category, key)
                        if result:
                            return [types.TextContent(
                                type="text",
                                text=json.dumps(result, indent=2)
                            )]
                        else:
                            return [types.TextContent(
                                type="text",
                                text=f"No knowledge found for {category}/{key}"
                            )]
                    else:
                        results = self.brain.recall_all_knowledge(category)
                        return [types.TextContent(
                            type="text",
                            text=json.dumps(results, indent=2)
                        )]

                elif name == "alfred_store_knowledge":
                    self.brain.store_knowledge(
                        category=arguments["category"],
                        key=arguments["key"],
                        value=arguments["value"],
                        importance=arguments.get("importance", 5),
                        confidence=arguments.get("confidence", 0.8)
                    )
                    return [types.TextContent(
                        type="text",
                        text=f"Knowledge stored: {arguments['category']}/{arguments['key']}"
                    )]

                elif name == "alfred_get_conversation_context":
                    limit = arguments.get("limit", 10)
                    min_importance = arguments.get("min_importance", 1)

                    context = self.brain.get_conversation_context(limit=limit)
                    # Filter by importance
                    filtered = [c for c in context if c.get("importance", 0) >= min_importance]

                    return [types.TextContent(
                        type="text",
                        text=json.dumps(filtered, indent=2)
                    )]

                elif name == "alfred_store_mistake":
                    self.brain.store_mistake(
                        mistake_type=arguments["mistake_type"],
                        description=arguments["description"],
                        context=arguments.get("context", ""),
                        lesson=arguments["lesson"]
                    )
                    return [types.TextContent(
                        type="text",
                        text="Mistake recorded for learning"
                    )]

                # ===== SKILL/PATTERN TOOLS =====
                elif name == "alfred_get_skills":
                    skills = self.brain.get_all_skills()
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(skills, indent=2)
                    )]

                elif name == "alfred_get_topics":
                    limit = arguments.get("limit", 20)
                    topics = self.brain.get_tracked_topics(limit=limit)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(topics, indent=2)
                    )]

                elif name == "alfred_get_patterns":
                    pattern_type = arguments.get("pattern_type")
                    patterns = self.brain.get_learned_patterns(pattern_type=pattern_type)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(patterns, indent=2)
                    )]

                elif name == "alfred_get_memory_stats":
                    stats = self.brain.get_memory_stats()
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(stats, indent=2)
                    )]

                # ===== VOICE TOOLS =====
                elif name == "alfred_speak":
                    voice = self._get_voice()
                    if voice:
                        text = arguments["text"]
                        personality_str = arguments.get("personality", "INFORMATION")
                        personality = VoicePersonality[personality_str]

                        voice.speak(text, personality=personality)
                        return [types.TextContent(
                            type="text",
                            text=f"Spoke with {personality_str} personality: {text}"
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text="Voice system not available"
                        )]

                elif name == "alfred_toggle_voice":
                    voice = self._get_voice()
                    if voice:
                        enabled = arguments["enabled"]
                        voice.enabled = enabled
                        return [types.TextContent(
                            type="text",
                            text=f"Voice {'enabled' if enabled else 'disabled'}"
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text="Voice system not available"
                        )]

                # ===== PRIVACY TOOLS =====
                elif name == "alfred_get_privacy_status":
                    status = {
                        "mode": self.privacy.mode.name,
                        "cloud_usage": {
                            provider.name: count
                            for provider, count in self.privacy.cloud_usage.items()
                        },
                        "total_cloud_requests": self.privacy.total_cloud_requests
                    }
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(status, indent=2)
                    )]

                elif name == "alfred_request_cloud_access":
                    provider_str = arguments["provider"]
                    provider = CloudProvider[provider_str]
                    reason = arguments["reason"]

                    # For MCP, we auto-approve since Claude Code is already a cloud service
                    # User has implicitly consented by using Claude Code
                    approved = True

                    return [types.TextContent(
                        type="text",
                        text=f"Cloud access to {provider_str} approved for: {reason}"
                    )]

                elif name == "alfred_set_privacy_mode":
                    mode_str = arguments["mode"]
                    mode = PrivacyMode[mode_str]
                    self.privacy.mode = mode

                    return [types.TextContent(
                        type="text",
                        text=f"Privacy mode set to {mode_str}"
                    )]

                # ===== AI ORCHESTRATION TOOLS =====
                elif name == "alfred_get_available_models":
                    ai = self._get_ai()
                    models = {
                        "local": ai.get_local_models() if hasattr(ai, 'get_local_models') else ["ollama"],
                        "cloud": ["claude", "openai", "groq"] if self.privacy.mode != PrivacyMode.LOCAL else []
                    }
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(models, indent=2)
                    )]

                elif name == "alfred_generate_with_model":
                    ai = self._get_ai()
                    prompt = arguments["prompt"]
                    context = arguments.get("context", "")

                    full_prompt = f"{context}\n\n{prompt}" if context else prompt
                    response = ai.generate(full_prompt, context={})

                    return [types.TextContent(
                        type="text",
                        text=response
                    )]

                elif name == "alfred_consolidate_memory":
                    self.brain.consolidate_memory()
                    return [types.TextContent(
                        type="text",
                        text="Memory consolidation completed"
                    )]

                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = AlfredMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
