"""
Simple Chat Example - Using Alfred as a Python Library

This demonstrates how to use Alfred programmatically in your Python projects.

Usage:
    python examples/simple_chat.py

Features:
- 100% local AI (no API key needed)
- Permanent memory (Alfred remembers everything)
- Privacy-first (no cloud, no data sharing)
"""

from alfred import Alfred  # Import Alfred

# Initialize Alfred (no API key needed - uses local Ollama)
bot = Alfred()

print("=" * 60)
print("Alfred Chat Interface")
print("=" * 60)
print(f"Alfred Status: {bot}")
print("Type 'exit' or 'quit' to end conversation")
print("=" * 60)
print()

# Simple chat loop
while True:
    user_msg = input("You: ")

    if user_msg.lower() in {"exit", "quit"}:
        print("\nAlfred: Very well, sir. Until next time.")
        break

    # Get response from Alfred
    response = bot.respond(user_msg)
    print(f"Alfred: {response}\n")
