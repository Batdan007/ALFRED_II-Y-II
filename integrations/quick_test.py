"""
Quick Integration Test Script
Run with your API keys to test GitHub and Slack integrations.

Usage:
    python quick_test.py --github YOUR_TOKEN --repo owner/repo
    python quick_test.py --slack YOUR_WEBHOOK_URL
    python quick_test.py --github YOUR_TOKEN --slack YOUR_WEBHOOK_URL
"""

import asyncio
import argparse
import sys


async def test_github(token: str, repo: str = None):
    """Test GitHub integration"""
    print("\n" + "=" * 50)
    print("  TESTING GITHUB INTEGRATION")
    print("=" * 50)

    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], check=True)
        import aiohttp

    async with aiohttp.ClientSession() as session:
        # Test authentication
        async with session.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"[OK] Authenticated as: {data.get('login')}")
                print(f"     Name: {data.get('name', 'N/A')}")
                print(f"     Public repos: {data.get('public_repos', 0)}")

                if repo:
                    # Test repo access
                    async with session.get(
                        f"https://api.github.com/repos/{repo}",
                        headers={"Authorization": f"Bearer {token}"}
                    ) as repo_resp:
                        if repo_resp.status == 200:
                            repo_data = await repo_resp.json()
                            print(f"[OK] Repository access: {repo}")
                            print(f"     Stars: {repo_data.get('stargazers_count', 0)}")
                            print(f"     Open issues: {repo_data.get('open_issues_count', 0)}")
                        else:
                            print(f"[FAIL] Cannot access repository: {repo}")
                            print(f"       Status: {repo_resp.status}")

                return True
            else:
                print(f"[FAIL] Authentication failed")
                print(f"       Status: {response.status}")
                error = await response.json()
                print(f"       Error: {error.get('message', 'Unknown')}")
                return False


async def test_slack(webhook_url: str):
    """Test Slack integration"""
    print("\n" + "=" * 50)
    print("  TESTING SLACK INTEGRATION")
    print("=" * 50)

    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], check=True)
        import aiohttp

    # Validate webhook URL format
    if not webhook_url.startswith("https://hooks.slack.com/"):
        print("[FAIL] Invalid webhook URL format")
        print("       URL should start with: https://hooks.slack.com/")
        return False

    message = {
        "text": "ALFRED Security Agent - Test Message",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "ALFRED Security Agent Connected!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Integration test successful!*\n\nYour Slack webhook is properly configured. You will receive security alerts in this channel."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_This is a test message from ALFRED Security Agent_"
                    }
                ]
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=message) as response:
            if response.status == 200:
                print("[OK] Message sent successfully!")
                print("     Check your Slack channel for the test message.")
                return True
            else:
                print(f"[FAIL] Failed to send message")
                print(f"       Status: {response.status}")
                text = await response.text()
                print(f"       Error: {text}")
                return False


def save_config(github_token=None, github_repo=None, slack_webhook=None):
    """Save configuration to .env file"""
    from pathlib import Path

    env_path = Path(__file__).parent.parent / ".env"

    # Read existing
    existing = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing[key] = value

    # Update
    if github_token:
        existing['GITHUB_TOKEN'] = github_token
    if github_repo:
        existing['GITHUB_DEFAULT_REPO'] = github_repo
    if slack_webhook:
        existing['SLACK_WEBHOOK_URL'] = slack_webhook

    # Write
    with open(env_path, 'w') as f:
        f.write("# ALFRED Integration Configuration\n")
        f.write("# Generated by quick_test.py\n\n")
        for key, value in existing.items():
            f.write(f"{key}={value}\n")

    print(f"\n[OK] Configuration saved to: {env_path}")


async def main():
    parser = argparse.ArgumentParser(description="Test ALFRED Integrations")
    parser.add_argument("--github", help="GitHub Personal Access Token")
    parser.add_argument("--repo", help="GitHub repository (owner/repo)")
    parser.add_argument("--slack", help="Slack Webhook URL")
    parser.add_argument("--save", action="store_true", help="Save working config to .env")
    args = parser.parse_args()

    if not args.github and not args.slack:
        print("ALFRED Integration Test")
        print("-" * 50)
        print("\nUsage examples:")
        print("  python quick_test.py --github ghp_xxxx")
        print("  python quick_test.py --github ghp_xxxx --repo owner/repo")
        print("  python quick_test.py --slack https://hooks.slack.com/...")
        print("  python quick_test.py --github ghp_xxxx --slack https://... --save")
        print("\nAdd --save to save working credentials to .env file")
        return

    results = {"github": None, "slack": None}

    if args.github:
        results["github"] = await test_github(args.github, args.repo)

    if args.slack:
        results["slack"] = await test_slack(args.slack)

    # Summary
    print("\n" + "=" * 50)
    print("  TEST SUMMARY")
    print("=" * 50)

    if results["github"] is not None:
        status = "[OK]" if results["github"] else "[FAIL]"
        print(f"  GitHub: {status}")

    if results["slack"] is not None:
        status = "[OK]" if results["slack"] else "[FAIL]"
        print(f"  Slack:  {status}")

    # Save if requested and tests passed
    if args.save:
        save_github = results["github"] is True
        save_slack = results["slack"] is True

        if save_github or save_slack:
            save_config(
                github_token=args.github if save_github else None,
                github_repo=args.repo if save_github and args.repo else None,
                slack_webhook=args.slack if save_slack else None
            )
        else:
            print("\n[SKIP] Not saving - tests did not pass")


if __name__ == "__main__":
    asyncio.run(main())
