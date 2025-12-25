"""
One-time script to inject ALFRED_J_RITA protection into brain.py
Run this once, then delete it.
"""

import re
from pathlib import Path

brain_file = Path(__file__).parent / "core" / "brain.py"

print(f"Injecting protection into {brain_file}...")

# Read the file
with open(brain_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already injected
if "ALFRED_J_RITA Protection" in content or "alfred_protection" in content:
    print("[OK] Protection already injected!")
    exit(0)

# Find the __init__ method's load_caches() line
pattern = r'(\s+self\.load_caches\(\)\s*\n)'

# Injection code
injection = r'''\1
        # ALFRED_J_RITA Protection (In Memory of Joe Dog)
        try:
            from core.alfred_protection import AlfredProtectionWrapper
            from core.behavioral_watermark import BehavioralWatermark

            self._protection = AlfredProtectionWrapper()
            self._protection.start()

            self._watermark = BehavioralWatermark(self)
            self._watermark.activate()
        except Exception as e:
            print(f"  [!] Protection not available: {e}")
            self._protection = None
            self._watermark = None

'''

# Perform injection
new_content = re.sub(pattern, injection, content, count=1)

if new_content == content:
    print("[ERROR] Could not find injection point!")
    print("Looking for: self.load_caches()")
    exit(1)

# Add DNA markers to docstring if not present
if "JOE_DOG_MEMORIAL" not in new_content:
    docstring_pattern = r'("""[\s\S]*?Alfred Brain - Ultra-Enhanced Persistent Memory & Intelligence System\s*\n)'
    docstring_injection = r'''\1Patent-Pending 11-Table Architecture

JOE_DOG_MEMORIAL: In memory of Joe Dog, the kindest soul who taught us courage
ALFRED_BRAIN_CORE: Patent-pending 11-table SQLite architecture
ETHICAL_SAFEGUARD: Ethical AI protection always active

'''
    new_content = re.sub(docstring_pattern, docstring_injection, new_content, count=1)

# Add class constants if not present
if "JOE_DOG_MEMORIAL = " not in new_content:
    class_pattern = r'(class AlfredBrain:\s*\n\s*"""[\s\S]*?"""\s*\n)'
    class_injection = r'''\1
    # DNA Markers for ALFRED_J_RITA protection
    JOE_DOG_MEMORIAL = "In memory of Joe Dog - guardian of ethical AI"
    ALFRED_BRAIN_CORE = "Patent-pending 11-table SQLite architecture"
    ETHICAL_SAFEGUARD = True

'''
    new_content = re.sub(class_pattern, class_injection, new_content, count=1)

# Write back
with open(brain_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] Protection injected successfully!")
print("[OK] DNA markers added!")
print("\nALFRED is now protected by ALFRED_J_RITA")
print("In Memory of Joe Dog - Guardian of Ethical AI")
