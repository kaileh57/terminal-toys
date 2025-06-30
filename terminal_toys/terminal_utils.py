#!/usr/bin/env python3
"""
Cross-platform terminal utilities for terminal toys
Works on Windows, macOS, Linux, and WSL
"""

import os
import sys
import time
import platform
import shutil
from typing import Optional

# Detect platform
def is_wsl():
    """Detect if running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_WSL = is_wsl()
IS_UNIX = not IS_WINDOWS

# Import platform-specific modules with error handling
if IS_WINDOWS:
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    try:
        import termios
        import tty
        import select
        import fcntl
    except ImportError:
        termios = tty = select = fcntl = None

def flush_output():
    """Force flush stdout to ensure rendering"""
    try:
        sys.stdout.flush()
    except:
        pass

def clear_screen():
    """Clear the terminal screen (cross-platform)"""
    try:
        if IS_WINDOWS:
            os.system('cls')
        else:
            # Use multiple methods for better compatibility
            if IS_WSL:
                # WSL-specific clearing sequence
                print('\033[2J\033[H', end='')
                print('\033[3J', end='')  # Clear scrollback
                flush_output()
            else:
                # Standard Unix clear
                print('\033[2J\033[H', end='')
                flush_output()
    except:
        # Fallback to simple newlines
        print('\n' * 100)
        flush_output()

def move_cursor(x: int, y: int):
    """Move cursor to position (1-indexed)"""
    print(f'\033[{y};{x}H', end='')
    flush_output()

def save_cursor_position():
    """Save current cursor position"""
    print('\033[s', end='')
    flush_output()

def restore_cursor_position():
    """Restore saved cursor position"""
    print('\033[u', end='')
    flush_output()

def enable_ansi_colors():
    """Enable ANSI color support"""
    if IS_WINDOWS:
        # Enable ANSI escape sequences on Windows 10+
        try:
            os.system('color')
            # Alternative method for Windows
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
        except:
            pass
    elif IS_WSL or IS_UNIX:
        # Ensure TERM is set properly for WSL and Unix
        if 'TERM' not in os.environ or os.environ['TERM'] == 'dumb':
            os.environ['TERM'] = 'xterm-256color'
        
        # Enable UTF-8 support
        if 'LANG' not in os.environ:
            os.environ['LANG'] = 'en_US.UTF-8'

def hide_cursor():
    """Hide the terminal cursor"""
    try:
        print('\033[?25l', end='')
        flush_output()
    except:
        pass

def show_cursor():
    """Show the terminal cursor"""
    try:
        print('\033[?25h', end='')
        flush_output()
    except:
        pass

def get_terminal_size():
    """Get terminal size with fallback values"""
    try:
        # Try multiple methods for better WSL compatibility
        if IS_WSL:
            # Try stty first for WSL
            try:
                import subprocess
                result = subprocess.run(['stty', 'size'], 
                                     capture_output=True, 
                                     text=True, 
                                     shell=False)
                if result.returncode == 0:
                    lines, cols = map(int, result.stdout.strip().split())
                    return cols, lines
            except:
                pass
        
        # Standard method
        size = shutil.get_terminal_size()
        # Ensure reasonable size
        cols = max(40, min(size.columns, 200))
        lines = max(20, min(size.lines, 60))
        return cols, lines
    except:
        return 80, 24

def enable_alternate_screen():
    """Switch to alternate screen buffer (for games/animations)"""
    if not IS_WINDOWS:
        print('\033[?1049h', end='')
        flush_output()

def disable_alternate_screen():
    """Switch back to main screen buffer"""
    if not IS_WINDOWS:
        print('\033[?1049l', end='')
        flush_output()

class KeyboardInput:
    """Cross-platform keyboard input handler with WSL support"""
    
    def __init__(self):
        self.old_settings = None
        self.input_mode = 'normal'  # 'normal', 'raw', or 'simple'
        
        if IS_WINDOWS and msvcrt:
            self.input_mode = 'windows'
        elif IS_UNIX and termios and tty:
            try:
                # Try to set raw mode
                self.old_settings = termios.tcgetattr(sys.stdin)
                # Get current settings
                new_settings = termios.tcgetattr(sys.stdin)
                
                if IS_WSL:
                    # WSL-specific terminal settings
                    # Disable canonical mode and echo
                    new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
                    # Set minimal characters for read
                    new_settings[6][termios.VMIN] = 0
                    new_settings[6][termios.VTIME] = 0
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
                else:
                    # Standard Unix raw mode
                    tty.setraw(sys.stdin.fileno())
                
                self.input_mode = 'raw'
                
                # Set non-blocking mode for better responsiveness
                if fcntl:
                    fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
                    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            except:
                # Fall back to simple input
                self.input_mode = 'simple'
        else:
            self.input_mode = 'simple'
    
    def __del__(self):
        """Restore terminal settings"""
        self.cleanup()
    
    def cleanup(self):
        """Manually cleanup terminal settings"""
        if self.old_settings and termios:
            try:
                # Restore blocking mode
                if fcntl and hasattr(sys.stdin, 'fileno'):
                    fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
                    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, fl & ~os.O_NONBLOCK)
                
                # Restore terminal settings
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
                self.old_settings = None
            except:
                pass
    
    def get_key(self, timeout: float = 0) -> Optional[str]:
        """
        Get a single keypress (non-blocking)
        Returns None if no key pressed within timeout
        Returns standardized key names: 'UP', 'DOWN', 'LEFT', 'RIGHT', or the character
        """
        try:
            if self.input_mode == 'windows':
                return self._get_key_windows()
            elif self.input_mode == 'raw':
                return self._get_key_unix_raw(timeout)
            else:
                return self._get_key_simple(timeout)
        except KeyboardInterrupt:
            # Re-raise keyboard interrupt
            raise
        except Exception:
            # If anything else fails, return None
            return None
    
    def _get_key_windows(self) -> Optional[str]:
        """Windows-specific key input"""
        if msvcrt and msvcrt.kbhit():
            try:
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
                    return key.decode('utf-8', errors='ignore')
            except:
                return None
        return None
    
    def _get_key_unix_raw(self, timeout: float) -> Optional[str]:
        """Unix/Linux/macOS/WSL-specific key input using raw mode"""
        if not select:
            return self._get_key_simple(timeout)
            
        try:
            # For WSL, add a small delay to allow buffering
            if IS_WSL and timeout > 0:
                time.sleep(0.001)
            
            # Check if input is available
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                # Read available characters
                chars = ''
                while True:
                    try:
                        char = sys.stdin.read(1)
                        if not char:
                            break
                        chars += char
                        # Check if more characters are immediately available
                        if not select.select([sys.stdin], [], [], 0)[0]:
                            break
                    except (OSError, IOError):
                        break
                
                if not chars:
                    return None
                
                # Parse the input
                if len(chars) == 1:
                    # Single character
                    if chars == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    elif chars == '\r' or chars == '\n':  # Enter
                        return '\n'
                    else:
                        return chars
                else:
                    # Multi-character sequence (likely escape sequence)
                    if chars.startswith('\x1b'):
                        # Arrow keys and other escape sequences
                        if chars == '\x1b[A' or chars == '\x1bOA':
                            return 'UP'
                        elif chars == '\x1b[B' or chars == '\x1bOB':
                            return 'DOWN'
                        elif chars == '\x1b[C' or chars == '\x1bOC':
                            return 'RIGHT'
                        elif chars == '\x1b[D' or chars == '\x1bOD':
                            return 'LEFT'
                        elif len(chars) == 1:
                            return '\x1b'  # Just ESC
                    
                    # Return first character if we can't parse the sequence
                    return chars[0] if chars else None
        except:
            return None
        
        return None
    
    def _get_key_simple(self, timeout: float) -> Optional[str]:
        """Simple fallback input method"""
        # This is a blocking input, so we can't properly implement timeout
        # But it's better than nothing for environments where raw mode fails
        try:
            import threading
            result = [None]
            
            def get_input():
                try:
                    result[0] = input()
                except:
                    pass
            
            thread = threading.Thread(target=get_input)
            thread.daemon = True
            thread.start()
            thread.join(timeout if timeout > 0 else 1.0)
            
            if result[0] is not None and result[0]:
                # Map common inputs
                inp = result[0].lower()
                if inp == 'w':
                    return 'UP'
                elif inp == 's':
                    return 'DOWN'
                elif inp == 'a':
                    return 'LEFT'
                elif inp == 'd':
                    return 'RIGHT'
                else:
                    return result[0][0]
        except:
            pass
        
        return None

# Test function
def test_terminal():
    """Test terminal functionality"""
    print(f"Platform: {platform.system()}")
    print(f"Is Windows: {IS_WINDOWS}")
    print(f"Is WSL: {IS_WSL}")
    print(f"Terminal size: {get_terminal_size()}")
    
    enable_ansi_colors()
    
    # Test colors
    print("\nColor test:")
    colors = [
        ('\033[91m', 'Red'),
        ('\033[92m', 'Green'),
        ('\033[93m', 'Yellow'),
        ('\033[94m', 'Blue'),
        ('\033[95m', 'Magenta'),
        ('\033[96m', 'Cyan'),
    ]
    
    for color_code, color_name in colors:
        print(f"{color_code}{color_name}\033[0m", end=' ')
    print()
    flush_output()
    
    # Test screen clearing
    print("\nPress Enter to test screen clearing...")
    input()
    clear_screen()
    print("Screen cleared! You should see this at the top.")
    
    # Test cursor movement
    print("\nTesting cursor movement...")
    save_cursor_position()
    move_cursor(10, 5)
    print("This text is at position (10, 5)")
    restore_cursor_position()
    print("Back to original position")
    
    # Test keyboard input
    print("\nKeyboard test - Press keys (q to quit):")
    print("Arrow keys should show as UP/DOWN/LEFT/RIGHT")
    print("Press WASD as fallback for arrow keys")
    kb = KeyboardInput()
    
    try:
        while True:
            key = kb.get_key(0.1)
            if key:
                print(f"Key pressed: {repr(key)}")
                flush_output()
                if key == 'q' or key == 'Q':
                    break
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        kb.cleanup()
        show_cursor()

if __name__ == "__main__":
    test_terminal() 