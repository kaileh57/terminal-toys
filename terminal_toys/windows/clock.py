#!/usr/bin/env python3
"""
ASCII Clock for Windows - Beautiful analog and digital clock display
Press Q to quit, A/D to switch between analog/digital/both modes
"""

import os
import sys
import time
import math
import msvcrt
from datetime import datetime

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

# 7-segment display patterns
DIGITS = {
    '0': ["  ███  ", " █   █ ", "█     █", "█     █", "█     █", " █   █ ", "  ███  "],
    '1': ["   █   ", "  ██   ", "   █   ", "   █   ", "   █   ", "   █   ", " █████ "],
    '2': [" █████ ", "█     █", "      █", " █████ ", "█      ", "█      ", "███████"],
    '3': [" █████ ", "█     █", "      █", " █████ ", "      █", "█     █", " █████ "],
    '4': ["█      ", "█    █ ", "█    █ ", "███████", "     █ ", "     █ ", "     █ "],
    '5': ["███████", "█      ", "█      ", "██████ ", "      █", "█     █", " █████ "],
    '6': [" █████ ", "█     █", "█      ", "██████ ", "█     █", "█     █", " █████ "],
    '7': ["███████", "█     █", "     █ ", "    █  ", "   █   ", "   █   ", "   █   "],
    '8': [" █████ ", "█     █", "█     █", " █████ ", "█     █", "█     █", " █████ "],
    '9': [" █████ ", "█     █", "█     █", " ██████", "      █", "█     █", " █████ "],
    ':': ["       ", "   ██  ", "   ██  ", "       ", "   ██  ", "   ██  ", "       "],
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
                clock[y][x] = '·'
                
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = int(self.radius + (self.radius - 1) * math.cos(angle)) * 2
            y = int(self.radius + (self.radius - 1) * math.sin(angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = str((i + 11) % 12 + 1) if i % 3 == 0 else '°'
                
        # Draw hands
        # Hour hand
        hour_angle = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
        for r in range(1, int(self.radius * 0.5)):
            x = int(self.radius + r * math.cos(hour_angle)) * 2
            y = int(self.radius + r * math.sin(hour_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = '█'
                
        # Minute hand
        minute_angle = math.radians(minute * 6 - 90)
        for r in range(1, int(self.radius * 0.8)):
            x = int(self.radius + r * math.cos(minute_angle)) * 2
            y = int(self.radius + r * math.sin(minute_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                clock[y][x] = '▓'
                
        # Second hand
        second_angle = math.radians(second * 6 - 90)
        for r in range(1, int(self.radius * 0.9)):
            x = int(self.radius + r * math.cos(second_angle)) * 2
            y = int(self.radius + r * math.sin(second_angle))
            if 0 <= x < diameter * 2 and 0 <= y < diameter:
                if clock[y][x] == ' ' or clock[y][x] == '·':
                    clock[y][x] = '│' if abs(math.sin(second_angle)) > 0.5 else '─'
                    
        # Center
        clock[self.radius][self.radius * 2] = '●'
        
        # Convert to strings with colors
        for row in clock:
            line = ""
            for char in row:
                if char == '█':
                    line += f"{BLUE}{char}{RESET}"
                elif char == '▓':
                    line += f"{GREEN}{char}{RESET}"
                elif char in '│─':
                    line += f"{RED}{char}{RESET}"
                elif char == '●':
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
                if char == '█':
                    colored_line += f"{GREEN}{char}{RESET}"
                else:
                    colored_line += char
            colored_lines.append(colored_line)
            
        return colored_lines
        
    def draw(self):
        """Draw the clock"""
        os.system('cls')
        
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        
        # Header
        print(f"\n{CYAN}╔═══════════════════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║{RESET}                    ASCII CLOCK                        {CYAN}║{RESET}")
        print(f"{CYAN}╚═══════════════════════════════════════════════════════╝{RESET}\n")
        
        if self.mode == 'analog' or self.mode == 'both':
            analog_lines = self.draw_analog_clock(hour, minute, second)
            for line in analog_lines:
                print("        " + line)
            print()
            
        if self.mode == 'digital' or self.mode == 'both':
            if self.mode == 'both':
                print()
            digital_lines = self.draw_digital_clock(hour, minute, second)
            for line in digital_lines:
                print("    " + line)
            print()
            
        # Date display
        date_str = now.strftime("%A, %B %d, %Y")
        print(f"\n{MAGENTA}{date_str.center(60)}{RESET}")
        
        # Controls
        print(f"\n{WHITE}Mode: {self.mode.upper()}{RESET}")
        print("Controls: A analog, D digital, B both, Q quit")

def get_key():
    """Get keyboard input (non-blocking) for Windows"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        return key.decode('utf-8', errors='ignore')
    return None

def main():
    try:
        # Hide cursor
        print('\033[?25l', end='', flush=True)
        
        clock = ASCIIClock()
        
        while True:
            clock.draw()
            
            # Handle input
            key = get_key()
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'a' or key == 'A':
                    clock.mode = 'analog'
                elif key == 'd' or key == 'D':
                    clock.mode = 'digital'
                elif key == 'b' or key == 'B':
                    clock.mode = 'both'
                    
            time.sleep(0.5)  # Update less frequently to reduce flickering
            
    finally:
        # Show cursor
        print('\033[?25h', end='', flush=True)
        os.system('cls')

if __name__ == "__main__":
    main() 

