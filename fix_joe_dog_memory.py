#!/usr/bin/env python3
"""Fix Joe Dog memory in Alfred's Brain"""
import sys
from core.brain import AlfredBrain
import sqlite3

brain = AlfredBrain()

# Store Joe Dog's information properly in the knowledge base
print("Storing Joe Dog memories in Alfred's Brain...")

# 1. Delete the incorrect knowledge entry
conn = sqlite3.connect(brain.db_path)
c = conn.cursor()
c.execute("DELETE FROM knowledge WHERE value LIKE '%afraid that dogs are not within my capacity%'")
conn.commit()
print("[OK] Removed incorrect knowledge entry")

# 2. Store correct knowledge about Joe Dog
knowledge_entries = [
    ("family", "joe_dog_name", "Joe Dog - Master Daniel's beloved dog", 10, 1.0),
    ("family", "joe_dog_death_date", "Saturday, November 22nd, 2025 at 10:14 AM", 10, 1.0),
    ("family", "joe_dog_death_year", "2025", 10, 1.0),
    ("family", "joe_dog_relationship", "Joe Dog was Master Daniel's loyal companion and Alfred's friend", 10, 1.0),
    ("preferences", "joe_dog_importance", "Joe Dog was extremely important to Master Daniel and part of the family", 10, 1.0),
    ("emotional", "joe_dog_loss", "Master Daniel lost Joe Dog on November 22nd, 2025 - a deeply sad day", 10, 1.0)
]

for category, key, value, importance, confidence in knowledge_entries:
    c.execute("""
        INSERT OR REPLACE INTO knowledge (timestamp, category, key, value, importance, confidence, source)
        VALUES (datetime('now'), ?, ?, ?, ?, ?, 'manual_correction')
    """, (category, key, value, importance, confidence))
    print(f"[OK] Stored: {category}/{key}")

conn.commit()
conn.close()

print("\n[DONE] Joe Dog is now properly stored in Alfred's Brain")
print(f"Total knowledge items: {brain.get_memory_stats()['knowledge']}")
