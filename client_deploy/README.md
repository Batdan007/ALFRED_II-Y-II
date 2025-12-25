# ALFRED II-Y-II Client Deployment

## For BATDAN Only

This folder contains tools to deploy protected ALFRED instances to clients.

## How It Works

1. **License Key System** - Each client gets a unique key tied to their machine
2. **Code Obfuscation** - Core logic is compiled to .pyc (not readable)
3. **Phone Home** - Client checks license on startup
4. **Time Bomb** - License expires, requires renewal

## Usage

```bash
# Generate license for new client
python license_generator.py --client "Client Name" --email "client@email.com" --days 30

# Build protected client package
python build_client.py --license LICENSE_KEY_HERE

# Install on client machine
# (You do this in person or via remote desktop)
```

## Pricing Tiers

| Tier | Price | Features |
|------|-------|----------|
| Basic | $29/mo | Terminal only, 1 AI provider |
| Pro | $99/mo | All features, 3 AI providers |
| Enterprise | $299/mo | Full access, all providers, priority support |

## Client Files (What They Get)

```
alfred_client/
├── alfred.exe          # Compiled launcher
├── config.json         # Their settings (no API keys visible)
├── license.key         # Their unique license
└── lib/                # Obfuscated Python files
```

## What They DON'T Get

- Source code (.py files)
- Your API keys
- Brain architecture details
- MCP servers (unless Enterprise)
- Ability to copy to another machine
