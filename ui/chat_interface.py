"""
ALFRED Chat Interface - Modern Web-Based UI for Desktop/Mobile

Features:
- Clean, responsive chat interface
- Local-first privacy (Ollama default)
- Agent selection and parallel execution display
- Response quality indicators
- Brain memory visualization
- Task type detection display

Author: Daniel J Rita (BATDAN)
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController, CloudProvider
from core.task_classifier import TaskClassifier
from core.agent_selector import AgentSelector
from core.response_quality_checker import ResponseQualityChecker
from ai.multimodel import MultiModelOrchestrator


class AlfredChatServer:
    """FastAPI server for ALFRED Chat UI"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        """Initialize chat server"""
        self.host = host
        self.port = port
        self.logger = self._setup_logging()

        # Initialize components
        self.brain = AlfredBrain()
        self.privacy = PrivacyController(default_mode="LOCAL")
        self.classifier = TaskClassifier(self.brain)
        self.selector = AgentSelector(self.brain)
        self.quality_checker = ResponseQualityChecker(self.brain)
        self.ai = MultiModelOrchestrator(self.privacy)

        # FastAPI app
        self.app = FastAPI(
            title="ALFRED Chat",
            description="Private AI Assistant with Persistent Memory",
            version="1.0.0"
        )

        self._setup_routes()
        self._setup_middleware()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alfred_chat.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            """Serve chat UI"""
            return self._get_html_ui()

        @self.app.websocket("/ws/chat")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for chat"""
            await websocket.accept()

            try:
                while True:
                    # Receive user message
                    data = await websocket.receive_text()
                    message_data = json.loads(data)

                    user_input = message_data.get("message", "").strip()
                    if not user_input:
                        continue

                    # Classify task
                    task_type, task_confidence, task_metadata = self.classifier.classify(user_input)

                    # Select agents
                    agents = self.selector.select_agents(user_input, max_agents=3)

                    # Send task classification to client
                    await websocket.send_json({
                        "type": "task_classification",
                        "task_type": task_type.value,
                        "confidence": task_confidence,
                        "agents": agents,
                        "metadata": task_metadata
                    })

                    # Generate response with parallel agent execution
                    try:
                        response_text = await self._generate_response_with_agents(
                            user_input, agents, task_type
                        )
                    except Exception as e:
                        response_text = f"Error generating response: {str(e)}"
                        self.logger.error(f"Response generation error: {e}")

                    # Check response quality
                    quality_assessment = self.quality_checker.check_response(
                        response_text, user_input
                    )

                    # Store conversation
                    self.brain.store_conversation(
                        user_input=user_input,
                        alfred_response=response_text,
                        success=quality_assessment.get("is_clean", True)
                    )

                    # Send response to client
                    await websocket.send_json({
                        "type": "response",
                        "message": response_text,
                        "quality": {
                            "level": quality_assessment["quality_level"].value,
                            "is_clean": quality_assessment["is_clean"],
                            "flags": quality_assessment["flags"],
                            "confidence": quality_assessment["confidence"],
                        }
                    })

            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                await websocket.close()

        @self.app.get("/api/privacy-status")
        async def get_privacy_status():
            """Get current privacy mode"""
            return {
                "mode": self.privacy.mode.value,
                "cloud_allowed": self.privacy.cloud_access_allowed,
                "last_cloud_request": self.privacy.last_cloud_request_at,
                "explanation": "All data stays on your device by default. Cloud AI requires your explicit permission."
            }

        @self.app.post("/api/request-cloud-access")
        async def request_cloud_access(provider: str = Query("claude")):
            """Request cloud AI access"""
            try:
                provider_enum = CloudProvider[provider.upper()]

                # Check if already approved
                if self.privacy.cloud_access_allowed:
                    return {
                        "approved": True,
                        "message": f"Cloud access to {provider_enum.value} already approved"
                    }

                # In interactive mode, this would prompt user
                # For now, return request status
                return {
                    "approved": False,
                    "message": f"Cloud access requires explicit permission. Use privacy controls to approve {provider_enum.value}",
                    "providers": [p.value for p in CloudProvider]
                }

            except KeyError:
                raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

        @self.app.get("/api/brain-stats")
        async def get_brain_stats():
            """Get brain memory statistics"""
            stats = self.brain.get_memory_stats()
            return {
                "total_conversations": stats.get("conversations", 0),
                "total_knowledge": stats.get("knowledge", 0),
                "patterns_learned": stats.get("patterns", 0),
                "skills_tracked": stats.get("skills", 0),
                "last_consolidated": stats.get("last_consolidated"),
            }

        @self.app.get("/api/task-history")
        async def get_task_history(limit: int = Query(10, ge=1, le=100)):
            """Get recent task classifications"""
            try:
                history = self.brain.search_conversations(
                    "",
                    limit=limit
                )

                return {
                    "recent_tasks": [
                        {
                            "timestamp": conv.get("timestamp"),
                            "input": conv.get("user_input")[:100],
                            "success": conv.get("success", False)
                        }
                        for conv in history
                    ]
                }
            except Exception as e:
                self.logger.error(f"Error fetching task history: {e}")
                return {"recent_tasks": []}

        @self.app.get("/api/agent-performance")
        async def get_agent_performance():
            """Get agent success rates"""
            try:
                performance = self.brain.recall_knowledge("agent_performance")
                if not performance:
                    return {"agents": {}}

                return {
                    "agents": performance
                }
            except Exception as e:
                self.logger.error(f"Error fetching agent performance: {e}")
                return {"agents": {}}

    async def _generate_response_with_agents(
        self,
        user_input: str,
        agents: List[Dict],
        task_type
    ) -> str:
        """Generate response using selected agents in parallel"""

        if not agents:
            # Fallback to default Ollama
            return await self.ai.generate(
                prompt=user_input,
                context="",
                max_tokens=2000
            )

        # Extract agent names and models
        selected_agents = [
            {
                "name": agent.get("agent"),
                "model": agent.get("model_tier", "sonnet")
            }
            for agent in agents[:3]  # Limit to 3 parallel agents
        ]

        # For now, use primary agent (parallel execution can be enhanced)
        primary_agent = selected_agents[0]

        try:
            response = await self.ai.generate(
                prompt=user_input,
                context=f"Using agent: {primary_agent['name']} with model tier: {primary_agent['model']}",
                max_tokens=2000
            )

            # Record agent outcome
            self.selector.record_agent_outcome(
                agent_name=primary_agent["name"],
                task_type=task_type,
                success=True,
                feedback="Response generated successfully"
            )

            return response

        except Exception as e:
            self.logger.error(f"Agent response error: {e}")
            raise

    def _get_html_ui(self) -> HTMLResponse:
        """Return HTML chat UI"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFRED Chat - Private AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 900px;
            height: 90vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .privacy-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            display: flex;
            gap: 12px;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message.alfred {
            justify-content: flex-start;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
        }

        .message.user .message-content {
            background: #667eea;
            color: white;
        }

        .message.alfred .message-content {
            background: #f0f0f0;
            color: #333;
        }

        .message-meta {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }

        .quality-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 8px;
            font-weight: 500;
        }

        .quality-verified {
            background: #d4edda;
            color: #155724;
        }

        .quality-honest-limitation {
            background: #fff3cd;
            color: #856404;
        }

        .quality-suspicious {
            background: #f8d7da;
            color: #721c24;
        }

        .agent-selection {
            background: #f9f9f9;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            font-size: 12px;
            color: #666;
        }

        .agent-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            margin-right: 8px;
            margin-top: 4px;
        }

        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 12px;
        }

        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }

        .input-area input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .input-area button:hover {
            background: #5568d3;
        }

        .input-area button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #721c24;
        }

        @media (max-width: 768px) {
            .message-content {
                max-width: 90%;
            }

            .header h1 {
                font-size: 18px;
            }

            .container {
                border-radius: 0;
                height: 100vh;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 ALFRED</h1>
            <p>Your Private AI Assistant with Persistent Memory</p>
            <div class="privacy-badge">🔒 Local-First Private</div>
        </div>

        <div class="chat-container" id="chatContainer">
            <div class="message alfred">
                <div>
                    <div class="message-content">
                        Hello! I'm ALFRED, your private AI assistant. I run locally on your device by default, so your data never leaves your computer unless you explicitly approve it. How can I help you today?
                    </div>
                    <div class="message-meta">Alfred • just now</div>
                </div>
            </div>
        </div>

        <div class="input-area">
            <input
                type="text"
                id="messageInput"
                placeholder="Ask me anything... (runs locally & privately)"
                autocomplete="off"
            />
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        let ws = null;
        let isConnecting = false;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);

            ws.onopen = () => {
                console.log('Connected to ALFRED');
                isConnecting = false;
                sendButton.disabled = false;
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'task_classification') {
                    showTaskClassification(data);
                } else if (data.type === 'response') {
                    showResponse(data);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                showError('Connection error. Ensure ALFRED server is running.');
            };

            ws.onclose = () => {
                console.log('Disconnected from ALFRED');
                setTimeout(connectWebSocket, 3000);
            };
        }

        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }

            // Show user message
            addMessage(message, 'user');

            // Send to server
            ws.send(JSON.stringify({ message }));

            // Clear input and show typing indicator
            messageInput.value = '';
            showTypingIndicator();

            sendButton.disabled = true;
        }

        function addMessage(text, sender) {
            const messageEl = document.createElement('div');
            messageEl.className = `message ${sender}`;

            const contentEl = document.createElement('div');
            contentEl.className = 'message-content';
            contentEl.textContent = text;

            const metaEl = document.createElement('div');
            metaEl.className = 'message-meta';
            metaEl.textContent = sender === 'user' ? 'You • just now' : 'Alfred • just now';

            messageEl.appendChild(contentEl);
            messageEl.appendChild(metaEl);
            chatContainer.appendChild(messageEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showTaskClassification(data) {
            const infoEl = document.createElement('div');
            infoEl.className = 'agent-selection';

            let agents = '';
            if (data.agents && data.agents.length > 0) {
                agents = data.agents.map(a => `<span class="agent-badge">${a.agent} (${a.model_tier})</span>`).join('');
            }

            infoEl.innerHTML = `
                <strong>Task Type:</strong> ${data.task_type} (${(data.confidence * 100).toFixed(0)}% confident)<br>
                <strong>Agents:</strong><br>${agents}
            `;

            chatContainer.appendChild(infoEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showResponse(data) {
            // Remove typing indicator
            const typing = document.querySelector('.typing-indicator');
            if (typing) {
                typing.remove();
            }

            const messageEl = document.createElement('div');
            messageEl.className = 'message alfred';

            const contentEl = document.createElement('div');
            contentEl.className = 'message-content';

            let qualityBadge = '';
            if (data.quality) {
                const qualityClass = `quality-${data.quality.level.replace(/_/g, '-')}`;
                qualityBadge = `<span class="quality-badge ${qualityClass}">${data.quality.level.replace(/_/g, ' ')}</span>`;
            }

            contentEl.innerHTML = `${data.message}${qualityBadge}`;

            const metaEl = document.createElement('div');
            metaEl.className = 'message-meta';
            metaEl.textContent = 'Alfred • just now';

            messageEl.appendChild(contentEl);
            messageEl.appendChild(metaEl);
            chatContainer.appendChild(messageEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            sendButton.disabled = false;
        }

        function showTypingIndicator() {
            const indicatorEl = document.createElement('div');
            indicatorEl.className = 'typing-indicator';
            indicatorEl.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

            chatContainer.appendChild(indicatorEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showError(message) {
            const errorEl = document.createElement('div');
            errorEl.className = 'error-message';
            errorEl.textContent = message;

            chatContainer.appendChild(errorEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Event listeners
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Connect on page load
        connectWebSocket();
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html)

    def run(self):
        """Run the chat server"""
        self.logger.info(f"Starting ALFRED Chat Server on {self.host}:{self.port}")
        self.logger.info(f"Privacy Mode: {self.privacy.mode.value}")
        self.logger.info(f"Open browser to http://localhost:{self.port}")

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )


def main():
    """Main entry point"""
    server = AlfredChatServer(host="127.0.0.1", port=8000)
    server.run()


if __name__ == "__main__":
    main()
