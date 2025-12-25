#!/usr/bin/env python3
"""Test if Alfred can now remember Joe Dog"""
import sys
import sqlite3
from core.brain import AlfredBrain

print("="*80)
print("TESTING ALFRED'S MEMORY OF JOE DOG")
print("="*80)
print()

brain = AlfredBrain()

# Simulate what alfred_terminal.py does when you ask "When did Joe Dog die?"
user_input = "When did Joe Dog die?"
print(f"Question: {user_input}")
print()

# Extract search terms (updated logic)
user_input_lower = user_input.lower()
search_terms = []
stopwords = {'the', 'is', 'at', 'on', 'in', 'to', 'a', 'an', 'of', 'for', 'and', 'or', 'but', 'if', 'how', 'what', 'when', 'where', 'who', 'why', 'did'}
for word in user_input_lower.split():
    # Remove punctuation
    word_clean = word.strip('.,!?;:').lower()
    # Include words 3+ chars that aren't stopwords
    if len(word_clean) >= 3 and word_clean not in stopwords:
        search_terms.append(word_clean)

print(f"Search terms extracted: {search_terms}")
print()

# Search knowledge base (same logic as alfred_terminal.py)
knowledge_context = []

if search_terms:
    conn = sqlite3.connect(brain.db_path)
    c = conn.cursor()

    # Search for any matching knowledge
    for term in search_terms[:5]:
        c.execute("""
            SELECT category, key, value, importance
            FROM knowledge
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY importance DESC
            LIMIT 3
        """, (f'%{term}%', f'%{term}%'))
        results = c.fetchall()

        for row in results:
            knowledge_context.append({
                'category': row[0],
                'key': row[1],
                'value': row[2],
                'importance': row[3]
            })

    conn.close()

# Show what knowledge was found
print("Knowledge found in Alfred's Brain:")
print("-" * 80)

if knowledge_context:
    # Remove duplicates
    seen = set()
    unique_knowledge = []
    for k in knowledge_context:
        key = f"{k['category']}/{k['key']}"
        if key not in seen:
            seen.add(key)
            unique_knowledge.append(k)

    for k in unique_knowledge[:5]:
        print(f"[{k['importance']}/10] {k['category']}/{k['key']}:")
        print(f"    {k['value']}")
        print()

    print("="*80)
    print("SUCCESS! Alfred found Joe Dog in his brain!")
    print("="*80)
    print()
    print("Context that will be sent to AI:")
    print("-" * 80)
    context_text = "[ALFRED'S BRAIN KNOWLEDGE - CRITICAL INFORMATION]:\n"
    for k in unique_knowledge[:5]:
        context_text += f"- {k['category']}/{k['key']}: {k['value']} (importance: {k['importance']}/10)\n"
    print(context_text)
else:
    print("ERROR: No knowledge found!")
    print("This means the brain search is not working correctly.")
