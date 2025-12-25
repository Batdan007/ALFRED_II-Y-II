"""
Tech Pulse Module
Cutting-edge technology intelligence and emerging tech tracking

Domains:
- Artificial Intelligence / Machine Learning
- Cybersecurity developments
- Quantum computing
- Blockchain / Web3
- Hardware innovations
- Open source developments
- Developer tools and frameworks

Author: Daniel J Rita (BATDAN)
For: ALFRED_J_RITA - Edge of Tomorrow Technical Intelligence
"""

import os
import re
import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import json


class TechPulse:
    """
    Cutting-edge technology intelligence for ALFRED

    Tracks:
    - AI/ML developments (models, research, releases)
    - Security tool releases
    - GitHub trending repos
    - Tech announcements
    - Framework/library updates
    - Hardware releases
    """

    # Tech categories and their keywords
    TECH_DOMAINS = {
        'ai': [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'large language model', 'gpt', 'claude',
            'gemini', 'llama', 'mistral', 'transformer', 'diffusion',
            'stable diffusion', 'midjourney', 'dall-e', 'computer vision',
            'nlp', 'natural language', 'reinforcement learning', 'rag',
            'fine-tuning', 'training', 'inference', 'embedding'
        ],
        'security': [
            'cybersecurity', 'penetration testing', 'pentest', 'red team',
            'blue team', 'threat hunting', 'malware analysis', 'reverse engineering',
            'exploit development', 'bug bounty', 'vulnerability', 'ctf',
            'osint', 'forensics', 'incident response', 'siem', 'soc',
            'zero trust', 'devsecops', 'appsec'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'google cloud', 'kubernetes', 'k8s',
            'docker', 'container', 'serverless', 'lambda', 'terraform',
            'infrastructure as code', 'iac', 'devops', 'ci/cd', 'gitops'
        ],
        'web3': [
            'blockchain', 'crypto', 'ethereum', 'solana', 'defi',
            'nft', 'smart contract', 'web3', 'dao', 'dapp'
        ],
        'quantum': [
            'quantum computing', 'quantum', 'qubit', 'quantum supremacy',
            'quantum algorithm', 'quantum cryptography'
        ],
        'hardware': [
            'chip', 'processor', 'gpu', 'tpu', 'npu', 'silicon',
            'semiconductor', 'nvidia', 'amd', 'intel', 'apple silicon',
            'm1', 'm2', 'm3', 'm4', 'arm', 'risc-v'
        ]
    }

    # Major tech companies/orgs to track
    TECH_LEADERS = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'google': 'Google/DeepMind',
        'meta': 'Meta AI',
        'microsoft': 'Microsoft',
        'nvidia': 'NVIDIA',
        'apple': 'Apple',
        'aws': 'Amazon Web Services',
        'huggingface': 'Hugging Face',
        'stability': 'Stability AI',
        'mistral': 'Mistral AI',
        'xai': 'xAI',
        'cohere': 'Cohere',
    }

    # Security tools categories
    SECURITY_TOOLS = {
        'recon': ['nmap', 'masscan', 'amass', 'subfinder', 'nuclei'],
        'exploit': ['metasploit', 'cobalt strike', 'sliver', 'havoc'],
        'web': ['burp', 'zap', 'sqlmap', 'ffuf', 'dirsearch'],
        'network': ['wireshark', 'tcpdump', 'responder', 'impacket'],
        'password': ['hashcat', 'john', 'hydra', 'crackmapexec'],
        'forensics': ['volatility', 'autopsy', 'sleuthkit', 'yara'],
        'osint': ['maltego', 'spiderfoot', 'theHarvester', 'shodan'],
    }

    def __init__(self, github_token: Optional[str] = None,
                 newsapi_key: Optional[str] = None):
        """
        Initialize tech pulse

        Args:
            github_token: GitHub API token for higher rate limits
            newsapi_key: NewsAPI key for tech news
        """
        self.logger = logging.getLogger(__name__)
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')

        # API endpoints
        self.github_api = "https://api.github.com"
        self.newsapi_url = "https://newsapi.org/v2"
        self.hacker_news_api = "https://hacker-news.firebaseio.com/v0"

    def is_available(self) -> bool:
        """Tech pulse is always available"""
        return True

    def detect_tech_domain(self, text: str) -> List[str]:
        """
        Detect which tech domains the query relates to

        Args:
            text: User message

        Returns:
            List of matching domains
        """
        text_lower = text.lower()
        matching = []

        for domain, keywords in self.TECH_DOMAINS.items():
            if any(kw in text_lower for kw in keywords):
                matching.append(domain)

        return matching if matching else ['general']

    def is_tech_query(self, text: str) -> bool:
        """
        Detect if text is asking about technology

        Args:
            text: User message

        Returns:
            True if tech-related query
        """
        tech_keywords = [
            'technology', 'tech', 'latest', 'new', 'release', 'update',
            'framework', 'library', 'tool', 'software', 'open source',
            'github', 'trending', 'development', 'programming', 'code',
            'api', 'sdk', 'platform'
        ]

        # Also check domain-specific keywords
        all_keywords = tech_keywords.copy()
        for keywords in self.TECH_DOMAINS.values():
            all_keywords.extend(keywords)

        text_lower = text.lower()
        return any(kw in text_lower for kw in all_keywords)

    def get_github_trending(self, language: Optional[str] = None,
                            since: str = 'daily') -> List[Dict]:
        """
        Get trending GitHub repositories

        Args:
            language: Programming language filter
            since: Time period (daily, weekly, monthly)

        Returns:
            List of trending repos
        """
        try:
            # GitHub doesn't have an official trending API, use search
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'

            # Search for recently created/updated repos with high stars
            date_cutoff = datetime.now() - timedelta(days=7 if since == 'weekly' else 30 if since == 'monthly' else 1)
            date_str = date_cutoff.strftime('%Y-%m-%d')

            query = f'created:>{date_str} stars:>10'
            if language:
                query += f' language:{language}'

            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }

            response = requests.get(
                f"{self.github_api}/search/repositories",
                params=params,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                repos = []

                for repo in data.get('items', [])[:10]:
                    repos.append({
                        'name': repo['full_name'],
                        'description': repo.get('description', '')[:150] if repo.get('description') else 'No description',
                        'stars': repo['stargazers_count'],
                        'language': repo.get('language', 'Unknown'),
                        'url': repo['html_url'],
                        'topics': repo.get('topics', [])[:5]
                    })

                return repos

            return []

        except Exception as e:
            self.logger.error(f"GitHub trending fetch failed: {e}")
            return []

    def get_security_tools_updates(self) -> List[Dict]:
        """
        Get recent updates to popular security tools

        Returns:
            List of security tool updates
        """
        updates = []

        # Check a few popular security repos
        security_repos = [
            'projectdiscovery/nuclei',
            'projectdiscovery/subfinder',
            'ffuf/ffuf',
            'sqlmapproject/sqlmap',
            'impacket/impacket',
            'BloodHoundAD/BloodHound',
            'gentilkiwi/mimikatz',
            'BishopFox/sliver',
        ]

        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'

        for repo in security_repos[:5]:  # Limit to avoid rate limits
            try:
                response = requests.get(
                    f"{self.github_api}/repos/{repo}/releases/latest",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    release = response.json()
                    updates.append({
                        'tool': repo.split('/')[-1],
                        'repo': repo,
                        'version': release.get('tag_name', 'Unknown'),
                        'published': release.get('published_at', '')[:10],
                        'name': release.get('name', ''),
                        'url': release.get('html_url', '')
                    })

            except Exception:
                continue

        return updates

    def get_hacker_news_top(self, limit: int = 10) -> List[Dict]:
        """
        Get top stories from Hacker News

        Args:
            limit: Number of stories

        Returns:
            List of top stories
        """
        try:
            # Get top story IDs
            response = requests.get(f"{self.hacker_news_api}/topstories.json", timeout=10)

            if response.status_code == 200:
                story_ids = response.json()[:limit]
                stories = []

                for story_id in story_ids:
                    story_response = requests.get(
                        f"{self.hacker_news_api}/item/{story_id}.json",
                        timeout=5
                    )

                    if story_response.status_code == 200:
                        story = story_response.json()
                        if story.get('type') == 'story':
                            stories.append({
                                'title': story.get('title', ''),
                                'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                'score': story.get('score', 0),
                                'comments': story.get('descendants', 0),
                                'by': story.get('by', 'unknown')
                            })

                return stories

            return []

        except Exception as e:
            self.logger.error(f"Hacker News fetch failed: {e}")
            return []

    def get_ai_developments(self) -> Dict:
        """
        Get latest AI/ML developments

        Returns:
            AI development summary
        """
        developments = {
            'timestamp': datetime.now().isoformat(),
            'trending_repos': [],
            'news': []
        }

        # Get AI-related trending repos
        ai_repos = self.get_github_trending(language='python')
        ai_filtered = [
            r for r in ai_repos
            if any(kw in (r.get('description', '') + ' ' + r['name']).lower()
                   for kw in ['ai', 'ml', 'llm', 'gpt', 'neural', 'model', 'transformer'])
        ]
        developments['trending_repos'] = ai_filtered[:5]

        # Get AI news from Hacker News
        hn_stories = self.get_hacker_news_top(20)
        ai_news = [
            s for s in hn_stories
            if any(kw in s.get('title', '').lower()
                   for kw in ['ai', 'gpt', 'llm', 'openai', 'anthropic', 'claude', 'gemini', 'mistral'])
        ]
        developments['news'] = ai_news[:5]

        return developments

    def format_trending_repos(self, repos: List[Dict]) -> str:
        """Format trending repos for display"""
        lines = []
        for repo in repos:
            stars = f"* {repo['stars']}"
            lang = f"[{repo['language']}]" if repo['language'] else ''
            lines.append(f"• {repo['name']} {stars} {lang}")
            if repo['description']:
                lines.append(f"  {repo['description'][:80]}...")
        return "\n".join(lines)

    def format_hn_stories(self, stories: List[Dict]) -> str:
        """Format Hacker News stories for display"""
        lines = []
        for story in stories:
            lines.append(f"• {story['title']} ({story['score']} pts, {story['comments']} comments)")
        return "\n".join(lines)

    def get_tech_brief(self, domains: List[str] = None) -> Dict:
        """
        Get comprehensive tech briefing

        Args:
            domains: Specific domains to focus on

        Returns:
            Tech intelligence briefing
        """
        domains = domains or ['ai', 'security']

        brief = {
            'timestamp': datetime.now().isoformat(),
            'domains': domains,
            'highlights': []
        }

        # Always include HN top stories (tech pulse)
        hn_stories = self.get_hacker_news_top(10)
        brief['hacker_news'] = hn_stories[:5]

        # Domain-specific content
        if 'ai' in domains:
            ai_dev = self.get_ai_developments()
            brief['ai'] = ai_dev

        if 'security' in domains:
            sec_tools = self.get_security_tools_updates()
            brief['security_tools'] = sec_tools

        # Get trending repos
        trending = self.get_github_trending()
        brief['trending_github'] = trending[:5]

        return brief

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point for tech queries

        Args:
            text: User message

        Returns:
            Tuple of (was_tech_query, context_to_inject)
        """
        if not self.is_tech_query(text):
            return False, ""

        domains = self.detect_tech_domain(text)
        self.logger.info(f"Tech query detected - domains: {domains}")

        context_parts = []
        context_parts.append(f"[TECH PULSE - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]")

        # Check for specific requests
        text_lower = text.lower()

        # GitHub trending
        if 'github' in text_lower or 'trending' in text_lower or 'repository' in text_lower or 'repo' in text_lower:
            # Check for language filter
            languages = ['python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c++', 'c#']
            lang_filter = None
            for lang in languages:
                if lang in text_lower:
                    lang_filter = lang
                    break

            repos = self.get_github_trending(language=lang_filter)
            if repos:
                lang_str = f" ({lang_filter})" if lang_filter else ""
                context_parts.append(f"\nTrending GitHub Repositories{lang_str}:")
                context_parts.append(self.format_trending_repos(repos[:5]))

        # AI developments
        if 'ai' in domains or any(kw in text_lower for kw in ['ai', 'machine learning', 'llm', 'gpt']):
            ai_dev = self.get_ai_developments()
            if ai_dev['trending_repos']:
                context_parts.append("\nAI/ML Trending Repositories:")
                context_parts.append(self.format_trending_repos(ai_dev['trending_repos']))
            if ai_dev['news']:
                context_parts.append("\nAI News from Hacker News:")
                context_parts.append(self.format_hn_stories(ai_dev['news']))

        # Security tools
        if 'security' in domains or any(kw in text_lower for kw in ['security', 'pentest', 'hacking', 'tool']):
            sec_tools = self.get_security_tools_updates()
            if sec_tools:
                context_parts.append("\nSecurity Tool Updates:")
                for tool in sec_tools[:5]:
                    context_parts.append(f"• {tool['tool']} {tool['version']} ({tool['published']})")

        # General tech news (Hacker News)
        if 'news' in text_lower or 'latest' in text_lower or len(context_parts) == 1:
            hn = self.get_hacker_news_top(10)
            if hn:
                context_parts.append("\nTech News (Hacker News Top Stories):")
                context_parts.append(self.format_hn_stories(hn[:5]))

        if len(context_parts) == 1:
            return False, ""

        context_parts.append("\n[Use this tech intelligence to provide cutting-edge insights]")
        return True, "\n".join(context_parts)


# Convenience function
def create_tech_pulse() -> TechPulse:
    """Create tech pulse instance"""
    return TechPulse()
