"""
Alfred Module Entry Point
Run Alfred as a Python module: python -m alfred

Usage:
    alfred                    # Full terminal mode (default)
    alfred --voice            # Voice mode with full brain
    alfred --stats            # Show memory statistics
    alfred --version          # Show version

After installing with: pip install -e .
Just type 'alfred' anywhere!

Author: Daniel J Rita (BATDAN)
"""

import sys
import argparse
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from alfred import Alfred, __version__
except ImportError:
    Alfred = None
    __version__ = "3.0.0"


def interactive_mode():
    """Run Alfred in interactive chat mode"""
    print("=" * 60)
    print("Alfred Interactive Mode")
    print("100% Local AI with Permanent Memory")
    print("=" * 60)

    # Initialize Alfred
    print("\nInitializing Alfred...")
    bot = Alfred()

    print(f"\n{bot}")
    print("\nType 'exit' or 'quit' to end conversation")
    print("Type 'stats' to see memory statistics")
    print("Type 'topics' to see conversation topics")
    print("=" * 60)
    print()

    # Chat loop
    while True:
        try:
            user_msg = input("You: ").strip()

            if not user_msg:
                continue

            # Commands
            if user_msg.lower() in {"exit", "quit", "bye"}:
                print("\nAlfred: Very well, sir. Until next time.")
                break

            elif user_msg.lower() == "stats":
                stats = bot.get_memory_stats()
                print("\n--- Memory Statistics ---")
                print(f"Conversations: {stats.get('conversations', 0)}")
                print(f"Knowledge Items: {stats.get('knowledge', 0)}")
                print(f"Topics: {stats.get('topics', 0)}")
                print(f"Skills: {stats.get('skills', 0)}")
                print(f"Patterns: {stats.get('patterns', 0)}")
                print(f"Avg Importance: {stats.get('avg_importance', 0)}")
                print(f"Success Rate: {stats.get('success_rate', 0)}%")
                print()
                continue

            elif user_msg.lower() == "topics":
                topics = bot.get_topics()
                if topics:
                    print("\n--- Top Topics ---")
                    for topic in topics[:10]:
                        print(f"  {topic['topic_name']}: {topic['frequency']} times")
                    print()
                else:
                    print("\nNo topics tracked yet.\n")
                continue

            # Normal conversation
            response = bot.respond(user_msg)
            print(f"Alfred: {response}\n")

        except KeyboardInterrupt:
            print("\n\nAlfred: Interrupted. Goodbye, sir.")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def show_stats():
    """Show Alfred's memory statistics"""
    bot = Alfred()
    stats = bot.get_memory_stats()

    print("\n" + "=" * 60)
    print("Alfred Memory Statistics")
    print("=" * 60)
    print(f"Conversations: {stats.get('conversations', 0)}")
    print(f"Knowledge Items: {stats.get('knowledge', 0)}")
    print(f"Preferences: {stats.get('preferences', 0)}")
    print(f"Patterns: {stats.get('patterns', 0)}")
    print(f"Skills: {stats.get('skills', 0)}")
    print(f"Topics: {stats.get('topics', 0)}")
    print(f"Mistakes (learned): {stats.get('mistakes', 0)}")
    print(f"\nAverage Importance: {stats.get('avg_importance', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0)}%")
    print(f"Average Skill Proficiency: {stats.get('avg_skill_proficiency', 0)}")
    print("=" * 60)


def voice_mode():
    """Run Alfred in voice mode with full brain integration"""
    try:
        from alfred_voice_mode import AlfredVoiceMode
        alfred = AlfredVoiceMode()
        return alfred.run()
    except ImportError as e:
        print(f"Voice mode not available: {e}")
        print("Run: python setup_voice.py")
        return 1


def terminal_mode():
    """Run Alfred full terminal (like claude code)"""
    try:
        from alfred_terminal import AlfredTerminal
        terminal = AlfredTerminal()
        terminal.run()
        return 0
    except ImportError as e:
        print(f"Terminal mode error: {e}")
        # Fall back to basic interactive mode
        interactive_mode()
        return 0


def main():
    """Main entry point - type 'alfred' anywhere after install"""
    parser = argparse.ArgumentParser(
        description="ALFRED - AI Butler Assistant (American with British accent)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  alfred                  # Full terminal mode (Ollama default)
  alfred --voice          # Voice mode - hands-free conversation
  alfred --cloud          # Enable cloud AI (Claude, OpenAI, etc.)
  alfred --local          # Force local-only (maximum privacy)
  alfred --voice --cloud  # Voice with cloud AI fallback
  alfred --stats          # Show memory statistics

Privacy Modes:
  --local   Ollama only (100% private, no internet)
  --cloud   Enable cloud providers when Ollama unavailable
  (default) Try Ollama first, ask before using cloud

Patent-pending technology by Daniel J Rita (BATDAN).
        """
    )

    parser.add_argument(
        '--voice', '-v',
        action='store_true',
        help='Voice mode - hands-free with full brain'
    )

    parser.add_argument(
        '--simple', '-s',
        action='store_true',
        help='Simple chat mode (no terminal UI)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show memory statistics and exit'
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run setup to install voice dependencies'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'ALFRED v{__version__}'
    )

    parser.add_argument(
        '--cloud', '-c',
        action='store_true',
        help='Enable cloud AI providers (Claude, OpenAI, Groq, Gemini)'
    )

    parser.add_argument(
        '--local', '-l',
        action='store_true',
        help='Force local-only mode (Ollama only, maximum privacy)'
    )

    args = parser.parse_args()

    # Set environment variables for privacy mode
    if args.cloud:
        os.environ['ALFRED_PRIVACY_MODE'] = 'cloud'
    elif args.local:
        os.environ['ALFRED_PRIVACY_MODE'] = 'local'

    # Execute command
    try:
        if args.setup:
            import subprocess
            subprocess.run([sys.executable, "setup_voice.py"])
            return 0

        elif args.stats:
            show_stats()
            return 0

        elif args.voice:
            return voice_mode()

        elif args.simple:
            interactive_mode()
            return 0

        else:
            # Default: full terminal mode
            return terminal_mode()

    except KeyboardInterrupt:
        print("\n\nAlfred: Goodbye, sir.")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
