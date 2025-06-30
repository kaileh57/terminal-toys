#!/usr/bin/env python3
"""
ASCII Clock - Cross-platform analog and digital clock display
Press Q to quit, A/D to switch between analog/digital/both modes
Works on Windows, macOS, and Linux
"""

import sys
import time
import math
from datetime import datetime
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput, flush_output,
    enable_alternate_screen, disable_alternate_screen, move_cursor,
    IS_WSL, render_frame_wsl
)

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
RESET = '\033[0m'

# 7-segment display patterns
DIGITS = {
    '0': ["  ###  ", " #   # ", "#     #", "#     #", "#     #", " #   # ", "  ###  "],
    '1': ["   #   ", "  ##   ", "   #   ", "   #   ", "   #   ", "   #   ", " ##### "],
    '2': [" ##### ", "#     #", "      #", " ##### ", "#      ", "#      ", "#######"],
    '3': [" ##### ", "#     #", "      #", " ##### ", "      #", "#     #", " ##### "],
    '4': ["#      ", "#    # ", "#    # ", "#######", "     # ", "     # ", "     # "],
    '5': ["#######", "#      ", "#      ", "###### ", "      #", "#     #", " ##### "],
    '6': [" ##### ", "#     #", "#      ", "###### ", "#     #", "#     #", " ##### "],
    '7': ["#######", "#     #", "     # ", "    #  ", "   #   ", "   #   ", "   #   "],
    '8': [" ##### ", "#     #", "#     #", " ##### ", "#     #", "#     #", " ##### "],
    '9': [" ##### ", "#     #", "#     #", " ######", "      #", "#     #", " ##### "],
    ':': ["       ", "   ##  ", "   ##  ", "       ", "   ##  ", "   ##  ", "       "],
    ' ': ["       ", "       ", "       ", "       ", "       ", "       ", "       "]
}

class ASCIIClock:
    def __init__(self):
        self.mode = 'both'  # 'analog', 'digital', 'both'
        self.radius = 10
        
    def draw_analog_clock(self, hour, minute, second):
        """Draw analog clock face"""
        lines = []
        diameter = self.radius * 2 + 1
        
        # Create empty clock face
        clock = [[' ' for _ in range(diameter * 2)] for _ in range(diameter)]
        
        # Draw circle
        for angle in range(360):
            x = int(self.radius + self.radius * math.cos(math.radians(angle))) * 2
            y = int(self.radius + self.radius * math.sin(math.radians(angle)))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = '.' if IS_WSL else '·'
                
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = int(self.radius + (self.radius - 1) * math.cos(angle)) * 2
            y = int(self.radius + (self.radius - 1) * math.sin(angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = str((i + 11) % 12 + 1) if i % 3 == 0 else ('o' if IS_WSL else '°')
                
        # Draw hands
        # Hour hand
        hour_angle = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
        for r in range(1, int(self.radius * 0.5)):
            x = int(self.radius + r * math.cos(hour_angle)) * 2
            y = int(self.radius + r * math.sin(hour_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = '#' if IS_WSL else '█'
                
        # Minute hand
        minute_angle = math.radians(minute * 6 - 90)
        for r in range(1, int(self.radius * 0.8)):
            x = int(self.radius + r * math.cos(minute_angle)) * 2
            y = int(self.radius + r * math.sin(minute_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = '=' if IS_WSL else '▓'
                
        # Second hand
        second_angle = math.radians(second * 6 - 90)
        for r in range(1, int(self.radius * 0.9)):
            x = int(self.radius + r * math.cos(second_angle)) * 2
            y = int(self.radius + r * math.sin(second_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                if clock[y][x] == ' ' or clock[y][x] in '.·':
                    clock[y][x] = '|' if abs(math.sin(second_angle)) > 0.5 else '-'
                    
        # Center
        clock[self.radius][self.radius * 2] = '*' if IS_WSL else '●'
        
        # Convert to strings with colors
        for row in clock:
            line = ""
            for char in row:
                if char in '#█':
                    line += f"{BLUE}{char}{RESET}"
                elif char in '=▓':
                    line += f"{GREEN}{char}{RESET}"
                elif char in '│─|-':
                    line += f"{RED}{char}{RESET}"
                elif char in '*●':
                    line += f"{YELLOW}{char}{RESET}"
                elif char.isdigit():
                    line += f"{CYAN}{char}{RESET}"
                else:
                    line += char
            lines.append(line)
            
        return lines
        
    def draw_digital_clock(self, hour, minute, second):
        """Draw digital clock display"""
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        lines = [""] * 7
        
        for char in time_str:
            digit_lines = DIGITS.get(char, DIGITS[' '])
            for i in range(7):
                lines[i] += digit_lines[i] + " "
                
        # Add colors
        colored_lines = []
        for line in lines:
            colored_line = ""
            for char in line:
                if char == '#':
                    colored_line += f"{GREEN}{char}{RESET}"
                else:
                    colored_line += char
            colored_lines.append(colored_line)
            
        return colored_lines
        
    def draw(self):
        """Draw the clock"""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        
        output = []
        
        # Header - use simple characters for WSL
        output.append("")
        if IS_WSL:
            output.append(f"{CYAN}+{'=' * 55}+{RESET}")
            output.append(f"{CYAN}|{RESET}                    ASCII CLOCK                        {CYAN}|{RESET}")
            output.append(f"{CYAN}+{'=' * 55}+{RESET}")
        else:
            output.append(f"{CYAN}╔{'═' * 55}╗{RESET}")
            output.append(f"{CYAN}║{RESET}                    ASCII CLOCK                        {CYAN}║{RESET}")
            output.append(f"{CYAN}╚{'═' * 55}╝{RESET}")
        output.append("")
        
        if self.mode == 'analog' or self.mode == 'both':
            analog_lines = self.draw_analog_clock(hour, minute, second)
            for line in analog_lines:
                output.append("        " + line)
            output.append("")
            
        if self.mode == 'digital' or self.mode == 'both':
            if self.mode == 'both':
                output.append("")
            digital_lines = self.draw_digital_clock(hour, minute, second)
            for line in digital_lines:
                output.append("    " + line)
            output.append("")
            
        # Date display
        date_str = now.strftime("%A, %B %d, %Y")
        output.append(f"\n{MAGENTA}{date_str.center(60)}{RESET}")
        
        # Controls
        output.append(f"\n{WHITE}Mode: {self.mode.upper()}{RESET}")
        output.append("Controls: A analog, D digital, B both, Q quit")
        
        # Render based on platform
        if IS_WSL:
            render_frame_wsl(output)
        else:
            clear_screen()
            print('\n'.join(output))
            flush_output()

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        if not IS_WSL:
            enable_alternate_screen()
        hide_cursor()
        clear_screen()
        
        clock = ASCIIClock()
        clock.draw()
        
        while True:
            # Handle input with timeout for clock updates
            key = kb.get_key(0.5)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'a' or key == 'A':
                    clock.mode = 'analog'
                elif key == 'd' or key == 'D':
                    clock.mode = 'digital'
                elif key == 'b' or key == 'B':
                    clock.mode = 'both'
            
            # Always redraw to update time
            clock.draw()
                    
    except KeyboardInterrupt:
        pass
    finally:
        kb.cleanup()
        show_cursor()
        if not IS_WSL:
            disable_alternate_screen()
        clear_screen()

if __name__ == "__main__":
    main() 