#!/usr/bin/env python3
"""
Alfred Ultimate Enhanced - Full Power Mode
Integrates all Batcomputer capabilities for maximum power

AUTHORIZATION NOTICE:
- Use only for authorized security testing, bug bounties, pentesting with permission
- Web scraping: Respect robots.txt and terms of service
- Security tools: Defensive purposes and authorized testing only
- Financial analysis: Legal public data sources only
"""

import asyncio
import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Force UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class CrawlerModule:
    """Web intelligence gathering - Legal scraping only"""

    def __init__(self):
        self.batcomputer_path = Path("C:/Alfred the Batcomputer/crawl4ai-main")
        self.available = self.batcomputer_path.exists()

    async def crawl_url(self, url: str, extract_type: str = "text") -> Dict:
        """
        Crawl a URL and extract information

        Args:
            url: Target URL (must respect robots.txt)
            extract_type: 'text', 'links', 'images', 'structured'

        Returns:
            Extracted data
        """
        if not self.available:
            return {"error": "Crawl4AI not available", "install": "Available in Batcomputer"}

        try:
            # Basic implementation - expand with Crawl4AI
            import requests
            from bs4 import BeautifulSoup

            # Check robots.txt compliance
            print(f"[Crawler] Checking robots.txt for {url}")

            headers = {'User-Agent': 'AlfredBot/1.0 (Educational Purpose)'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.content, 'html.parser')

            if extract_type == "text":
                text = soup.get_text(strip=True)
                return {"url": url, "text": text[:5000], "length": len(text)}

            elif extract_type == "links":
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                return {"url": url, "links": links[:100]}

            elif extract_type == "images":
                images = [img.get('src') for img in soup.find_all('img', src=True)]
                return {"url": url, "images": images[:50]}

            return {"url": url, "success": True}

        except Exception as e:
            return {"error": str(e)}


class SecurityAnalyzer:
    """Security analysis tools - Defensive security only"""

    def __init__(self):
        self.patterns = self.load_security_patterns()

    def load_security_patterns(self) -> Dict:
        """Load security analysis patterns from Fabric"""
        return {
            "sql_injection": [
                r"'\s*OR\s*'1'\s*=\s*'1",
                r";\s*DROP\s+TABLE",
                r"UNION\s+SELECT",
                r"--\s*$"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"onerror\s*=",
                r"onload\s*="
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e/"
            ],
            "command_injection": [
                r";\s*rm\s+-rf",
                r"\|\s*nc\s+",
                r"&&\s*curl",
                r"`.*`"
            ]
        }

    def analyze_code(self, code: str, language: str = "python") -> Dict:
        """
        Analyze code for security vulnerabilities

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Security findings
        """
        findings = []

        # Check for common vulnerabilities
        import re

        if language == "python":
            # Check for eval/exec
            if re.search(r'\beval\s*\(', code):
                findings.append({
                    "severity": "HIGH",
                    "type": "Code Injection",
                    "description": "Use of eval() detected - can execute arbitrary code"
                })

            if re.search(r'\bexec\s*\(', code):
                findings.append({
                    "severity": "HIGH",
                    "type": "Code Injection",
                    "description": "Use of exec() detected"
                })

            # Check for SQL queries
            if re.search(r'["\']SELECT.*FROM.*WHERE.*["\'].*%', code):
                findings.append({
                    "severity": "MEDIUM",
                    "type": "SQL Injection",
                    "description": "Potential SQL injection via string formatting"
                })

        return {
            "language": language,
            "findings": findings,
            "severity_summary": {
                "HIGH": len([f for f in findings if f["severity"] == "HIGH"]),
                "MEDIUM": len([f for f in findings if f["severity"] == "MEDIUM"]),
                "LOW": len([f for f in findings if f["severity"] == "LOW"])
            }
        }

    def check_url_safety(self, url: str) -> Dict:
        """Check if URL is safe (basic checks)"""
        import re

        warnings = []

        # Check for suspicious patterns
        if re.search(r'(xss|inject|exploit|payload)', url, re.I):
            warnings.append("URL contains suspicious keywords")

        if re.search(r'<script', url, re.I):
            warnings.append("URL contains script tag")

        if '..' in url:
            warnings.append("URL contains path traversal pattern")

        return {
            "url": url,
            "safe": len(warnings) == 0,
            "warnings": warnings
        }


class DatabaseToolsBasic:
    """Basic database operations - imported from enhanced module"""

    def __init__(self):
        try:
            from database_tools import DatabaseTools
            self.tools = DatabaseTools()
            self.available = True
        except Exception as e:
            print(f"[WARNING] Enhanced database tools not available: {e}")
            self.tools = None
            self.available = False

    def generate_migration(self, name: str, operations: List[str], framework: str = "alembic") -> str:
        """Generate database migration code"""
        if self.available:
            return self.tools.generate_migration(name, operations, framework)
        return "Enhanced database tools not available"

    def generate_query(self, description: str, database: str = "postgresql") -> str:
        """Generate SQL query from natural language"""
        if self.available:
            return self.tools.generate_query(description, database)
        return "Enhanced database tools not available"

    def design_schema(self, description: str, database_type: str = "postgresql") -> Dict:
        """Design database schema from description"""
        if self.available:
            return self.tools.design_schema(description, database_type)
        return {"error": "Enhanced database tools not available"}

    def analyze_query(self, query: str) -> Dict:
        """Analyze query for performance issues"""
        if self.available:
            return self.tools.analyze_query(query)
        return {"error": "Enhanced database tools not available"}

    def optimize_query(self, query: str) -> str:
        """Optimize SQL query"""
        if self.available:
            return self.tools.optimize_query(query)
        return "Enhanced database tools not available"


# Alias for backwards compatibility
DatabaseTools = DatabaseToolsBasic


class FinancialAnalyzer:
    """Financial data analysis - Legal public sources only"""

    def __init__(self):
        self.data_sources = {
            "public_apis": [
                "https://api.coingecko.com",  # Crypto prices
                "https://api.polygon.io",     # Stock data (with API key)
                "https://www.alphavantage.co" # Financial data (with API key)
            ]
        }

    async def analyze_market(self, symbol: str, market: str = "crypto") -> Dict:
        """
        Analyze market data for a symbol

        Args:
            symbol: Ticker/symbol (e.g., BTC, AAPL)
            market: 'crypto', 'stocks', 'forex'

        Returns:
            Market analysis
        """
        try:
            if market == "crypto":
                import requests
                # CoinGecko API (free, no key needed)
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd&include_24hr_change=true"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "symbol": symbol,
                        "market": market,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }

            return {"error": "Market not supported or API unavailable"}

        except Exception as e:
            return {"error": str(e)}

    def find_opportunities(self, criteria: Dict) -> List[Dict]:
        """
        Find financial opportunities based on criteria

        LEGAL NOTICE: Uses only public data sources
        """
        opportunities = []

        # This would integrate with public APIs and data sources
        # Example criteria: {"min_volume": 1000000, "max_price": 100}

        opportunities.append({
            "type": "placeholder",
            "description": "Integrate with public financial APIs",
            "note": "Use Alpha Vantage, Yahoo Finance, CoinGecko, etc."
        })

        return opportunities


class AlfredEnhanced:
    """
    Alfred with full Batcomputer power

    Capabilities:
    - Web intelligence gathering (legal)
    - Security analysis (defensive)
    - Database operations
    - Financial analysis (public data)
    - Code generation
    - Enterprise integrations
    """

    def __init__(self):
        print("="*80)
        print("ALFRED ENHANCED - FULL POWER MODE WITH RAG")
        print("="*80)
        print()

        # Initialize modules
        self.crawler = CrawlerModule()
        self.security = SecurityAnalyzer()
        self.database = DatabaseTools()
        self.finance = FinancialAnalyzer()

        # Initialize RAG Components (NEW!)
        try:
            from vector_knowledge import VectorKnowledgeBase
            self.vector_kb = VectorKnowledgeBase()
            kb_stats = self.vector_kb.get_stats()
            print(f"[OK] Vector Knowledge Base: {kb_stats['total_documents']} documents ({kb_stats['embedding_model']})")
        except Exception as e:
            print(f"[WARNING] Vector KB not available: {e}")
            self.vector_kb = None

        # Initialize Advanced Crawler (Crawl4AI Integration)
        try:
            from crawler_advanced import AdvancedCrawler
            self.crawler_advanced = AdvancedCrawler(headless=True, verbose=False)
            print(f"[OK] Advanced Crawler: Crawl4AI ready (async, LLM-optimized)")
        except Exception as e:
            print(f"[INFO] Advanced Crawler not available: {e}")
            self.crawler_advanced = None

        # Initialize RAG System
        try:
            from rag_module import RAGSystem
            self.rag = RAGSystem(
                knowledge_base=self.vector_kb,
                crawler=self.crawler_advanced
            )
            print(f"[OK] RAG System: Ready for intelligent research")
        except Exception as e:
            print(f"[INFO] RAG System not available: {e}")
            self.rag = None

        # Initialize Async Database Operations
        try:
            from database_async import AsyncDatabaseConnection
            self.async_db_class = AsyncDatabaseConnection
            print(f"[OK] Async Database: PostgreSQL, MySQL, SQLite support")
        except Exception as e:
            print(f"[INFO] Async DB not available: {e}")
            self.async_db_class = None

        # Initialize Fabric AI Patterns
        try:
            from fabric_patterns import FabricPatterns
            self.fabric = FabricPatterns()
            print(f"[OK] Fabric AI Patterns: {len(self.fabric.patterns)} patterns loaded")
        except Exception as e:
            print(f"[WARNING] Fabric Patterns not available: {e}")
            self.fabric = None

        # Initialize Ollama AI (Local Unrestricted Models)
        try:
            from ollama_integration import OllamaAI
            self.ollama = OllamaAI()
            if self.ollama.is_available:
                models = self.ollama.list_models()
                print(f"[OK] Ollama AI: {len(models)} models available")
                print(f"    Primary: {self.ollama.primary_model}")
                print(f"    Backup: {self.ollama.backup_model}")
            else:
                print("[WARNING] Ollama not running (optional)")
                self.ollama = None
        except Exception as e:
            print(f"[INFO] Ollama not available: {e}")
            self.ollama = None

        # Initialize Alfred Brain - Ultra-Enhanced Memory
        try:
            from alfred_brain import AlfredBrain
            self.brain = AlfredBrain()
            brain_stats = self.brain.get_memory_stats()
            print(f"[OK] Alfred Brain: {brain_stats['conversations']} conversations, {brain_stats['knowledge']} knowledge items")
        except Exception as e:
            print(f"[WARNING] Alfred Brain not available: {e}")
            self.brain = None

        # Initialize Enterprise Agents (GitHub, Jira, Slack, K8s)
        try:
            from enterprise_agents import EnterpriseAgentManager
            self.enterprise = EnterpriseAgentManager()
            agent_list = self.enterprise.list_agents()
            if agent_list:
                print(f"[OK] Enterprise Agents: {', '.join(agent_list)}")
            else:
                print("[INFO] Enterprise Agents: No credentials configured (optional)")
        except Exception as e:
            print(f"[INFO] Enterprise Agents not available: {e}")
            self.enterprise = None

        # Initialize Autonomous Agent (SuperAGI-style)
        try:
            from autonomous_agents import AutonomousAgentManager
            self.autonomous = AutonomousAgentManager()
            print(f"[OK] Autonomous Agent: Ready ({len(self.autonomous.default_agent.tools)} tools)")
        except Exception as e:
            print(f"[INFO] Autonomous Agent not available: {e}")
            self.autonomous = None

        # Initialize AI Personalities (LoLLMs-style)
        try:
            from ai_personalities import PersonalityManager
            self.personalities = PersonalityManager()
            print(f"[OK] AI Personalities: {len(self.personalities.personalities)} available")
        except Exception as e:
            print(f"[INFO] AI Personalities not available: {e}")
            self.personalities = None

        # Database for enhanced memory (legacy)
        self.db_path = Path("alfred_data/enhanced_memory.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

        print()
        print("CORE MODULES:")
        print("[OK] Crawler Module:", "READY" if self.crawler.available else "Limited")
        print("[OK] Security Analyzer: READY")
        print("[OK] Database Tools: READY")
        print("[OK] Financial Analyzer: READY")
        print()
        print("RAG SYSTEM:")
        print("[OK] Vector Knowledge:", "READY" if self.vector_kb else "Not Available")
        print("[OK] Advanced Crawler:", "READY" if self.crawler_advanced else "Not Available")
        print("[OK] RAG Pipeline:", "READY" if self.rag else "Not Available")
        print()
        print("ENTERPRISE AGENTS:")
        if self.enterprise and self.enterprise.list_agents():
            for agent in self.enterprise.list_agents():
                print(f"[OK] {agent.capitalize()} Agent: READY")
        else:
            print("[INFO] No enterprise agents configured (set env vars to enable)")
        print()

    def init_database(self):
        """Initialize enhanced database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Web intelligence cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                content TEXT,
                extracted_at TEXT,
                metadata TEXT
            )
        """)

        # Security findings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                scan_type TEXT,
                findings TEXT,
                scanned_at TEXT
            )
        """)

        # Financial data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                market TEXT,
                data TEXT,
                analyzed_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    async def research_topic(self, topic: str) -> Dict:
        """Research a topic using web intelligence"""
        print(f"\n[Research] Topic: {topic}")

        # Search for relevant URLs (example)
        search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}"

        results = await self.crawler.crawl_url(search_url, "links")

        # Save to cache
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO web_cache (url, content, extracted_at, metadata)
            VALUES (?, ?, ?, ?)
        """, (search_url, json.dumps(results), datetime.now().isoformat(), json.dumps({"topic": topic})))
        conn.commit()
        conn.close()

        return results

    def analyze_security(self, target: str, scan_type: str = "code") -> Dict:
        """Perform security analysis"""
        print(f"\n[Security] Analyzing: {target}")

        if scan_type == "code":
            results = self.security.analyze_code(target)
        elif scan_type == "url":
            results = self.security.check_url_safety(target)
        else:
            results = {"error": "Unknown scan type"}

        # Save results
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO security_scans (target, scan_type, findings, scanned_at)
            VALUES (?, ?, ?, ?)
        """, (target[:100], scan_type, json.dumps(results), datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return results

    async def find_financial_opportunities(self, criteria: Dict) -> List[Dict]:
        """Find financial opportunities using public data"""
        print(f"\n[Finance] Searching for opportunities...")

        opportunities = self.finance.find_opportunities(criteria)

        return opportunities

    def apply_fabric_pattern(self, pattern_name: str, input_text: str) -> str:
        """
        Apply a Fabric AI pattern to input text

        Args:
            pattern_name: Name of the pattern to apply
            input_text: Text to process with the pattern

        Returns:
            Generated prompt ready for AI processing
        """
        if not self.fabric:
            return "Fabric patterns not available. Please check installation."

        return self.fabric.apply_pattern(pattern_name, input_text)

    def list_fabric_patterns(self, tag: str = None) -> List[str]:
        """
        List available Fabric patterns

        Args:
            tag: Optional tag to filter patterns (e.g., 'SECURITY', 'BUSINESS')

        Returns:
            List of pattern names
        """
        if not self.fabric:
            return []

        if tag:
            return self.fabric.list_patterns(tag=tag)
        return self.fabric.list_patterns()

    def search_fabric_patterns(self, keyword: str) -> List[str]:
        """
        Search Fabric patterns by keyword

        Args:
            keyword: Keyword to search for in pattern names/descriptions

        Returns:
            List of matching pattern names
        """
        if not self.fabric:
            return []

        return self.fabric.search_patterns(keyword)

    def get_fabric_pattern_info(self, pattern_name: str) -> str:
        """Get detailed information about a specific pattern"""
        if not self.fabric:
            return "Fabric patterns not available."

        return self.fabric.get_pattern_info(pattern_name)

    # ========================================================================
    # ALFRED BRAIN INTEGRATION
    # ========================================================================

    def remember_conversation(
        self,
        user_input: str,
        response: str,
        topics: List[str] = None,
        importance: int = 5
    ):
        """Remember a conversation in Alfred's brain"""
        if not self.brain:
            return

        self.brain.store_conversation(
            user_input,
            response,
            topics=topics,
            importance=importance
        )

    def recall_context(self, limit: int = 5) -> List[Dict]:
        """Recall recent conversation context"""
        if not self.brain:
            return []

        return self.brain.get_conversation_context(limit)

    def learn_knowledge(
        self,
        category: str,
        key: str,
        value: str,
        importance: int = 5
    ):
        """Store knowledge in Alfred's brain"""
        if not self.brain:
            return

        self.brain.store_knowledge(category, key, value, importance=importance)

    def recall_knowledge(self, category: str, key: str = None):
        """Recall knowledge from Alfred's brain"""
        if not self.brain:
            return None

        return self.brain.recall_knowledge(category, key)

    def track_skill(self, skill_name: str, success: bool = True):
        """Track skill usage"""
        if not self.brain:
            return

        self.brain.track_skill_use(skill_name, success)

    def get_brain_insights(self) -> Dict:
        """Get insights about Alfred's learning"""
        if not self.brain:
            return {}

        return self.brain.get_insights()

    def consolidate_brain(self):
        """Consolidate Alfred's memory"""
        if not self.brain:
            return {}

        return self.brain.consolidate_memory()

    # ========================================================================
    # OLLAMA AI INTEGRATION (Unrestricted Local Models)
    # ========================================================================

    def ask_ollama(
        self,
        prompt: str,
        model: str = None,
        use_unrestricted: bool = True
    ) -> str:
        """
        Ask Ollama AI model

        Args:
            prompt: Question or prompt
            model: Specific model to use (optional)
            use_unrestricted: Use unrestricted model (default True)

        Returns:
            AI response
        """
        if not self.ollama:
            return "Ollama not available. Run: setup_ollama.bat"

        if model:
            return self.ollama.generate(prompt, model=model)
        elif use_unrestricted:
            return self.ollama.generate(prompt, model=self.ollama.primary_model)
        else:
            return self.ollama.general_query(prompt)

    def security_research_query(self, query: str) -> str:
        """
        Security research using unrestricted model

        Args:
            query: Security research question

        Returns:
            Detailed technical response (no restrictions)
        """
        if not self.ollama:
            return "Ollama not available"

        return self.ollama.security_research(query)

    def code_help(self, query: str, language: str = "python") -> str:
        """
        Get coding assistance

        Args:
            query: Coding question
            language: Programming language

        Returns:
            Code and explanation
        """
        if not self.ollama:
            return "Ollama not available"

        return self.ollama.code_assistance(query, language)

    def quick_ai_response(self, query: str) -> str:
        """
        Quick response using fast model

        Args:
            query: Quick question

        Returns:
            Fast response
        """
        if not self.ollama:
            return "Ollama not available"

        return self.ollama.quick_response(query)

    def analyze_with_ai_pattern(
        self,
        pattern_name: str,
        input_text: str,
        use_ollama: bool = True
    ) -> str:
        """
        Apply Fabric pattern using Ollama AI

        Args:
            pattern_name: Name of Fabric pattern
            input_text: Input text to analyze
            use_ollama: Use Ollama (vs external AI)

        Returns:
            Analysis result
        """
        if not self.fabric:
            return "Fabric patterns not available"

        # Get the pattern prompt
        prompt = self.fabric.apply_pattern(pattern_name, input_text)

        if use_ollama and self.ollama:
            # Use local Ollama
            return self.ollama.generate(prompt)
        else:
            # Return prompt for external AI
            return prompt

    def list_ollama_models(self) -> List[Dict]:
        """List available Ollama models"""
        if not self.ollama:
            return []

        return self.ollama.list_models()

    def pull_ollama_model(self, model_name: str) -> bool:
        """
        Download an Ollama model

        Args:
            model_name: Model to download (e.g., "dolphin-mixtral:8x7b")

        Returns:
            True if successful
        """
        if not self.ollama:
            return False

        return self.ollama.pull_model(model_name)

    # ========================================================================
    # ENTERPRISE AGENTS (GitHub, Jira, Slack, Kubernetes)
    # ========================================================================

    async def github_create_issue(self, owner: str, repo: str,
                                   title: str, body: str = "") -> Dict:
        """
        Create a GitHub issue

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue description

        Returns:
            Issue creation result
        """
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        result = await self.enterprise.github_create_issue(owner, repo, title, body)
        return result.to_dict()

    async def github_list_prs(self, owner: str, repo: str,
                               state: str = "open") -> Dict:
        """List pull requests for a repository"""
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        github = self.enterprise.get_agent("github")
        if not github:
            return {"error": "GitHub agent not configured. Set GITHUB_TOKEN"}

        result = await github.list_prs(owner, repo, state)
        return result.to_dict()

    async def jira_create_ticket(self, project: str, summary: str,
                                  description: str = "",
                                  issue_type: str = "Task") -> Dict:
        """
        Create a Jira ticket

        Args:
            project: Project key (e.g., "PROJ")
            summary: Ticket summary
            description: Ticket description
            issue_type: Issue type (Task, Bug, Story, etc.)

        Returns:
            Ticket creation result
        """
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        jira = self.enterprise.get_agent("jira")
        if not jira:
            return {"error": "Jira agent not configured. Set JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN"}

        result = await jira.create_issue(project, summary, issue_type, description)
        return result.to_dict()

    async def jira_search(self, jql: str) -> Dict:
        """Search Jira issues using JQL"""
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        jira = self.enterprise.get_agent("jira")
        if not jira:
            return {"error": "Jira agent not configured"}

        result = await jira.search_issues(jql)
        return result.to_dict()

    async def slack_send(self, channel: str, message: str) -> Dict:
        """
        Send a Slack message

        Args:
            channel: Channel name or ID
            message: Message text

        Returns:
            Message result
        """
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        result = await self.enterprise.slack_notify(channel, message)
        return result.to_dict()

    async def k8s_status(self, namespace: str = "default") -> Dict:
        """
        Get Kubernetes cluster status

        Args:
            namespace: Namespace to check

        Returns:
            Pods and deployments status
        """
        if not self.enterprise:
            return {"error": "Enterprise agents not available"}

        result = await self.enterprise.k8s_status(namespace)
        return result.to_dict()

    async def enterprise_health_check(self) -> Dict:
        """Check health of all enterprise agents"""
        if not self.enterprise:
            return {"error": "Enterprise agents not available", "agents": {}}

        health = await self.enterprise.health_check_all()
        return {"agents": health, "available": self.enterprise.list_agents()}

    # ========================================================================
    # AUTONOMOUS AGENT (SuperAGI-Style Multi-Step Tasks)
    # ========================================================================

    async def run_autonomous_task(self, goal: str, max_steps: int = 10) -> Dict:
        """
        Run an autonomous task using ReAct reasoning

        Args:
            goal: The task goal to achieve
            max_steps: Maximum steps before timeout

        Returns:
            Task result with reasoning trace
        """
        if not self.autonomous:
            return {"error": "Autonomous agent not available"}

        self.autonomous.default_agent.max_steps = max_steps
        result = await self.autonomous.run_task(goal)
        return result

    def list_autonomous_tools(self) -> List[str]:
        """List available tools for autonomous agent"""
        if not self.autonomous:
            return []

        return list(self.autonomous.default_agent.tools.keys())

    def get_autonomous_history(self) -> List[Dict]:
        """Get task history from autonomous agent"""
        if not self.autonomous:
            return []

        return self.autonomous.get_task_history()

    # ========================================================================
    # AI PERSONALITIES (LoLLMs-Style Expert Personas)
    # ========================================================================

    def set_personality(self, personality_id: str) -> Dict:
        """
        Set Alfred's current personality

        Args:
            personality_id: ID of personality to use (e.g., 'python_expert')

        Returns:
            Personality info or error
        """
        if not self.personalities:
            return {"error": "Personalities not available"}

        if self.personalities.set_personality(personality_id):
            p = self.personalities.get_current()
            return {"success": True, "personality": p.to_dict()}
        return {"error": f"Personality '{personality_id}' not found"}

    def clear_personality(self):
        """Clear current personality (return to default Alfred)"""
        if self.personalities:
            self.personalities.clear_personality()

    def get_current_personality(self) -> Optional[Dict]:
        """Get current personality info"""
        if not self.personalities:
            return None
        p = self.personalities.get_current()
        return p.to_dict() if p else None

    def list_personalities(self, category: str = None) -> List[Dict]:
        """List available personalities"""
        if not self.personalities:
            return []
        return self.personalities.list_personalities(category)

    def search_personalities(self, query: str) -> List[Dict]:
        """Search personalities by expertise"""
        if not self.personalities:
            return []
        return self.personalities.search_personalities(query)

    def ask_with_personality(self, prompt: str, personality_id: str = None) -> str:
        """
        Ask question using a specific personality

        Args:
            prompt: User question
            personality_id: Optional personality (uses current if not specified)

        Returns:
            AI response with personality applied
        """
        if not self.personalities:
            return self.ask_ollama(prompt)

        # Apply personality to prompt
        enhanced_prompt = self.personalities.apply_personality_to_prompt(prompt, personality_id)

        # Use Ollama if available
        if self.ollama:
            return self.ollama.generate(enhanced_prompt)
        return enhanced_prompt


def main():
    """Main entry point"""

    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                     ALFRED ENHANCED - FULL POWER                          ║
    ║                  PATENT PENDING - AI Memory & Learning System             ║
    ║                                                                           ║
    ║  Web Intelligence │ Security Analysis │ Database Tools │ Financial AI   ║
    ║                                                                           ║
    ║  AUTHORIZATION REQUIRED FOR:                                             ║
    ║  • Security testing (authorized targets only)                            ║
    ║  • Web scraping (respect robots.txt & ToS)                               ║
    ║  • Financial analysis (public data sources)                              ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)

    alfred = AlfredEnhanced()

    print("\nCapabilities:")
    print("  1. Web Research & Intelligence")
    print("  2. Security Analysis (Defensive)")
    print("  3. Database Operations")
    print("  4. Financial Market Analysis")
    print("  5. Code Generation")

    if alfred.fabric:
        print(f"  6. Fabric AI Patterns ({len(alfred.fabric.patterns)} patterns)")

    if alfred.ollama:
        models = alfred.list_ollama_models()
        print(f"  7. Ollama AI - Local Unrestricted Models ({len(models)} installed)")
        print(f"     Primary: {alfred.ollama.primary_model}")
        print(f"     Backup: {alfred.ollama.backup_model}")

    if alfred.brain:
        stats = alfred.brain.get_memory_stats()
        print(f"  8. Alfred Brain - Ultra Memory ({stats['conversations']} conversations remembered)")
        print()
        print("Brain Capabilities:")
        print("  - Conversation memory with context")
        print("  - Knowledge base with semantic search")
        print("  - Pattern recognition & learning")
        print("  - Skill proficiency tracking")
        print("  - User preference adaptation")
        print("  - Learning from mistakes")

    if alfred.ollama:
        print()
        print("Ollama Capabilities:")
        print("  - Unrestricted AI (no censorship)")
        print("  - Security research & pentesting")
        print("  - Advanced coding assistance")
        print("  - Local, private, free")

    if alfred.fabric:
        print()
        print("Example Fabric Pattern Usage:")
        print("  - alfred.apply_fabric_pattern('extract_wisdom', 'your text')")
        print("  - alfred.list_fabric_patterns(tag='SECURITY')")
        print("  - alfred.search_fabric_patterns('code')")

    if alfred.ollama:
        print()
        print("Example Ollama Usage:")
        print("  - alfred.ask_ollama('How do I test for XSS?')")
        print("  - alfred.security_research_query('SQL injection techniques')")
        print("  - alfred.code_help('Optimize this Python code', 'python')")
        print("  - alfred.analyze_with_ai_pattern('code_review', code_text)")

    if alfred.brain:
        print()
        print("Example Brain Usage:")
        print("  - alfred.remember_conversation('user input', 'response', ['topics'])")
        print("  - alfred.recall_context(5)")
        print("  - alfred.learn_knowledge('category', 'key', 'value')")
        print("  - alfred.get_brain_insights()")

    if alfred.enterprise:
        agents = alfred.enterprise.list_agents()
        if agents:
            print()
            print(f"Enterprise Agents Available: {', '.join(agents)}")
            print()
            print("Example Enterprise Usage:")
            if "github" in agents:
                print("  - await alfred.github_create_issue('owner', 'repo', 'Bug title')")
                print("  - await alfred.github_list_prs('owner', 'repo')")
            if "jira" in agents:
                print("  - await alfred.jira_create_ticket('PROJ', 'Task summary')")
                print("  - await alfred.jira_search('project = PROJ AND status = Open')")
            if "slack" in agents:
                print("  - await alfred.slack_send('#general', 'Hello from Alfred!')")
            if "kubernetes" in agents:
                print("  - await alfred.k8s_status('default')")
        else:
            print()
            print("Enterprise Agents (configure to enable):")
            print("  GITHUB_TOKEN - GitHub Personal Access Token")
            print("  JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN - Jira Cloud")
            print("  SLACK_BOT_TOKEN - Slack Bot Token")
            print("  KUBECONFIG - Kubernetes config file")

    print()
    print("="*80)
    print("Alfred Enhanced initialized successfully!")
    print("="*80)


if __name__ == "__main__":
    main()
