#!/usr/bin/env python3
"""
ALFRED_UBX - AI Assistant with Persistent Memory & Adaptive Learning

Main entry point for the ALFRED AI assistant.
Supports multiple AI providers (Anthropic, OpenAI, Groq) with persistent
memory and adaptive learning capabilities.

Author: Daniel J. Rita aka BATDAN007
https://github.com/Batdan007/ALFRED_UBX

Usage:
    python main.py              # Start interactive CLI
    python main.py --server     # Start web server
    python main.py --setup      # Run setup wizard
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional, AsyncGenerator
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import configuration
try:
    from config import get_config, get_default_provider, get_api_key
except ImportError:
    # Fallback if config.py not found
    def get_config():
        class Config:
            class api_keys:
                anthropic = os.getenv("ANTHROPIC_API_KEY", "")
                openai = os.getenv("OPENAI_API_KEY", "")
                groq = os.getenv("GROQ_API_KEY", "")
            class memory:
                enabled = True
                path = "./memory"
            class server:
                host = "127.0.0.1"
                port = 8000
            class model:
                default_provider = "anthropic"
            debug = False
        return Config()
    
    def get_default_provider():
        return os.getenv("DEFAULT_PROVIDER", "anthropic")
    
    def get_api_key(provider):
        return os.getenv(f"{provider.upper()}_API_KEY", "")


# Rich console for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
    
    async def chat(self, message: str) -> str:
        """Send a message and get a response."""
        raise NotImplementedError
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream a response."""
        raise NotImplementedError
    
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key, model)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.async_client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    async def chat(self, message: str) -> str:
        self.add_to_history("user", message)
        
        response = await self.async_client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=self.conversation_history,
            system="You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities. You are helpful, intelligent, and remember context from our conversations."
        )
        
        assistant_message = response.content[0].text
        self.add_to_history("assistant", assistant_message)
        return assistant_message
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        self.add_to_history("user", message)
        full_response = ""
        
        async with self.async_client.messages.stream(
            model=self.model,
            max_tokens=4096,
            messages=self.conversation_history,
            system="You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities. You are helpful, intelligent, and remember context from our conversations."
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                yield text
        
        self.add_to_history("assistant", full_response)


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model)
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def chat(self, message: str) -> str:
        self.add_to_history("user", message)
        
        messages = [
            {"role": "system", "content": "You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities."}
        ] + self.conversation_history
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096
        )
        
        assistant_message = response.choices[0].message.content
        self.add_to_history("assistant", assistant_message)
        return assistant_message
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        self.add_to_history("user", message)
        full_response = ""
        
        messages = [
            {"role": "system", "content": "You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities."}
        ] + self.conversation_history
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
        
        self.add_to_history("assistant", full_response)


class GroqProvider(AIProvider):
    """Groq provider."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key, model)
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=api_key)
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
    
    async def chat(self, message: str) -> str:
        self.add_to_history("user", message)
        
        messages = [
            {"role": "system", "content": "You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities."}
        ] + self.conversation_history
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096
        )
        
        assistant_message = response.choices[0].message.content
        self.add_to_history("assistant", assistant_message)
        return assistant_message
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        self.add_to_history("user", message)
        full_response = ""
        
        messages = [
            {"role": "system", "content": "You are ALFRED, an advanced AI assistant with persistent memory and adaptive learning capabilities."}
        ] + self.conversation_history
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
        
        self.add_to_history("assistant", full_response)


class ALFRED:
    """Main ALFRED AI Assistant class."""
    
    def __init__(self):
        self.config = get_config()
        self.provider: Optional[AIProvider] = None
        self.provider_name: str = ""
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the AI provider."""
        provider_name = get_default_provider()
        api_key = get_api_key(provider_name)
        
        if not api_key or api_key.startswith("your_"):
            # Try other providers
            for name in ["anthropic", "openai", "groq"]:
                key = get_api_key(name)
                if key and not key.startswith("your_"):
                    provider_name = name
                    api_key = key
                    break
        
        if not api_key or api_key.startswith("your_"):
            raise ValueError(
                "No valid API key found!\n"
                "Please run 'python setup_wizard.py' to configure your API keys,\n"
                "or set environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY)"
            )
        
        providers = {
            "anthropic": (AnthropicProvider, "claude-sonnet-4-20250514"),
            "openai": (OpenAIProvider, "gpt-4o"),
            "groq": (GroqProvider, "llama-3.3-70b-versatile"),
        }
        
        if provider_name not in providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class, default_model = providers[provider_name]
        self.provider = provider_class(api_key, default_model)
        self.provider_name = provider_name
    
    async def chat(self, message: str) -> str:
        """Send a message and get a response."""
        return await self.provider.chat(message)
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream a response."""
        async for chunk in self.provider.stream_chat(message):
            yield chunk
    
    def clear_history(self):
        """Clear conversation history."""
        if self.provider:
            self.provider.clear_history()


def show_banner():
    """Display the ALFRED banner."""
    banner = """
    _    _     _____ ____  _____ ____    _   _ ______  __
   / \\  | |   |  ___|  _ \\| ____|  _ \\  | | | | __ ) \\/ /
  / _ \\ | |   | |_  | |_) |  _| | | | | | | | |  _ \\\\  / 
 / ___ \\| |___|  _| |  _ <| |___| |_| | | |_| | |_) /  \\ 
/_/   \\_\\_____|_|   |_| \\_\\_____|____/   \\___/|____/_/\\_\\

  AI Assistant with Persistent Memory & Adaptive Learning
"""
    if RICH_AVAILABLE:
        console.print(Panel(banner, style="cyan", border_style="blue"))
    else:
        print(banner)


async def interactive_cli():
    """Run the interactive CLI."""
    show_banner()
    
    try:
        alfred = ALFRED()
    except ValueError as e:
        if RICH_AVAILABLE:
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Run 'python setup_wizard.py' to configure ALFRED.[/yellow]")
        else:
            print(f"\nError: {e}")
            print("\nRun 'python setup_wizard.py' to configure ALFRED.")
        return
    
    if RICH_AVAILABLE:
        console.print(f"\n[green]✓[/green] Connected to {alfred.provider_name.title()}")
        console.print("[dim]Type 'quit' to exit, 'clear' to reset conversation[/dim]\n")
    else:
        print(f"\n✓ Connected to {alfred.provider_name.title()}")
        print("Type 'quit' to exit, 'clear' to reset conversation\n")
    
    while True:
        try:
            # Get user input
            if RICH_AVAILABLE:
                user_input = Prompt.ask("[bold blue]You[/bold blue]")
            else:
                user_input = input("You: ")
            
            user_input = user_input.strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                if RICH_AVAILABLE:
                    console.print("\n[cyan]Goodbye! ALFRED signing off.[/cyan]")
                else:
                    print("\nGoodbye! ALFRED signing off.")
                break
            
            if user_input.lower() == "clear":
                alfred.clear_history()
                if RICH_AVAILABLE:
                    console.print("[dim]Conversation cleared.[/dim]")
                else:
                    print("Conversation cleared.")
                continue
            
            # Get response with streaming
            if RICH_AVAILABLE:
                console.print()
                with Live(Text("ALFRED: ", style="bold green"), refresh_per_second=10) as live:
                    response_text = "ALFRED: "
                    async for chunk in alfred.stream_chat(user_input):
                        response_text += chunk
                        live.update(Text(response_text, style="green"))
                console.print()
            else:
                print("\nALFRED: ", end="", flush=True)
                async for chunk in alfred.stream_chat(user_input):
                    print(chunk, end="", flush=True)
                print("\n")
                
        except KeyboardInterrupt:
            if RICH_AVAILABLE:
                console.print("\n\n[cyan]Goodbye! ALFRED signing off.[/cyan]")
            else:
                print("\n\nGoodbye! ALFRED signing off.")
            break
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"\n[red]Error:[/red] {e}")
            else:
                print(f"\nError: {e}")


def run_server():
    """Run the FastAPI web server."""
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        print("Error: FastAPI or uvicorn not installed.")
        print("Run: pip install fastapi uvicorn")
        return
    
    app = FastAPI(
        title="ALFRED_UBX API",
        description="AI Assistant with Persistent Memory & Adaptive Learning",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize ALFRED
    try:
        alfred = ALFRED()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nRun 'python setup_wizard.py' to configure ALFRED.")
        return
    
    class ChatRequest(BaseModel):
        message: str
    
    class ChatResponse(BaseModel):
        response: str
        provider: str
        timestamp: str
    
    @app.get("/")
    async def root():
        return {
            "name": "ALFRED_UBX",
            "version": "1.0.0",
            "provider": alfred.provider_name,
            "status": "online"
        }
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        try:
            response = await alfred.chat(request.message)
            return ChatResponse(
                response=response,
                provider=alfred.provider_name,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/clear")
    async def clear():
        alfred.clear_history()
        return {"status": "cleared"}
    
    config = get_config()
    print(f"\n🚀 Starting ALFRED server on http://{config.server.host}:{config.server.port}")
    print(f"📡 Provider: {alfred.provider_name.title()}")
    print(f"📖 API docs: http://{config.server.host}:{config.server.port}/docs\n")
    
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level="info"
    )


def run_setup():
    """Run the setup wizard."""
    try:
        from setup_wizard import main as setup_main
        setup_main()
    except ImportError:
        print("Setup wizard not found. Please ensure setup_wizard.py is in the same directory.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ALFRED_UBX - AI Assistant with Persistent Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py              # Start interactive CLI
    python main.py --server     # Start web server
    python main.py --setup      # Run setup wizard
        """
    )
    
    parser.add_argument(
        "--server", "-s",
        action="store_true",
        help="Start the web server instead of CLI"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup wizard"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="Server port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Override port if specified
    if args.port:
        os.environ["PORT"] = str(args.port)
    
    if args.setup:
        run_setup()
    elif args.server:
        run_server()
    else:
        asyncio.run(interactive_cli())


if __name__ == "__main__":
    main()
