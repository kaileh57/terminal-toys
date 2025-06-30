#!/usr/bin/env python3
"""
Cross-platform terminal utilities for terminal toys
Works on Windows, macOS, and Linux
"""

import os
import sys
import time
import platform
import shutil
from typing import Optional

# Determine the platform
IS_WINDOWS = platform.system() == 'Windows'

# Import platform-specific modules
if IS_WINDOWS:
    import msvcrt
else:
    import termios
    import tty
    import select

def clear_screen():
    """Clear the terminal screen (cross-platform)"""
    if IS_WINDOWS:
        os.system('cls')
    else:
        os.system('clear')

def enable_ansi_colors():
    """Enable ANSI color support (mainly for Windows)"""
    if IS_WINDOWS:
        # Enable ANSI escape sequences on Windows 10+
        os.system('color')
        # Alternative method for Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def hide_cursor():
    """Hide the terminal cursor"""
    print('\033[?25l', end='', flush=True)

def show_cursor():
    """Show the terminal cursor"""
    print('\033[?25h', end='', flush=True)

def get_terminal_size():
    """Get terminal size with fallback values"""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24

class KeyboardInput:
    """Cross-platform keyboard input handler"""
    
    def __init__(self):
        if not IS_WINDOWS:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
    
    def __del__(self):
        if not IS_WINDOWS and hasattr(self, 'old_settings'):
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def get_key(self, timeout: float = 0) -> Optional[str]:
        """
        Get a single keypress (non-blocking)
        Returns None if no key pressed within timeout
        Returns standardized key names: 'UP', 'DOWN', 'LEFT', 'RIGHT', or the character
        """
        if IS_WINDOWS:
            return self._get_key_windows()
        else:
            return self._get_key_unix(timeout)
    
    def _get_key_windows(self) -> Optional[str]:
        """Windows-specific key input"""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:  # Special keys (arrows, function keys)
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    return 'UP'
                elif key == b'P':  # Down arrow
                    return 'DOWN'
                elif key == b'K':  # Left arrow
                    return 'LEFT'
                elif key == b'M':  # Right arrow
                    return 'RIGHT'
            else:
                try:
                    return key.decode('utf-8', errors='ignore')
                except:
                    return None
        return None
    
    def _get_key_unix(self, timeout: float) -> Optional[str]:
        """Unix/Linux/macOS-specific key input"""
        if select.select([sys.stdin], [], [], timeout)[0]:
            key = sys.stdin.read(1)
            
            # Check for escape sequences (arrow keys)
            if key == '\x1b':  # ESC
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key += sys.stdin.read(1)
                    if key == '\x1b[':  # Arrow key prefix
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            key += sys.stdin.read(1)
                            if key == '\x1b[A':
                                return 'UP'
                            elif key == '\x1b[B':
                                return 'DOWN'
                            elif key == '\x1b[C':
                                return 'RIGHT'
                            elif key == '\x1b[D':
                                return 'LEFT'
                return '\x1b'  # Just ESC key
            
            return key
        return None

# Test the module
if __name__ == "__main__":
    print(f"Platform: {platform.system()}")
    print("Testing keyboard input. Press 'q' to quit.")
    
    enable_ansi_colors()
    kb = KeyboardInput()
    
    while True:
        key = kb.get_key()
        if key:
            print(f"Key pressed: {repr(key)}")
            if key == 'q':
                break 