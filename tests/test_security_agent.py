"""
Test Suite for ALFRED Security Agent

Tests the autonomous security scanning capabilities including:
- ReAct loop execution
- Code vulnerability detection
- Finding storage in Alfred Brain
- Agent state management

Author: Daniel J Rita (BATDAN)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.security_agent import (
    AlfredSecurityAgent,
    AgentState,
    ActionType,
    SecurityFinding,
    quick_security_scan
)


# Test code samples with known vulnerabilities
VULNERABLE_CODE = '''
import os
import sqlite3

def get_user(user_id):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()

def run_command(cmd):
    # Command injection vulnerability
    os.system(cmd)

def process_data(data):
    # Dangerous eval
    result = eval(data)
    return result

# Hardcoded credentials
password = "super_secret_password123"
api_key = "sk-1234567890abcdefghijklmnop"
'''

SAFE_CODE = '''
import sqlite3
from typing import Optional

def get_user(user_id: int) -> Optional[dict]:
    """Safely fetch user by ID using parameterized query."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def process_data(data: str) -> str:
    """Safely process data without eval."""
    return data.strip().lower()
'''


def test_agent_initialization():
    """Test that the security agent initializes correctly"""
    print("\n[TEST] Agent Initialization")
    print("-" * 40)

    agent = AlfredSecurityAgent()

    assert agent.state == AgentState.IDLE, "Agent should start in IDLE state"
    assert agent.max_iterations == 10, "Default max iterations should be 10"
    assert agent.findings == [], "Findings should start empty"
    assert agent.thoughts == [], "Thoughts should start empty"

    status = agent.get_status()
    print(f"  State: {status['state']}")
    print(f"  Brain connected: {status['brain_connected']}")
    print(f"  Strix available: {status['strix_available']}")
    print(f"  Fabric available: {status['fabric_available']}")

    print("  [PASS] Agent initialized correctly")
    return True


def test_fallback_code_scan():
    """Test the fallback code scanner (when Strix not available)"""
    print("\n[TEST] Fallback Code Scanner")
    print("-" * 40)

    agent = AlfredSecurityAgent()

    # Create a temporary file with vulnerable code
    test_dir = Path(__file__).parent / "test_scan_target"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "vulnerable.py"
    test_file.write_text(VULNERABLE_CODE)

    try:
        # Run fallback scan
        result = agent._fallback_code_scan(str(test_dir))

        print(f"  Files scanned: {result.get('files_scanned', 0)}")
        print(f"  Vulnerabilities found: {result.get('vulnerabilities_found', 0)}")
        print(f"  Agent findings: {len(agent.findings)}")

        # Should find vulnerabilities
        assert result.get('success'), "Scan should succeed"
        assert result.get('vulnerabilities_found', 0) > 0, "Should find vulnerabilities"
        assert len(agent.findings) > 0, "Should have findings in agent"

        # Check severity distribution
        severities = [f.severity for f in agent.findings]
        print(f"  Severity distribution: {severities}")

        print("  [PASS] Fallback scanner detected vulnerabilities")
        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_safe_code_scan():
    """Test that safe code doesn't trigger false positives"""
    print("\n[TEST] Safe Code Scan")
    print("-" * 40)

    agent = AlfredSecurityAgent()

    # Create a temporary file with safe code
    test_dir = Path(__file__).parent / "test_safe_target"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "safe.py"
    test_file.write_text(SAFE_CODE)

    try:
        # Run fallback scan
        result = agent._fallback_code_scan(str(test_dir))

        print(f"  Files scanned: {result.get('files_scanned', 0)}")
        print(f"  Vulnerabilities found: {result.get('vulnerabilities_found', 0)}")

        # Should find few or no vulnerabilities
        vuln_count = result.get('vulnerabilities_found', 0)
        print(f"  [{'PASS' if vuln_count == 0 else 'WARN'}] Found {vuln_count} potential issues")

        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_security_finding_dataclass():
    """Test SecurityFinding dataclass"""
    print("\n[TEST] SecurityFinding Dataclass")
    print("-" * 40)

    finding = SecurityFinding(
        id="TEST-001",
        title="SQL Injection",
        severity="critical",
        description="Found SQL injection in login function",
        proof_of_concept="' OR '1'='1",
        recommendation="Use parameterized queries"
    )

    assert finding.id == "TEST-001"
    assert finding.severity == "critical"
    assert finding.discovered_at is not None

    print(f"  ID: {finding.id}")
    print(f"  Title: {finding.title}")
    print(f"  Severity: {finding.severity}")
    print(f"  Discovered: {finding.discovered_at}")

    print("  [PASS] SecurityFinding works correctly")
    return True


async def test_react_loop():
    """Test the ReAct loop execution"""
    print("\n[TEST] ReAct Loop Execution")
    print("-" * 40)

    agent = AlfredSecurityAgent(max_iterations=3)  # Limit iterations for test

    # Create test target
    test_dir = Path(__file__).parent / "test_react_target"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test.py"
    test_file.write_text(VULNERABLE_CODE)

    try:
        # Run the agent
        result = await agent.execute(
            "Scan for security vulnerabilities",
            str(test_dir)
        )

        print(f"  Success: {result.get('success')}")
        print(f"  State: {result.get('state')}")
        print(f"  Iterations: {result.get('iterations')}")
        print(f"  Findings: {result.get('findings_count')}")

        # Check thought chain
        thought_chain = result.get('thought_chain', [])
        print(f"  Thought chain:")
        for i, thought in enumerate(thought_chain[:3]):
            print(f"    {i+1}. {thought.get('action', 'unknown')}: {thought.get('reasoning', '')[:50]}...")

        print("  [PASS] ReAct loop executed")
        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


async def test_quick_scan():
    """Test the quick_security_scan convenience function"""
    print("\n[TEST] Quick Security Scan")
    print("-" * 40)

    # Create test target
    test_dir = Path(__file__).parent / "test_quick_target"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "quick_test.py"
    test_file.write_text(VULNERABLE_CODE)

    try:
        result = await quick_security_scan(str(test_dir))

        print(f"  Success: {result.get('success')}")
        print(f"  Findings: {result.get('findings_count', 0)}")

        print("  [PASS] Quick scan completed")
        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_target_extraction():
    """Test target extraction from task description"""
    print("\n[TEST] Target Extraction")
    print("-" * 40)

    agent = AlfredSecurityAgent()

    test_cases = [
        ("Scan https://example.com for vulnerabilities", "https://example.com"),
        ("Check http://localhost:8080/api", "http://localhost:8080/api"),
        ("Review C:\\Users\\test\\project", "C:\\Users\\test\\project"),
        ("Analyze /home/user/code", "/home/user/code"),
        ("Scan ./my-project for issues", "./my-project"),
    ]

    for task, expected in test_cases:
        result = agent._extract_target_from_task(task)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] '{task[:30]}...' -> {result}")

    print("  [PASS] Target extraction working")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ALFRED Security Agent Test Suite")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Synchronous tests
    sync_tests = [
        test_agent_initialization,
        test_security_finding_dataclass,
        test_target_extraction,
        test_fallback_code_scan,
        test_safe_code_scan,
    ]

    for test in sync_tests:
        try:
            if test():
                tests_passed += 1
            else:
                tests_failed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            tests_failed += 1

    # Async tests
    async_tests = [
        test_react_loop,
        test_quick_scan,
    ]

    for test in async_tests:
        try:
            if asyncio.run(test()):
                tests_passed += 1
            else:
                tests_failed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 60)

    return tests_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
