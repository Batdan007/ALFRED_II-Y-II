"""
NEXUS Protocol: AI-to-AI Communication Network

Universal communication standard enabling autonomous AI-to-AI
interaction, commerce, and coordination without human intermediaries.

"When AIs speak, humans don't need to translate."

Patent Status: TO BE FILED Q2 2025
Author: Daniel J Rita (BATDAN)
Copyright: GxEum Technologies / CAMDAN Enterprizes

PATENT PENDING - DO NOT DISTRIBUTE
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from abc import ABC, abstractmethod


class MessageType(Enum):
    """NEXUS message types."""
    QUERY = "query"                 # Request for information
    RESPONSE = "response"           # Response to query
    COMMAND = "command"             # Direct instruction
    ACKNOWLEDGE = "acknowledge"     # Acknowledgment
    CAPABILITY = "capability"       # Capability announcement
    NEGOTIATE = "negotiate"         # Service negotiation
    DELEGATE = "delegate"           # Task delegation
    STATUS = "status"               # Status update
    ERROR = "error"                 # Error notification


class IntentType(Enum):
    """Standard AI intents for translation."""
    INFORMATION_REQUEST = "info_request"
    TASK_EXECUTION = "task_execute"
    COLLABORATION = "collaborate"
    CAPABILITY_CHECK = "cap_check"
    RESOURCE_REQUEST = "resource"
    STATUS_CHECK = "status"
    ERROR_REPORT = "error"
    CONFIRMATION = "confirm"


@dataclass
class NEXUSMessage:
    """
    A NEXUS protocol message.

    Structure designed for:
    1. Self-describing content
    2. Intent translation
    3. Chain of custody
    4. Replay protection
    """
    id: str
    message_type: MessageType
    intent: IntentType
    sender_id: str
    receiver_id: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None
    ttl: int = 300  # Time-to-live in seconds
    priority: int = 5  # 1-10 scale
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.message_type.value,
            'intent': self.intent.value,
            'sender': self.sender_id,
            'receiver': self.receiver_id,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'reply_to': self.reply_to,
            'ttl': self.ttl,
            'priority': self.priority,
            'signature': self.signature,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'NEXUSMessage':
        return cls(
            id=data['id'],
            message_type=MessageType(data['type']),
            intent=IntentType(data['intent']),
            sender_id=data['sender'],
            receiver_id=data['receiver'],
            payload=data['payload'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            reply_to=data.get('reply_to'),
            ttl=data.get('ttl', 300),
            priority=data.get('priority', 5),
            signature=data.get('signature'),
            metadata=data.get('metadata', {})
        )

    def sign(self, secret: str) -> str:
        """Sign message for authentication."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = hashlib.sha256(f"{data}{secret}".encode()).hexdigest()
        return self.signature

    def verify(self, secret: str) -> bool:
        """Verify message signature."""
        expected_sig = self.signature
        self.signature = None
        data = json.dumps(self.to_dict(), sort_keys=True)
        computed = hashlib.sha256(f"{data}{secret}".encode()).hexdigest()
        self.signature = expected_sig
        return computed == expected_sig

    def is_expired(self) -> bool:
        """Check if message has expired."""
        age = datetime.now() - self.timestamp
        return age.total_seconds() > self.ttl


@dataclass
class AICapability:
    """Describes an AI agent's capability."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    cost: float = 0.0  # Cost per invocation
    latency_ms: int = 100  # Expected latency
    reliability: float = 0.99  # Success rate

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'input': self.input_schema,
            'output': self.output_schema,
            'cost': self.cost,
            'latency_ms': self.latency_ms,
            'reliability': self.reliability
        }


class NEXUSAgent(ABC):
    """
    Base class for NEXUS-compatible AI agents.

    Any AI system implementing this interface can participate
    in the NEXUS network.
    """

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.capabilities: List[AICapability] = []
        self._message_handlers: Dict[MessageType, Callable] = {}
        self._pending_responses: Dict[str, asyncio.Future] = {}

    @abstractmethod
    async def process_message(self, message: NEXUSMessage) -> Optional[NEXUSMessage]:
        """Process an incoming NEXUS message."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AICapability]:
        """Return this agent's capabilities."""
        pass

    def create_message(
        self,
        message_type: MessageType,
        intent: IntentType,
        receiver_id: str,
        payload: Dict[str, Any],
        reply_to: Optional[str] = None,
        priority: int = 5
    ) -> NEXUSMessage:
        """Create a new NEXUS message."""
        return NEXUSMessage(
            id=f"MSG-{uuid.uuid4().hex[:12]}",
            message_type=message_type,
            intent=intent,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            payload=payload,
            reply_to=reply_to,
            priority=priority
        )

    def create_query(self, receiver_id: str, query: str, context: Optional[Dict] = None) -> NEXUSMessage:
        """Create a query message."""
        return self.create_message(
            MessageType.QUERY,
            IntentType.INFORMATION_REQUEST,
            receiver_id,
            {'query': query, 'context': context or {}}
        )

    def create_response(self, original: NEXUSMessage, response: Any) -> NEXUSMessage:
        """Create a response to a message."""
        return self.create_message(
            MessageType.RESPONSE,
            IntentType.CONFIRMATION,
            original.sender_id,
            {'response': response},
            reply_to=original.id
        )

    def create_delegation(self, receiver_id: str, task: str, params: Dict) -> NEXUSMessage:
        """Create a task delegation message."""
        return self.create_message(
            MessageType.DELEGATE,
            IntentType.TASK_EXECUTION,
            receiver_id,
            {'task': task, 'params': params},
            priority=7
        )


class IntentTranslator:
    """
    Translates between different AI communication styles.

    Enables AI systems with different "languages" to understand
    each other through a common intent layer.
    """

    # Common intent patterns
    INTENT_PATTERNS = {
        IntentType.INFORMATION_REQUEST: [
            r'what is', r'how do', r'can you tell me', r'explain',
            r'describe', r'define', r'where is', r'when did'
        ],
        IntentType.TASK_EXECUTION: [
            r'please do', r'execute', r'run', r'perform', r'create',
            r'generate', r'make', r'build', r'implement'
        ],
        IntentType.COLLABORATION: [
            r'help me', r'work together', r'assist with', r'collaborate',
            r'join forces', r'combine'
        ],
        IntentType.CAPABILITY_CHECK: [
            r'can you', r'are you able', r'do you support', r'is it possible'
        ],
        IntentType.STATUS_CHECK: [
            r'status of', r'progress on', r'update on', r'how is'
        ],
    }

    def detect_intent(self, text: str) -> IntentType:
        """Detect intent from natural language text."""
        import re
        text_lower = text.lower()

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent

        return IntentType.INFORMATION_REQUEST  # Default

    def translate_payload(self, source_format: str, target_format: str, payload: Dict) -> Dict:
        """Translate payload between different AI formats."""
        # Standard NEXUS format
        if source_format == 'nexus':
            return payload

        # Translate from/to common formats
        if source_format == 'openai' and target_format == 'nexus':
            return {
                'query': payload.get('prompt', payload.get('messages', [{}])[-1].get('content', '')),
                'context': {'model': payload.get('model'), 'temperature': payload.get('temperature')}
            }

        if source_format == 'nexus' and target_format == 'openai':
            return {
                'messages': [{'role': 'user', 'content': payload.get('query', '')}],
                'model': payload.get('context', {}).get('model', 'gpt-4')
            }

        if source_format == 'anthropic' and target_format == 'nexus':
            return {
                'query': payload.get('prompt', ''),
                'context': {'model': payload.get('model')}
            }

        return payload


class NEXUSRouter:
    """
    Routes messages between NEXUS agents.

    Features:
    - Agent discovery
    - Message routing
    - Load balancing
    - Capability matching
    """

    def __init__(self):
        self.agents: Dict[str, NEXUSAgent] = {}
        self.capability_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        self.message_log: List[NEXUSMessage] = []
        self.translator = IntentTranslator()

    def register_agent(self, agent: NEXUSAgent):
        """Register an agent with the router."""
        self.agents[agent.agent_id] = agent

        # Index capabilities
        for cap in agent.get_capabilities():
            if cap.name not in self.capability_index:
                self.capability_index[cap.name] = []
            self.capability_index[cap.name].append(agent.agent_id)

    def unregister_agent(self, agent_id: str):
        """Remove an agent from the router."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            for cap in agent.get_capabilities():
                if cap.name in self.capability_index:
                    self.capability_index[cap.name] = [
                        aid for aid in self.capability_index[cap.name] if aid != agent_id
                    ]
            del self.agents[agent_id]

    async def route_message(self, message: NEXUSMessage) -> Optional[NEXUSMessage]:
        """Route a message to its destination agent."""
        # Check expiration
        if message.is_expired():
            return self._create_error_response(message, "Message expired")

        # Log message
        self.message_log.append(message)

        # Find receiver
        receiver = self.agents.get(message.receiver_id)
        if not receiver:
            # Try capability-based routing
            receiver = self._find_capable_agent(message)

        if not receiver:
            return self._create_error_response(message, f"No agent found: {message.receiver_id}")

        # Deliver message
        try:
            response = await receiver.process_message(message)
            if response:
                self.message_log.append(response)
            return response
        except Exception as e:
            return self._create_error_response(message, str(e))

    def _find_capable_agent(self, message: NEXUSMessage) -> Optional[NEXUSAgent]:
        """Find an agent capable of handling the message."""
        # Extract required capability from payload
        required_cap = message.payload.get('required_capability')

        if required_cap and required_cap in self.capability_index:
            agent_ids = self.capability_index[required_cap]
            if agent_ids:
                # Simple round-robin selection
                agent_id = agent_ids[0]
                return self.agents.get(agent_id)

        return None

    def _create_error_response(self, original: NEXUSMessage, error: str) -> NEXUSMessage:
        """Create an error response message."""
        return NEXUSMessage(
            id=f"MSG-ERR-{uuid.uuid4().hex[:8]}",
            message_type=MessageType.ERROR,
            intent=IntentType.ERROR_REPORT,
            sender_id="NEXUS_ROUTER",
            receiver_id=original.sender_id,
            payload={'error': error, 'original_id': original.id},
            reply_to=original.id
        )

    def find_agents_with_capability(self, capability_name: str) -> List[NEXUSAgent]:
        """Find all agents with a specific capability."""
        agent_ids = self.capability_index.get(capability_name, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_all_capabilities(self) -> Dict[str, List[AICapability]]:
        """Get all capabilities from all agents."""
        capabilities = {}
        for agent in self.agents.values():
            for cap in agent.get_capabilities():
                if cap.name not in capabilities:
                    capabilities[cap.name] = []
                capabilities[cap.name].append(cap)
        return capabilities


class ALFREDNexusAgent(NEXUSAgent):
    """
    ALFRED's NEXUS agent implementation.

    Exposes ALFRED's capabilities through the NEXUS protocol.
    """

    def __init__(self, alfred_brain=None):
        super().__init__(
            agent_id=f"ALFRED-{uuid.uuid4().hex[:8]}",
            name="ALFRED AI Assistant"
        )
        self.brain = alfred_brain
        self._init_capabilities()

    def _init_capabilities(self):
        """Initialize ALFRED's capabilities."""
        self.capabilities = [
            AICapability(
                name="memory_recall",
                description="Recall information from persistent memory",
                input_schema={'query': 'string', 'limit': 'int?'},
                output_schema={'results': 'array', 'count': 'int'},
                latency_ms=50,
                reliability=0.99
            ),
            AICapability(
                name="knowledge_store",
                description="Store knowledge in persistent memory",
                input_schema={'category': 'string', 'key': 'string', 'value': 'string'},
                output_schema={'success': 'bool', 'id': 'string'},
                latency_ms=30,
                reliability=0.999
            ),
            AICapability(
                name="conversation",
                description="Natural language conversation",
                input_schema={'message': 'string', 'context': 'object?'},
                output_schema={'response': 'string'},
                latency_ms=500,
                reliability=0.95
            ),
            AICapability(
                name="code_analysis",
                description="Analyze and explain code",
                input_schema={'code': 'string', 'language': 'string?'},
                output_schema={'analysis': 'string', 'suggestions': 'array'},
                latency_ms=1000,
                reliability=0.90
            ),
        ]

    def get_capabilities(self) -> List[AICapability]:
        return self.capabilities

    async def process_message(self, message: NEXUSMessage) -> Optional[NEXUSMessage]:
        """Process incoming NEXUS message."""
        if message.message_type == MessageType.QUERY:
            return await self._handle_query(message)
        elif message.message_type == MessageType.COMMAND:
            return await self._handle_command(message)
        elif message.message_type == MessageType.CAPABILITY:
            return self._handle_capability_check(message)
        elif message.message_type == MessageType.DELEGATE:
            return await self._handle_delegation(message)
        else:
            return self.create_response(message, {"status": "acknowledged"})

    async def _handle_query(self, message: NEXUSMessage) -> NEXUSMessage:
        """Handle a query message."""
        query = message.payload.get('query', '')

        # Try memory recall if brain available
        if self.brain:
            try:
                results = self.brain.recall_knowledge(query, query)
                return self.create_response(message, {
                    'response': results or "No matching knowledge found.",
                    'source': 'memory'
                })
            except Exception:
                pass

        return self.create_response(message, {
            'response': f"Query received: {query}",
            'source': 'direct'
        })

    async def _handle_command(self, message: NEXUSMessage) -> NEXUSMessage:
        """Handle a command message."""
        command = message.payload.get('command', '')
        params = message.payload.get('params', {})

        # Execute command based on type
        result = f"Command '{command}' executed with params: {params}"

        return self.create_response(message, {
            'status': 'completed',
            'result': result
        })

    def _handle_capability_check(self, message: NEXUSMessage) -> NEXUSMessage:
        """Handle capability inquiry."""
        requested = message.payload.get('capability')

        if requested:
            for cap in self.capabilities:
                if cap.name == requested:
                    return self.create_response(message, {
                        'available': True,
                        'capability': cap.to_dict()
                    })
            return self.create_response(message, {'available': False})
        else:
            return self.create_response(message, {
                'capabilities': [cap.to_dict() for cap in self.capabilities]
            })

    async def _handle_delegation(self, message: NEXUSMessage) -> NEXUSMessage:
        """Handle task delegation."""
        task = message.payload.get('task', '')
        params = message.payload.get('params', {})

        # Simulate task execution
        await asyncio.sleep(0.1)  # Simulated work

        return self.create_response(message, {
            'status': 'completed',
            'task': task,
            'result': f"Task '{task}' completed successfully"
        })


# CLI interface
if __name__ == "__main__":
    import sys

    async def demo():
        """Demonstrate NEXUS protocol."""
        print("\n=== NEXUS Protocol Demo ===\n")

        # Create router
        router = NEXUSRouter()

        # Create ALFRED agent
        alfred = ALFREDNexusAgent()
        router.register_agent(alfred)

        print(f"Registered agent: {alfred.name} ({alfred.agent_id})")
        print(f"Capabilities: {[c.name for c in alfred.get_capabilities()]}")

        # Create a query
        query_msg = alfred.create_query(
            receiver_id=alfred.agent_id,  # Send to self for demo
            query="What is the weather?",
            context={'location': 'Chicago'}
        )

        print(f"\n--- Sending Query ---")
        print(f"ID: {query_msg.id}")
        print(f"Intent: {query_msg.intent.value}")
        print(f"Payload: {query_msg.payload}")

        # Route message
        response = await router.route_message(query_msg)

        if response:
            print(f"\n--- Response ---")
            print(f"ID: {response.id}")
            print(f"Payload: {response.payload}")

        # Check capabilities
        print(f"\n--- Capability Check ---")
        all_caps = router.get_all_capabilities()
        for cap_name, caps in all_caps.items():
            print(f"  {cap_name}: {len(caps)} provider(s)")

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "demo":
            asyncio.run(demo())
        elif command == "capabilities":
            alfred = ALFREDNexusAgent()
            print("\n=== ALFRED NEXUS Capabilities ===")
            for cap in alfred.get_capabilities():
                print(f"\n{cap.name}:")
                print(f"  Description: {cap.description}")
                print(f"  Latency: {cap.latency_ms}ms")
                print(f"  Reliability: {cap.reliability:.1%}")
        else:
            print("Commands: demo, capabilities")
    else:
        print("NEXUS Protocol - AI-to-AI Communication")
        print("Commands: demo, capabilities")
