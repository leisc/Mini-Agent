"""Keyboard input utilities for handling special keys like ESC.

This module provides cross-platform support for capturing keyboard input,
particularly the ESC key for interrupting agent execution.
"""

import sys
import platform
import threading


class KeyboardListener:
    """Listener for keyboard events in a non-blocking manner."""

    def __init__(self):
        self._should_stop = False
        self._lock = threading.Lock()
        self._current_key = None
        self._listener_thread = None

    def start(self):
        """Start the keyboard listener thread."""
        if self._listener_thread is not None and self._listener_thread.is_alive():
            return  # Already running

        self._should_stop = False
        self._current_key = None
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()

    def stop(self):
        """Stop the keyboard listener thread."""
        with self._lock:
            self._should_stop = True

    def _listen(self):
        """Listen for keyboard input in a separate thread."""
        if platform.system() == "Windows":
            self._listen_windows()
        else:
            self._listen_unix()

    def _listen_unix(self):
        """Listen for keyboard input on Unix-like systems."""
        try:
            import tty
            import termios
        except ImportError:
            return

        # Save terminal settings
        old_settings = None
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            # Set terminal to raw mode
            tty.setraw(fd)

            while True:
                with self._lock:
                    if self._should_stop:
                        break

                # Read a single character
                ch = sys.stdin.read(1)

                with self._lock:
                    self._current_key = ch

                # Check for ESC key (ASCII 27)
                if ch == '\x1b':
                    # Check if it's ESC followed by something
                    # Common sequences: ESC [ or ESC O
                    next_char = sys.stdin.read(1)
                    if next_char:
                        # ESC + character sequence (e.g., ESC [ for cursor keys)
                        self._current_key = ch + next_char
                    else:
                        # Just ESC alone
                        self._current_key = ch

        except Exception:
            pass
        finally:
            # Restore terminal settings
            if old_settings is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass

    def _listen_windows(self):
        """Listen for keyboard input on Windows."""
        try:
            import msvcrt

            while True:
                with self._lock:
                    if self._should_stop:
                        break

                # Check if there's a key available
                if msvcrt.kbhit():
                    ch = msvcrt.getch()

                    # Check for ESC (ASCII 27)
                    if ord(ch) == 27:
                        # Try to read more characters for sequences
                        next_char = msvcrt.getch()
                        if next_char:
                            self._current_key = ch + next_char
                        else:
                            self._current_key = ch

        except Exception:
            pass

    def is_esc_pressed(self) -> bool:
        """Check if ESC key was pressed.

        Returns:
            True if ESC (or ESC+sequence) was pressed, False otherwise
        """
        with self._lock:
            key = self._current_key
            self._current_key = None  # Reset after reading
            return key == '\x1b' or (key and len(key) > 1 and key[0] == '\x1b')

    def get_current_key(self) -> str | None:
        """Get the last pressed key.

        Returns:
            The last key pressed, or None if no key was pressed
        """
        with self._lock:
            key = self._current_key
            self._current_key = None  # Reset after reading
            return key


# Global keyboard listener instance
_keyboard_listener = None


def get_keyboard_listener() -> KeyboardListener:
    """Get or create the global keyboard listener instance.

    Returns:
        KeyboardListener instance
    """
    global _keyboard_listener
    if _keyboard_listener is None:
        _keyboard_listener = KeyboardListener()
    return _keyboard_listener


def start_keyboard_listener():
    """Start the global keyboard listener."""
    listener = get_keyboard_listener()
    listener.start()


def stop_keyboard_listener():
    """Stop the global keyboard listener."""
    listener = get_keyboard_listener()
    listener.stop()


def is_esc_pressed() -> bool:
    """Check if ESC key was pressed.

    This is a convenience function that wraps the keyboard listener.

    Returns:
        True if ESC was pressed, False otherwise
    """
    listener = get_keyboard_listener()
    return listener.is_esc_pressed()
