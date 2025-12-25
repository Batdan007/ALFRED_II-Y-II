"""
Test Core ALFRED-UBX Modules
Author: Daniel J Rita (BATDAN)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all core modules can be imported"""
    print("="*60)
    print("TESTING ALFRED-UBX CORE MODULES")
    print("="*60)

    try:
        from core.brain import AlfredBrain
        print("✅ AlfredBrain imported successfully")
    except Exception as e:
        print(f"❌ AlfredBrain import failed: {e}")
        return False

    try:
        from core.path_manager import PathManager
        print("✅ PathManager imported successfully")
    except Exception as e:
        print(f"❌ PathManager import failed: {e}")
        return False

    try:
        from core.config_loader import ConfigLoader
        print("✅ ConfigLoader imported successfully")
    except Exception as e:
        print(f"❌ ConfigLoader import failed: {e}")
        return False

    try:
        from core.privacy_controller import PrivacyController, PrivacyMode, CloudProvider
        print("✅ PrivacyController imported successfully")
    except Exception as e:
        print(f"❌ PrivacyController import failed: {e}")
        return False

    try:
        from core.ui_launcher import UILauncher, UIMode
        print("✅ UILauncher imported successfully")
    except Exception as e:
        print(f"❌ UILauncher import failed: {e}")
        return False

    try:
        from core.context_manager import ContextManager
        print("✅ ContextManager imported successfully")
    except Exception as e:
        print(f"❌ ContextManager import failed: {e}")
        return False

    return True


def test_privacy_controller():
    """Test Privacy Controller"""
    print("\n" + "="*60)
    print("TESTING PRIVACY CONTROLLER")
    print("="*60)

    from core.privacy_controller import PrivacyController, PrivacyMode, CloudProvider

    # Create controller in local mode
    controller = PrivacyController(default_mode=PrivacyMode.LOCAL)

    # Test local-only status
    assert controller.is_local_only(), "Should be local-only by default"
    assert not controller.is_cloud_enabled(), "Cloud should be disabled by default"
    print("✅ Default mode is LOCAL")

    # Test status
    status = controller.get_status()
    assert status['mode'] == 'local', "Mode should be 'local'"
    assert status['status_icon'] == '🔒 LOCAL', "Status icon should be 🔒 LOCAL"
    print(f"✅ Status: {status['status_icon']}")

    # Test cloud request (should deny by default)
    approved = controller.request_cloud_access(CloudProvider.CLAUDE, "testing")
    assert not approved, "Cloud access should be denied by default"
    print("✅ Cloud access denied by default (privacy preserved)")

    # Test with auto-confirm
    controller_auto = PrivacyController(default_mode=PrivacyMode.LOCAL, auto_confirm=True)
    approved = controller_auto.request_cloud_access(CloudProvider.CLAUDE, "auto-approve test")
    assert approved, "Cloud access should be approved with auto_confirm=True"
    assert controller_auto.is_cloud_enabled(), "Cloud should be enabled after approval"
    print("✅ Cloud access works with auto-confirm")

    # Test disable all
    controller_auto.disable_all_cloud()
    assert controller_auto.is_local_only(), "Should return to local mode"
    print("✅ Disable all cloud returns to local mode")

    print("\n✅ Privacy Controller: ALL TESTS PASSED")
    return True


def test_ui_launcher():
    """Test UI Launcher"""
    print("\n" + "="*60)
    print("TESTING UI LAUNCHER")
    print("="*60)

    from core.ui_launcher import UILauncher, UIMode

    launcher = UILauncher()

    # Test visual trigger detection
    test_inputs = [
        ("show me a diagram", UIMode.VISUAL_VIEWER),
        ("display the wiring schematic", UIMode.VISUAL_VIEWER),
        ("show building plans", UIMode.DOCUMENT_VIEWER),
        ("compare models", UIMode.MULTIMODEL_DASHBOARD),
        ("show agent dashboard", UIMode.AGENT_DASHBOARD),
        ("what is 2+2", None),  # Should not trigger UI
    ]

    for user_input, expected_mode in test_inputs:
        detected = launcher.should_launch_ui(user_input)
        if expected_mode:
            assert detected == expected_mode, f"Failed to detect {expected_mode} for '{user_input}'"
            print(f"✅ Detected {expected_mode.value} for: '{user_input}'")
        else:
            assert detected is None, f"Incorrectly detected UI for '{user_input}'"
            print(f"✅ Correctly no UI for: '{user_input}'")

    # Test enable/disable
    launcher.disable_ui()
    assert not launcher.ui_enabled, "UI should be disabled"
    print("✅ UI disable works")

    launcher.enable_ui()
    assert launcher.ui_enabled, "UI should be enabled"
    print("✅ UI enable works")

    print("\n✅ UI Launcher: ALL TESTS PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ALFRED-UBX CORE SYSTEM TEST SUITE")
    print("="*60 + "\n")

    all_passed = True

    # Run tests
    if not test_imports():
        print("\n❌ Import tests failed")
        all_passed = False
    else:
        # Only run other tests if imports work
        if not test_privacy_controller():
            all_passed = False

        if not test_ui_launcher():
            all_passed = False

    # Final summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    if all_passed:
        print("✅ ALL TESTS PASSED - CORE SYSTEM READY")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - SEE ABOVE")
        sys.exit(1)
