#!/usr/bin/env python3
"""
Alfred RAG - Research & Knowledge Assistant
Optimized for Retrieval Augmented Generation with semantic search

Features:
- RAG System (Vector Knowledge + LLM)
- Vector Knowledge Base (ChromaDB)
- Advanced Crawler (Crawl4AI)
- Ollama AI (local models)
- Fabric Patterns (243 patterns)
- Alfred Brain (persistent memory)
- Security Analysis
- Database Tools

Note: Voice features disabled due to protobuf compatibility

DEPENDENCY REQUIREMENTS:
To activate full RAG capabilities, run:
  pip install protobuf==5.29.3 transformers==4.47.1 --force-reinstall

To switch back to Voice mode, run:
  pip install parler-tts --upgrade
"""

import os
import sys

# Configure for RAG/Transformers compatibility
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("=" * 80)
print("ALFRED RAG - Research & Knowledge Assistant")
print("PATENT PENDING - AI Memory & Learning System")
print("=" * 80)
print()
print("Optimized for: RAG (Retrieval Augmented Generation)")
print()

# Import Alfred Brain
from alfred_brain import AlfredBrain

# Try to import RAG modules
RAG_AVAILABLE = False
VECTOR_KB_AVAILABLE = False

try:
    from rag_module import RAGSystem
    RAG_AVAILABLE = True
    print("[OK] RAG System: Ready")
except ImportError as e:
    print(f"[WARNING] RAG System: Not Available")
    print(f"         Reason: {str(e)[:100]}")
    print("         To fix: pip install protobuf==5.29.3 transformers==4.47.1 --force-reinstall")

try:
    from vector_knowledge import VectorKnowledgeBase, DocumentChunker
    VECTOR_KB_AVAILABLE = True
    print("[OK] Vector Knowledge Base: Ready")
except ImportError as e:
    print(f"[WARNING] Vector KB: Not Available")
    print(f"         Reason: {str(e)[:100]}")

# Try to import Advanced Crawler
try:
    from crawler_advanced import AdvancedCrawler
    CRAWLER_AVAILABLE = True
    print("[OK] Advanced Crawler: Ready")
except ImportError:
    CRAWLER_AVAILABLE = False
    print("[WARNING] Advanced Crawler: Not Available")

# Initialize Alfred Brain
alfred = AlfredBrain()
print(f"[OK] Alfred Brain: {len(alfred.context_cache)} conversations, {len(alfred.knowledge_cache)} knowledge items")

# Initialize RAG if available
rag = None
if RAG_AVAILABLE:
    try:
        rag = RAGSystem()
        print("[OK] RAG System: Initialized")
    except Exception as e:
        print(f"[WARNING] RAG initialization failed: {e}")
        rag = None

# Initialize Vector KB if available
vector_kb = None
if VECTOR_KB_AVAILABLE and not rag:
    try:
        vector_kb = VectorKnowledgeBase()
        print("[OK] Vector KB: Initialized standalone")
    except Exception as e:
        print(f"[WARNING] Vector KB initialization failed: {e}")
        vector_kb = None

print()
print("=" * 80)
print("Alfred RAG is ready!")
print()

if RAG_AVAILABLE:
    print("RAG Commands Available:")
    print("  rag.research_url('https://...')          - Research a URL")
    print("  rag.ask_question('question')             - Ask about stored knowledge")
    print("  rag.add_knowledge('text', metadata={})   - Add to knowledge base")
    print()

if VECTOR_KB_AVAILABLE:
    print("Vector KB Commands Available:")
    print("  vector_kb.store_document(text, metadata) - Store document")
    print("  vector_kb.search(query, k=5)             - Semantic search")
    print("  vector_kb.get_stats()                    - Knowledge base stats")
    print()

print("Alfred Brain Commands:")
print("  alfred.store_conversation(user, response)  - Save conversation")
print("  alfred.get_conversation_context(limit=5)   - Get recent context")
print("  alfred.store_knowledge(cat, key, val)      - Store knowledge")
print("  alfred.recall_knowledge(cat, key)          - Recall knowledge")
print()
print("Capabilities:")
print(f"  [{'+'  if RAG_AVAILABLE else '-'}] RAG System (Retrieval + LLM)")
print(f"  [{'+'  if VECTOR_KB_AVAILABLE else '-'}] Vector Knowledge Base (Semantic Search)")
print(f"  [{'+'  if CRAWLER_AVAILABLE else '-'}] Advanced Crawler (Web Research)")
print("  [+] Ollama AI (Local Models)")
print("  [+] Fabric Patterns (243 patterns)")
print("  [+] Alfred Brain (Memory)")
print("  [+] Security Analysis")
print("  [+] Database Tools")
print("  [-] Voice Output (use Alfred LIVE for this)")
print()
print("=" * 80)
print()

# Interactive mode
if __name__ == "__main__":
    if RAG_AVAILABLE:
        print("Starting in interactive RAG mode...")
        print("Commands: research <url>, ask <question>, store <text>, quit")
        print()

        while True:
            try:
                user_input = input("\n[RAG Command]: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Parse command
                if user_input.startswith("research "):
                    url = user_input[9:].strip()
                    print(f"Researching: {url}")
                    # result = await rag.research_url(url)
                    print("Note: Use rag.research_url(url) in async context")

                elif user_input.startswith("ask "):
                    question = user_input[4:].strip()
                    print(f"Question: {question}")
                    # answer = await rag.ask_question(question)
                    print("Note: Use rag.ask_question(q) in async context")

                elif user_input.startswith("store "):
                    text = user_input[6:].strip()
                    if vector_kb:
                        vector_kb.store_document(text, {"source": "manual"})
                        print("Stored in vector knowledge base")
                    else:
                        print("Vector KB not available")

                else:
                    print("Unknown command. Try: research <url>, ask <question>, store <text>")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("RAG not available. Check dependency requirements above.")
        print()
        print("Import alfred_rag in your code to use available features:")
        print("  from alfred_rag import alfred, rag, vector_kb")
        print()
        print("Example async usage:")
        print("  import asyncio")
        print("  result = await rag.research_url('https://example.com')")
        print("  answer = await rag.ask_question('What is...?')")
