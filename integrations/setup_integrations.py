"""
Integration Setup Helper for ALFRED

Interactive setup for GitHub and Slack integrations.
Run this script to configure and test your API keys.

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_instructions():
    """Print instructions for getting API keys"""
    print_header("HOW TO GET YOUR API KEYS")

    print("""
╔══════════════════════════════════════════════════════════════╗
║                     GITHUB TOKEN                              ║
╚══════════════════════════════════════════════════════════════╝

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "ALFRED Security Agent"
4. Select scopes:
   ✓ repo (Full control of private repositories)
   ✓ write:discussion (optional, for comments)
5. Click "Generate token"
6. COPY THE TOKEN NOW - you won't see it again!

╔══════════════════════════════════════════════════════════════╗
║                   SLACK WEBHOOK                               ║
╚══════════════════════════════════════════════════════════════╝

1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "ALFRED Security" and select your workspace
4. Go to "Incoming Webhooks" in the left sidebar
5. Toggle "Activate Incoming Webhooks" to ON
6. Click "Add New Webhook to Workspace"
7. Select the channel (e.g., #security-alerts)
8. Click "Allow"
9. Copy the Webhook URL

""")


async def test_github(token: str, repo: str = None) -> bool:
    """Test GitHub integration"""
    print("\n🔄 Testing GitHub connection...")

    try:
        from github_integration import GitHubIntegration
        gh = GitHubIntegration(token=token, default_repo=repo)

        # Test API access
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GitHub authenticated as: {data.get('login')}")

                    if repo:
                        # Test repo access
                        owner, repo_name = repo.split("/")
                        async with session.get(
                            f"https://api.github.com/repos/{owner}/{repo_name}",
                            headers={"Authorization": f"Bearer {token}"}
                        ) as repo_response:
                            if repo_response.status == 200:
                                print(f"✅ Repository access confirmed: {repo}")
                            else:
                                print(f"⚠️  Cannot access repository: {repo}")

                    return True
                else:
                    print(f"❌ GitHub authentication failed: {response.status}")
                    return False

    except ImportError:
        print("❌ aiohttp not installed. Install with: pip install aiohttp")
        return False
    except Exception as e:
        print(f"❌ GitHub test failed: {e}")
        return False


async def test_slack(webhook_url: str) -> bool:
    """Test Slack integration"""
    print("\n🔄 Testing Slack connection...")

    try:
        from slack_integration import SlackIntegration
        slack = SlackIntegration(webhook_url=webhook_url)

        # Send a test message
        result = await slack.send_message(
            text="🤖 ALFRED Security Agent connected successfully!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *ALFRED Security Agent* is now connected to this channel.\n\nYou will receive security alerts here when vulnerabilities are detected."
                    }
                },
                {
                    "type": "context",
                    "elements": [{
                        "type": "mrkdwn",
                        "text": "_This is a test message from the integration setup._"
                    }]
                }
            ]
        )

        await slack.close()

        if result.get("ok"):
            print("✅ Slack webhook working! Check your channel for the test message.")
            return True
        else:
            print(f"❌ Slack test failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        return False


def save_to_env_file(github_token: str = None, github_repo: str = None,
                     slack_webhook: str = None):
    """Save configuration to .env file"""
    env_path = Path(__file__).parent.parent / ".env"

    # Read existing .env if it exists
    existing = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing[key] = value

    # Update with new values
    if github_token:
        existing['GITHUB_TOKEN'] = github_token
    if github_repo:
        existing['GITHUB_DEFAULT_REPO'] = github_repo
    if slack_webhook:
        existing['SLACK_WEBHOOK_URL'] = slack_webhook

    # Write back
    with open(env_path, 'w') as f:
        f.write("# ALFRED Integration Configuration\n")
        f.write("# Generated by setup_integrations.py\n\n")
        for key, value in existing.items():
            f.write(f"{key}={value}\n")

    print(f"\n✅ Configuration saved to: {env_path}")
    print("   Load with: source .env (Linux/Mac) or use dotenv in Python")


async def interactive_setup():
    """Interactive setup wizard"""
    print_header("ALFRED Integration Setup")

    print("""
This wizard will help you set up GitHub and Slack integrations
for the ALFRED Security Agent.
""")

    # Show instructions
    show_instructions = input("Do you need instructions on getting API keys? (y/N): ").strip().lower()
    if show_instructions == 'y':
        print_instructions()
        input("\nPress Enter when you have your keys ready...")

    # GitHub setup
    print_header("GITHUB SETUP")
    github_token = input("Enter your GitHub Personal Access Token (or press Enter to skip): ").strip()
    github_repo = None

    if github_token:
        github_repo = input("Enter default repository (owner/repo) or press Enter to skip: ").strip()

        # Test it
        if await test_github(github_token, github_repo or None):
            print("✅ GitHub integration ready!")
        else:
            print("⚠️  GitHub test failed, but configuration saved. Check your token.")

    # Slack setup
    print_header("SLACK SETUP")
    slack_webhook = input("Enter your Slack Webhook URL (or press Enter to skip): ").strip()

    if slack_webhook:
        if await test_slack(slack_webhook):
            print("✅ Slack integration ready!")
        else:
            print("⚠️  Slack test failed. Check your webhook URL.")

    # Save configuration
    if github_token or slack_webhook:
        print_header("SAVING CONFIGURATION")
        save = input("Save configuration to .env file? (Y/n): ").strip().lower()
        if save != 'n':
            save_to_env_file(
                github_token=github_token if github_token else None,
                github_repo=github_repo if github_repo else None,
                slack_webhook=slack_webhook if slack_webhook else None
            )

    # Summary
    print_header("SETUP COMPLETE")
    print(f"""
Configuration Summary:
  GitHub Token:  {'✅ Configured' if github_token else '❌ Not set'}
  GitHub Repo:   {github_repo if github_repo else 'Not set'}
  Slack Webhook: {'✅ Configured' if slack_webhook else '❌ Not set'}

To use these in your current session, set environment variables:
""")

    if github_token:
        print(f'  set GITHUB_TOKEN={github_token[:20]}...')
    if github_repo:
        print(f'  set GITHUB_DEFAULT_REPO={github_repo}')
    if slack_webhook:
        print(f'  set SLACK_WEBHOOK_URL={slack_webhook[:40]}...')

    print("""
Or load from .env file in Python:
  from dotenv import load_dotenv
  load_dotenv()
""")


async def quick_test():
    """Quick test of existing configuration"""
    print_header("TESTING EXISTING CONFIGURATION")

    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_DEFAULT_REPO")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    results = {"github": False, "slack": False}

    if github_token:
        results["github"] = await test_github(github_token, github_repo)
    else:
        print("⚠️  GITHUB_TOKEN not set")

    if slack_webhook:
        results["slack"] = await test_slack(slack_webhook)
    else:
        print("⚠️  SLACK_WEBHOOK_URL not set")

    print_header("TEST RESULTS")
    print(f"  GitHub: {'✅ Working' if results['github'] else '❌ Not working'}")
    print(f"  Slack:  {'✅ Working' if results['slack'] else '❌ Not working'}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ALFRED Integration Setup")
    parser.add_argument("--test", action="store_true", help="Test existing configuration")
    parser.add_argument("--instructions", action="store_true", help="Show instructions only")
    args = parser.parse_args()

    if args.instructions:
        print_instructions()
    elif args.test:
        asyncio.run(quick_test())
    else:
        asyncio.run(interactive_setup())
