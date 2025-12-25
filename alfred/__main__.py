"""
Alfred Module Entry Point
Run Alfred as a Python module: python -m alfred

Usage:
    python -m alfred              # Interactive chat mode
    python -m alfred --help       # Show help
    python -m alfred --stats      # Show memory statistics
    python -m alfred --version    # Show version

Author: Daniel J Rita (BATDAN)
"""

import sys
import argparse
from alfred import Alfred, __version__


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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Alfred - 100% Local AI Assistant with Permanent Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m alfred              # Interactive chat mode
  python -m alfred --stats      # Show memory statistics
  python -m alfred --version    # Show version

Alfred is a privacy-first AI assistant that runs 100% locally using Ollama.
All conversations are permanently stored in a patent-pending 11-table memory system.

No API key required. No cloud. No data sharing.
        """
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show memory statistics and exit'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'Alfred v{__version__}'
    )

    args = parser.parse_args()

    # Execute command
    try:
        if args.stats:
            show_stats()
        else:
            interactive_mode()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
