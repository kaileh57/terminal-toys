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
        elif IS_WSL:
            # For WSL, use a combination of methods
            print('\033[H\033[J', end='')
            sys.stdout.write('\033[2J\033[H')
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
    # For WSL, we'll avoid using cursor positioning
    if IS_WSL:
        clear_screen()
    else:
        print(f'\033[{y};{x}H', end='')
        flush_output()

def save_cursor_position():
    """Save current cursor position"""
    if not IS_WSL:
        print('\033[s', end='')
        flush_output()

def restore_cursor_position():
    """Restore saved cursor position"""
    if not IS_WSL:
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
        
        # For WSL specifically, set additional environment variables
        if IS_WSL:
            os.environ['COLUMNS'] = str(shutil.get_terminal_size().columns)
            os.environ['LINES'] = str(shutil.get_terminal_size().lines)

def hide_cursor():
    """Hide the terminal cursor"""
    try:
        sys.stdout.write('\033[?25l')
        flush_output()
    except:
        pass

def show_cursor():
    """Show the terminal cursor"""
    try:
        sys.stdout.write('\033[?25h')
        flush_output()
    except:
        pass

def get_terminal_size():
    """Get terminal size with fallback values"""
    try:
        # Try multiple methods for better WSL compatibility
        if IS_WSL:
            # For WSL, prefer environment variables if set
            if 'COLUMNS' in os.environ and 'LINES' in os.environ:
                try:
                    cols = int(os.environ['COLUMNS'])
                    lines = int(os.environ['LINES'])
                    if cols > 0 and lines > 0:
                        return cols, lines
                except:
                    pass
            
            # Try stty for WSL
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
        cols = max(40, min(size.columns, 120))
        lines = max(20, min(size.lines, 40))
        return cols, lines
    except:
        return 80, 24

def enable_alternate_screen():
    """Switch to alternate screen buffer (for games/animations)"""
    # Disable alternate screen for WSL as it can cause issues
    if not IS_WINDOWS and not IS_WSL:
        print('\033[?1049h', end='')
        flush_output()

def disable_alternate_screen():
    """Switch back to main screen buffer"""
    # Disable alternate screen for WSL as it can cause issues
    if not IS_WINDOWS and not IS_WSL:
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
                    # Use cbreak mode for WSL to avoid issues
                    tty.setcbreak(sys.stdin.fileno())
                else:
                    # Standard Unix raw mode
                    tty.setraw(sys.stdin.fileno())
                
                self.input_mode = 'raw'
                
                # Set non-blocking mode for better responsiveness
                if fcntl and not IS_WSL:  # Avoid non-blocking in WSL
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
                if fcntl and hasattr(sys.stdin, 'fileno') and not IS_WSL:
                    try:
                        fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
                        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, fl & ~os.O_NONBLOCK)
                    except:
                        pass
                
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
            # For WSL, use blocking read with timeout
            if IS_WSL:
                # Set a small timeout for select in WSL
                rlist, _, _ = select.select([sys.stdin], [], [], timeout if timeout > 0 else 0.1)
                if not rlist:
                    return None
                
                # Read one character at a time for WSL
                char = sys.stdin.read(1)
                if not char:
                    return None
                    
                # Check for escape sequences
                if char == '\x1b':
                    # Check if more characters are available
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if rlist:
                        char2 = sys.stdin.read(1)
                        if char2 == '[':
                            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                            if rlist:
                                char3 = sys.stdin.read(1)
                                if char3 == 'A':
                                    return 'UP'
                                elif char3 == 'B':
                                    return 'DOWN'
                                elif char3 == 'C':
                                    return 'RIGHT'
                                elif char3 == 'D':
                                    return 'LEFT'
                    return char  # Just ESC
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif char == '\r' or char == '\n':  # Enter
                    return '\n'
                else:
                    return char
            else:
                # Standard Unix handling
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

# WSL-specific rendering helper
def render_frame_wsl(lines):
    """Render a complete frame for WSL with proper clearing"""
    if IS_WSL:
        # Clear screen and home cursor
        sys.stdout.write('\033[H\033[J')
        # Print all lines at once
        sys.stdout.write('\n'.join(lines))
        sys.stdout.write('\n')
        flush_output()
    else:
        # For non-WSL, just print normally
        print('\n'.join(lines))
        flush_output()

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
    
    # Test screen clearing
    print("\nPress Enter to test screen clearing...")
    input()
    clear_screen()
    print("Screen cleared! You should see this at the top.")
    
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