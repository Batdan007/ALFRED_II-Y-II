#!/usr/bin/env python3
"""
Test MCP Servers

Quick test to verify all MCP servers can initialize properly.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test that all MCP servers can be imported"""
    results = {}

    print("Testing MCP Server Imports...")
    print("=" * 60)

    # Add mcp directory to path
    mcp_dir = Path(__file__).parent
    if str(mcp_dir) not in sys.path:
        sys.path.insert(0, str(mcp_dir))

    # Test ALFRED MCP Server
    try:
        import alfred_mcp_server
        results['alfred_mcp_server'] = "✓ OK"
    except Exception as e:
        results['alfred_mcp_server'] = f"✗ FAIL: {e}"

    # Test CAMDAN MCP Server
    try:
        import camdan_mcp_server
        results['camdan_mcp_server'] = "✓ OK"
    except Exception as e:
        results['camdan_mcp_server'] = f"✗ FAIL: {e}"

    # Test Strix MCP Server
    try:
        import strix_mcp_server
        results['strix_mcp_server'] = "✓ OK"
    except Exception as e:
        results['strix_mcp_server'] = f"✗ FAIL: {e}"

    # Test DontLookUp MCP Server
    try:
        import dontlookup_mcp_server
        results['dontlookup_mcp_server'] = "✓ OK"
    except Exception as e:
        results['dontlookup_mcp_server'] = f"✗ FAIL: {e}"

    # Test CAIPE MCP Server
    try:
        import caipe_mcp_server
        results['caipe_mcp_server'] = "✓ OK"
    except Exception as e:
        results['caipe_mcp_server'] = f"✗ FAIL: {e}"

    # Test Crawl4AI MCP Server
    try:
        import crawl4ai_mcp_server
        results['crawl4ai_mcp_server'] = "✓ OK"
    except Exception as e:
        results['crawl4ai_mcp_server'] = f"✗ FAIL: {e}"

    # Test Security Agent MCP Server
    try:
        import security_agent_mcp_server
        results['security_agent_mcp_server'] = "✓ OK"
    except Exception as e:
        results['security_agent_mcp_server'] = f"✗ FAIL: {e}"

    # Print results
    for server, result in results.items():
        print(f"{server:25} {result}")

    print("=" * 60)

    # Summary
    passed = sum(1 for r in results.values() if r.startswith("✓"))
    total = len(results)

    print(f"\nSummary: {passed}/{total} servers imported successfully")

    if passed == total:
        print("✓ All MCP servers ready!")
        return True
    else:
        print("⚠ Some MCP servers failed to import")
        return False


def test_server_initialization():
    """Test that servers can be initialized"""
    print("\n\nTesting MCP Server Initialization...")
    print("=" * 60)

    results = {}

    # Test ALFRED server
    try:
        from alfred_mcp_server import AlfredMCPServer
        server = AlfredMCPServer()
        results['alfred'] = f"✓ OK - {server.server.name}"
    except Exception as e:
        results['alfred'] = f"✗ FAIL: {e}"

    # Test CAMDAN server
    try:
        from camdan_mcp_server import CAMDANMCPServer
        server = CAMDANMCPServer()
        results['camdan'] = f"✓ OK - {server.server.name}"
    except Exception as e:
        results['camdan'] = f"✗ FAIL: {e}"

    # Test Strix server
    try:
        from strix_mcp_server import StrixMCPServer
        server = StrixMCPServer()
        results['strix'] = f"✓ OK - {server.server.name}"
    except Exception as e:
        results['strix'] = f"✗ FAIL: {e}"

    # Test DontLookUp server
    try:
        from dontlookup_mcp_server import DontLookUpMCPServer
        server = DontLookUpMCPServer()
        results['dontlookup'] = f"✓ OK - {server.server.name}"
    except Exception as e:
        results['dontlookup'] = f"✗ FAIL: {e}"

    # Test CAIPE server
    try:
        from caipe_mcp_server import CAIPEMCPServer
        server = CAIPEMCPServer()
        results['caipe'] = f"✓ OK - {server.server.name}"
    except Exception as e:
        results['caipe'] = f"✗ FAIL: {e}"

    # Test Crawl4AI server
    try:
        from crawl4ai_mcp_server import Crawl4AIMCPServer
        server = Crawl4AIMCPServer()
        if server.server:
            results['crawl4ai'] = f"✓ OK - {server.server.name}"
        else:
            results['crawl4ai'] = "⚠ Degraded - MCP not installed"
    except Exception as e:
        results['crawl4ai'] = f"✗ FAIL: {e}"

    # Test Security Agent server
    try:
        import security_agent_mcp_server
        # Just check if the module loads
        results['security_agent'] = "✓ OK - security-agent"
    except Exception as e:
        results['security_agent'] = f"✗ FAIL: {e}"

    # Print results
    for server, result in results.items():
        print(f"{server:25} {result}")

    print("=" * 60)

    # Summary
    passed = sum(1 for r in results.values() if r.startswith("✓"))
    total = len(results)

    print(f"\nSummary: {passed}/{total} servers initialized successfully")

    if passed == total:
        print("✓ All MCP servers initialized!")
        return True
    else:
        print("⚠ Some MCP servers failed to initialize")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n\nChecking Dependencies...")
    print("=" * 60)

    results = {}

    # Check MCP library
    try:
        import mcp
        results['mcp'] = f"✓ Installed - v{getattr(mcp, '__version__', 'unknown')}"
    except ImportError:
        results['mcp'] = "✗ Not installed - Run: pip install mcp"

    # Check ALFRED brain
    try:
        from core.brain import AlfredBrain
        results['alfred-brain'] = "✓ Available"
    except ImportError as e:
        results['alfred-brain'] = f"✗ Not available: {e}"

    # Check Strix (optional)
    try:
        from capabilities.security.strix_scanner import StrixScanner
        results['strix'] = "✓ Available"
    except ImportError:
        results['strix'] = "⚠ Optional - Install with: pipx install strix-agent"

    # Check CAMDAN tool (optional)
    try:
        from tools.camdan_tool import query_engineering_knowledge
        results['camdan'] = "✓ Available"
    except ImportError:
        results['camdan'] = "⚠ Optional - Requires CAMDAN installation"

    # Print results
    for dep, result in results.items():
        print(f"{dep:25} {result}")

    print("=" * 60)


def main():
    """Run all tests"""
    print("\nALFRED MCP Server Test Suite")
    print("=" * 60 + "\n")

    # Check dependencies
    check_dependencies()

    # Test imports
    imports_ok = test_imports()

    # Test initialization
    init_ok = test_server_initialization()

    # Final status
    print("\n\n" + "=" * 60)
    if imports_ok and init_ok:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nMCP servers are ready to use with Claude Code!")
        print("\nNext steps:")
        print("1. Copy mcp/claude_code_config.json to Claude Code's config directory")
        print("2. Update paths in the config to match your installation")
        print("3. Restart Claude Code")
        print("4. Test with: 'Use alfred_get_memory_stats to show brain statistics'")
    else:
        print("⚠⚠⚠ SOME TESTS FAILED ⚠⚠⚠")
        print("\nCheck error messages above and:")
        print("1. Install missing dependencies: pip install mcp")
        print("2. Fix import errors")
        print("3. Rerun tests: python mcp/test_mcp_servers.py")

    print("=" * 60)


if __name__ == "__main__":
    main()
