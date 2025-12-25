#!/usr/bin/env python3
"""
Fabric AI Patterns - 227+ Expert Prompts
Integrated from Fabric AI Framework and Alfred the Batcomputer

This module provides access to 227+ AI patterns from the Fabric framework
plus custom Alfred patterns for enhanced AI assistance.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class FabricPatterns:
    """
    Expert AI patterns for various tasks
    Based on Fabric AI framework + Custom Alfred patterns

    Features:
    - 227+ Fabric patterns from danielmiessler/fabric
    - Custom security, business, and automation patterns
    - Dynamic pattern loading from JSON
    - Fallback to embedded patterns
    """

    def __init__(self):
        self.custom_patterns = self.load_custom_patterns()
        self.fabric_patterns = self.load_fabric_patterns()
        self.patterns = {**self.custom_patterns, **self.fabric_patterns}

    def load_fabric_patterns(self) -> dict:
        """Load all 227+ patterns from Fabric framework"""

        # Try to load from BAT_UBX Fabric installation
        fabric_paths = [
            Path("C:/BAT_UBX/Fabric-main/scripts/pattern_descriptions/pattern_descriptions.json"),
            Path("C:/Alfred the Batcomputer/Fabric-main/scripts/pattern_descriptions/pattern_descriptions.json"),
            Path("../Fabric-main/scripts/pattern_descriptions/pattern_descriptions.json"),
        ]

        patterns = {}

        for fabric_path in fabric_paths:
            if fabric_path.exists():
                try:
                    with open(fabric_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # Convert Fabric patterns to our format
                        for pattern_info in data.get('patterns', []):
                            pattern_name = pattern_info['patternName']
                            patterns[pattern_name] = {
                                "name": pattern_name.replace('_', ' ').title(),
                                "description": pattern_info['description'],
                                "tags": pattern_info.get('tags', []),
                                "prompt": self.generate_fabric_prompt(pattern_name, pattern_info['description'])
                            }

                        print(f"[Fabric] Loaded {len(patterns)} patterns from {fabric_path}")
                        return patterns

                except Exception as e:
                    print(f"[Fabric] Error loading from {fabric_path}: {e}")
                    continue

        print("[Fabric] Using embedded fallback patterns")
        return self.load_embedded_fabric_patterns()

    def generate_fabric_prompt(self, pattern_name: str, description: str) -> str:
        """Generate a prompt template for Fabric patterns"""
        return f"""Apply the '{pattern_name}' pattern to analyze:

{{input}}

Task: {description}

Provide comprehensive analysis following this pattern's methodology."""

    def load_embedded_fabric_patterns(self) -> dict:
        """Embedded subset of most popular Fabric patterns"""
        return {
            "extract_wisdom": {
                "name": "Extract Wisdom",
                "description": "Extract insightful ideas and recommendations focusing on life wisdom",
                "tags": ["EXTRACT", "WISDOM", "SELF"],
                "prompt": """Extract the most valuable wisdom from:

{input}

Provide:
1. Main Ideas (5-10 key concepts)
2. Insights (unique perspectives)
3. Quotes (most impactful quotes)
4. Habits (actionable habits suggested)
5. Facts (interesting facts mentioned)
6. References (books, people, resources mentioned)
7. Recommendations (what to do with this information)"""
            },

            "create_summary": {
                "name": "Create Summary",
                "description": "Generate concise summaries by extracting key points",
                "tags": ["SUMMARIZE", "WRITING"],
                "prompt": """Create a comprehensive summary of:

{input}

Include:
1. One-sentence summary
2. Main points (3-5 bullets)
3. Key takeaways
4. Who should read/watch this
5. Best quote
6. Rating out of 10"""
            },

            "analyze_claims": {
                "name": "Analyze Claims",
                "description": "Evaluate truth claims by analyzing evidence and logical fallacies",
                "tags": ["ANALYSIS", "RESEARCH", "CR THINKING"],
                "prompt": """Analyze the claims made in:

{input}

For each claim provide:
1. The claim itself
2. Evidence provided
3. Strength of evidence (Strong/Medium/Weak)
4. Potential biases
5. Counter-arguments
6. Verification sources
7. Overall credibility rating"""
            },

            "improve_writing": {
                "name": "Improve Writing",
                "description": "Enhance writing by improving clarity, flow, and style",
                "tags": ["WRITING"],
                "prompt": """Improve this writing:

{input}

Focus on:
1. Clarity - Make it clearer
2. Conciseness - Remove fluff
3. Impact - Make it more compelling
4. Flow - Improve transitions
5. Grammar - Fix errors
6. Tone - Appropriate for audience

Provide both the improved version and explanation of changes."""
            },

            "create_keynote": {
                "name": "Create Keynote",
                "description": "Design TED-style presentations with narrative, slides and notes",
                "tags": ["WRITING", "VISUALIZE"],
                "prompt": """Create a keynote presentation outline for:

{input}

Structure:
1. Title Slide
2. Hook/Opening Story
3. Main Points (3-5 slides each)
4. Supporting Data/Visuals
5. Key Takeaways
6. Call to Action
7. Q&A Topics

Include speaker notes for each slide."""
            },
        }

    def load_custom_patterns(self) -> dict:
        """Load custom Alfred-specific patterns"""
        return {
            # SECURITY PATTERNS (Custom Alfred)
            "security_audit": {
                "name": "Security Audit",
                "description": "Comprehensive security analysis",
                "tags": ["SECURITY"],
                "prompt": """Analyze the following for security vulnerabilities:

1. SQL Injection risks
2. XSS vulnerabilities
3. Authentication/Authorization issues
4. Data exposure risks
5. Input validation problems
6. OWASP Top 10 considerations

{input}

Provide detailed findings with severity levels."""
            },

            "vulnerability_scanner": {
                "name": "Vulnerability Scanner",
                "description": "Scan code for common vulnerabilities",
                "tags": ["SECURITY"],
                "prompt": """Scan this code for vulnerabilities:

Check for:
- Hardcoded credentials
- Unsafe deserialization
- Command injection
- Path traversal
- Insecure cryptography
- Race conditions

{input}

List all findings with recommended fixes."""
            },

            # WEB INTELLIGENCE PATTERNS (Custom Alfred)
            "web_research": {
                "name": "Web Research",
                "description": "Deep research analysis",
                "tags": ["RESEARCH"],
                "prompt": """Research the following topic in depth:

{input}

Provide:
1. Key findings and insights
2. Recent developments
3. Expert opinions
4. Data sources and citations
5. Actionable conclusions"""
            },

            # FINANCIAL PATTERNS (Custom Alfred)
            "market_analysis": {
                "name": "Market Analysis",
                "description": "Analyze market opportunities",
                "tags": ["BUSINESS", "ANALYSIS"],
                "prompt": """Analyze this market data:

{input}

Provide:
1. Current market trends
2. Opportunities identified
3. Risk assessment
4. Potential strategies
5. Data-driven recommendations"""
            },

            "investment_research": {
                "name": "Investment Research",
                "description": "Research investment opportunities",
                "tags": ["BUSINESS", "ANALYSIS"],
                "prompt": """Research investment opportunity:

{input}

Analyze:
- Market potential
- Competition landscape
- Risk factors
- Financial metrics
- Growth prospects
- Recommendation (with caveats)"""
            },

            # CODE PATTERNS (Custom Alfred)
            "code_review": {
                "name": "Code Review",
                "description": "Professional code review",
                "tags": ["DEVELOPMENT", "REVIEW"],
                "prompt": """Review this code professionally:

{input}

Check:
1. Code quality and style
2. Performance issues
3. Security concerns
4. Best practices
5. Potential bugs
6. Improvement suggestions"""
            },

            "optimize_code": {
                "name": "Optimize Code",
                "description": "Optimize code performance",
                "tags": ["DEVELOPMENT"],
                "prompt": """Optimize this code for better performance:

{input}

Focus on:
- Algorithm efficiency
- Memory usage
- Speed improvements
- Scalability
- Readability vs performance tradeoffs"""
            },

            # BUSINESS PATTERNS (Custom Alfred)
            "business_analysis": {
                "name": "Business Analysis",
                "description": "Analyze business opportunities",
                "tags": ["BUSINESS", "ANALYSIS"],
                "prompt": """Analyze this business opportunity:

{input}

Evaluate:
1. Market opportunity size
2. Competitive advantages
3. Revenue potential
4. Risk factors
5. Resource requirements
6. Go-to-market strategy"""
            },

            "competitive_analysis": {
                "name": "Competitive Analysis",
                "description": "Analyze competition",
                "tags": ["BUSINESS", "ANALYSIS"],
                "prompt": """Analyze competitive landscape:

{input}

Assess:
- Key competitors
- Their strengths/weaknesses
- Market positioning
- Differentiation opportunities
- Threat level
- Strategic recommendations"""
            },

            # AUTOMATION PATTERNS (Custom Alfred)
            "automation_script": {
                "name": "Automation Script",
                "description": "Generate automation scripts",
                "tags": ["DEVELOPMENT", "AUTOMATION"],
                "prompt": """Create automation script for:

{input}

Generate:
1. Well-documented code
2. Error handling
3. Logging
4. Configuration options
5. Usage instructions"""
            },

            "web_scraper": {
                "name": "Web Scraper",
                "description": "Generate web scraping code",
                "tags": ["DEVELOPMENT", "AUTOMATION"],
                "prompt": """Create web scraper for:

{input}

Requirements:
1. Respect robots.txt
2. Rate limiting
3. Error handling
4. Data extraction logic
5. Storage format
6. Ethical scraping practices

Legal use only."""
            },

            # PENTESTING PATTERNS (Authorized Only - Custom Alfred)
            "pentest_plan": {
                "name": "Penetration Test Plan",
                "description": "Plan authorized security testing",
                "tags": ["SECURITY", "STRATEGY"],
                "prompt": """Create penetration testing plan for:

{input}

AUTHORIZATION REQUIRED

Plan should include:
1. Scope definition
2. Testing methodology
3. Tools to use
4. Attack vectors to test
5. Reporting format
6. Rules of engagement

Note: Only for authorized targets with written permission."""
            },

            "bug_bounty_research": {
                "name": "Bug Bounty Research",
                "description": "Research for bug bounties",
                "tags": ["SECURITY", "RESEARCH"],
                "prompt": """Research bug bounty opportunity:

{input}

Focus on:
1. Program scope and rules
2. Common vulnerability types
3. Payout structure
4. Submission process
5. Testing approach
6. Tools and techniques

Follow responsible disclosure practices."""
            },

            "exploit_analysis": {
                "name": "Exploit Analysis",
                "description": "Analyze vulnerabilities (defensive)",
                "tags": ["SECURITY", "ANALYSIS"],
                "prompt": """Analyze this vulnerability for defensive purposes:

{input}

Provide:
1. Vulnerability description
2. Exploitation method (educational)
3. Affected systems
4. Mitigation strategies
5. Detection methods
6. Patching recommendations

For defensive security only."""
            },

            # DATABASE PATTERNS (Custom Alfred)
            "generate_migration": {
                "name": "Database Migration",
                "description": "Generate database migrations",
                "tags": ["DEVELOPMENT", "DATABASE"],
                "prompt": """Generate database migration for:

{input}

Include:
1. Up migration (schema changes)
2. Down migration (rollback)
3. Data transformations if needed
4. Index creation
5. Constraints
6. Comments and documentation"""
            },

            "sql_query_builder": {
                "name": "SQL Query Builder",
                "description": "Generate SQL from natural language",
                "tags": ["DEVELOPMENT", "DATABASE"],
                "prompt": """Generate SQL query for:

{input}

Provide:
1. Optimized query
2. Explanation of logic
3. Index recommendations
4. Potential performance issues
5. Alternative approaches if applicable"""
            },
        }

    def get_pattern(self, pattern_name: str) -> dict:
        """Get a specific pattern by name"""
        return self.patterns.get(pattern_name, {})

    def apply_pattern(self, pattern_name: str, input_text: str) -> str:
        """Apply a pattern to input text"""
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            return f"Pattern '{pattern_name}' not found. Use list_patterns() to see available patterns."

        prompt = pattern["prompt"].format(input=input_text)
        return prompt

    def list_patterns(self, category: str = None, tag: str = None) -> List[str]:
        """
        List all available patterns

        Args:
            category: Filter by category in name (optional)
            tag: Filter by tag (optional)

        Returns:
            List of pattern names
        """
        if category:
            return [name for name, p in self.patterns.items()
                   if category.lower() in p["name"].lower()]
        elif tag:
            return [name for name, p in self.patterns.items()
                   if tag.upper() in p.get("tags", [])]
        return sorted(list(self.patterns.keys()))

    def get_patterns_by_tag(self, tag: str) -> Dict[str, dict]:
        """Get all patterns with a specific tag"""
        tag_upper = tag.upper()
        return {name: pattern for name, pattern in self.patterns.items()
                if tag_upper in pattern.get("tags", [])}

    def get_all_tags(self) -> List[str]:
        """Get all unique tags from all patterns"""
        tags = set()
        for pattern in self.patterns.values():
            tags.update(pattern.get("tags", []))
        return sorted(list(tags))

    def search_patterns(self, query: str) -> List[str]:
        """Search patterns by name or description"""
        query_lower = query.lower()
        return [name for name, pattern in self.patterns.items()
                if query_lower in pattern["name"].lower() or
                   query_lower in pattern["description"].lower()]

    def get_pattern_info(self, pattern_name: str) -> str:
        """Get formatted information about a pattern"""
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            return f"Pattern '{pattern_name}' not found"

        info = f"""
Pattern: {pattern['name']}
Description: {pattern['description']}
Tags: {', '.join(pattern.get('tags', []))}

Usage: fabric.apply_pattern('{pattern_name}', 'your input text here')
"""
        return info


# Command-line interface
if __name__ == "__main__":
    fabric = FabricPatterns()

    print("="*80)
    print("FABRIC AI PATTERNS - ALFRED ULTIMATE")
    print("="*80)
    print()
    print(f"Total Patterns Loaded: {len(fabric.patterns)}")
    print(f"  - Fabric Patterns: {len(fabric.fabric_patterns)}")
    print(f"  - Custom Alfred Patterns: {len(fabric.custom_patterns)}")
    print()

    print("Available Tags:")
    tags = fabric.get_all_tags()
    print(f"  {', '.join(tags)}")
    print()

    print("Sample Patterns by Category:")
    print()

    # Show samples from each category
    categories = {}
    for name, pattern in list(fabric.patterns.items())[:50]:
        for tag in pattern.get('tags', []):
            if tag not in categories:
                categories[tag] = []
            if len(categories[tag]) < 3:
                categories[tag].append(name)

    for tag in sorted(categories.keys())[:10]:
        print(f"\n  {tag}:")
        for pattern_name in categories[tag]:
            pattern = fabric.patterns[pattern_name]
            print(f"    - {pattern_name}: {pattern['description'][:60]}...")

    print()
    print("="*80)
    print(f"Use fabric.list_patterns() to see all {len(fabric.patterns)} patterns")
    print(f"Use fabric.search_patterns('keyword') to search")
    print(f"Use fabric.get_patterns_by_tag('TAG') to filter by tag")
    print("="*80)
