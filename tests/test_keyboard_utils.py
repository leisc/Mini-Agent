"""Test suite for keyboard utilities."""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path to import mini_agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mini_agent.utils.keyboard_utils import (
    KeyboardListener,
    start_keyboard_listener,
    stop_keyboard_listener,
    is_esc_pressed,
    get_keyboard_listener,
)


class TestKeyboardUtils:
    """Test cases for keyboard utilities."""

    @staticmethod
    def test_keyboard_listener_initialization():
        """Test that keyboard listener can be initialized."""
        print("\n1. Testing keyboard listener initialization...")
        listener = KeyboardListener()
        assert listener is not None
        print("✓ KeyboardListener created successfully")

    @staticmethod
    def test_keyboard_listener_start_stop():
        """Test starting and stopping the listener."""
        print("\n2. Testing start/stop functionality...")
        listener = KeyboardListener()
        listener.start()
        assert listener.is_esc_pressed() == False
        listener.stop()
        print("✓ Start/stop functionality works")

    @staticmethod
    def test_is_esc_pressed_no_key():
        """Test is_esc_pressed when no key is pressed."""
        print("\n3. Testing is_esc_pressed with no key pressed...")
        listener = KeyboardListener()
        listener.start()
        result = listener.is_esc_pressed()
        listener.stop()
        assert result == False
        print("✓ Returns False when no key pressed")

    @staticmethod
    def test_global_listener():
        """Test the global keyboard listener functions."""
        print("\n4. Testing global listener functions...")
        # Get global listener
        listener = get_keyboard_listener()
        assert listener is not None

        # Start it
        start_keyboard_listener()
        assert listener.is_esc_pressed() == False

        # Stop it
        stop_keyboard_listener()
        print("✓ Global listener functions work correctly")

    @staticmethod
    def test_esc_press_detection():
        """Test ESC key detection (simulated)."""
        print("\n5. Testing ESC key detection...")
        listener = KeyboardListener()
        listener.start()

        # Simulate ESC press by setting current_key
        with listener._lock:
            listener._current_key = '\x1b'

        result = listener.is_esc_pressed()
        listener.stop()

        assert result == True
        print("✓ ESC key detection works")

    @staticmethod
    async def test_esc_press_in_async():
        """Test ESC key detection in async context."""
        print("\n6. Testing ESC in async context...")

        async def check_esc():
            """Function that checks for ESC press."""
            start_keyboard_listener()
            await asyncio.sleep(0.1)
            result = is_esc_pressed()
            stop_keyboard_listener()
            return result

        result = await check_esc()
        assert result == False or result is None
        print("✓ ESC detection works in async context")

    @staticmethod
    def test_keyboard_listener_cleanup():
        """Test that listener thread is properly cleaned up."""
        print("\n7. Testing listener cleanup...")

        listener = KeyboardListener()
        listener.start()

        # Give thread a moment to start
        time.sleep(0.1)

        # Stop the listener
        listener.stop()

        # Give thread a moment to stop
        time.sleep(0.1)

        # Should be stopped
        assert listener._listener_thread is None or not listener._listener_thread.is_alive()
        print("✓ Listener cleanup works correctly")

    @staticmethod
    def run_all_tests():
        """Run all test cases."""
        print("=" * 60)
        print("Keyboard Utilities Test Suite")
        print("=" * 60)

        tests = [
            test_keyboard_listener_initialization,
            test_keyboard_listener_start_stop,
            test_is_esc_pressed_no_key,
            test_global_listener,
            test_esc_press_detection,
            test_esc_press_in_async,
            test_keyboard_listener_cleanup,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"✗ Test failed: {e}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"Test Results: {passed} passed, {failed} failed")
        print("=" * 60)

        return failed == 0


if __name__ == "__main__":
    success = TestKeyboardUtils.run_all_tests()
    sys.exit(0 if success else 1)
