"""
Advanced Alfred Usage Example

Demonstrates all features of the Alfred Python API:
- Conversation with memory
- Knowledge recall
- Topic tracking
- Memory statistics
- Memory export

Author: Daniel J Rita (BATDAN)
"""

from alfred import Alfred

def main():
    # Initialize Alfred
    print("Initializing Alfred...")
    bot = Alfred()

    print("\n" + "=" * 60)
    print("Alfred Advanced Usage Example")
    print("=" * 60)
    print(f"\nAlfred Status: {bot}\n")

    # Example 1: Simple conversation
    print("Example 1: Simple Conversation")
    print("-" * 60)
    response = bot.respond("What's the capital of France?")
    print(f"Alfred: {response}\n")

    # Example 2: Follow-up (tests memory)
    print("Example 2: Follow-up Question (Testing Memory)")
    print("-" * 60)
    response = bot.respond("What did I just ask you about?")
    print(f"Alfred: {response}\n")

    # Example 3: Memory statistics
    print("Example 3: Memory Statistics")
    print("-" * 60)
    stats = bot.get_memory_stats()
    print(f"Total Conversations: {stats.get('conversations', 0)}")
    print(f"Knowledge Items: {stats.get('knowledge', 0)}")
    print(f"Learned Patterns: {stats.get('patterns', 0)}")
    print(f"Tracked Topics: {stats.get('topics', 0)}")
    print(f"Skill Proficiencies: {stats.get('skills', 0)}")
    print(f"Average Importance: {stats.get('avg_importance', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0)}%\n")

    # Example 4: Topics
    print("Example 4: Conversation Topics")
    print("-" * 60)
    topics = bot.get_topics()
    if topics:
        for topic in topics[:5]:  # Top 5 topics
            print(f"  - {topic['topic_name']} (frequency: {topic['frequency']})")
    else:
        print("  No topics tracked yet")
    print()

    # Example 5: Export memory
    print("Example 5: Export Memory")
    print("-" * 60)
    backup_path = bot.export_memory()
    print(f"Memory exported to: {backup_path}\n")

    print("=" * 60)
    print("Advanced usage demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
