#!/usr/bin/env python3
"""
Matrix Rain - Cross-platform Matrix-style falling characters animation
Press Q to quit
Works on Windows, macOS, and Linux
"""

import sys
import time
import random
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput
)

# Matrix characters
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

# Colors
GREEN = '\033[92m'
BRIGHT_GREEN = '\033[32;1m'
DIM_GREEN = '\033[32;2m'
WHITE = '\033[97m'
RESET = '\033[0m'

class MatrixRain:
    def __init__(self):
        width, height = get_terminal_size()
        self.width = width
        self.height = height - 2  # Leave space for status
        self.drops = []
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.chars = CHARS + KATAKANA
        
        # Initialize drops
        for x in range(self.width):
            if random.random() > 0.7:
                self.drops.append({
                    'x': x,
                    'y': random.randint(-self.height, 0),
                    'speed': random.uniform(0.5, 2.0),
                    'length': random.randint(5, 20),
                    'chars': []
                })
                
    def update(self):
        """Update the animation"""
        # Clear screen buffer
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Update existing drops
        for drop in self.drops[:]:
            drop['y'] += drop['speed']
            
            # Add new character to trail
            if len(drop['chars']) < drop['length']:
                drop['chars'].append(random.choice(self.chars))
            
            # Draw the drop
            for i, char in enumerate(drop['chars']):
                y = int(drop['y']) - i
                if 0 <= y < len(self.screen) and drop['x'] < self.width:
                    if i == 0:  # Head of the drop
                        self.screen[y][drop['x']] = (char, 'bright')
                    elif i < 3:  # Near head
                        self.screen[y][drop['x']] = (char, 'normal')
                    else:  # Tail
                        self.screen[y][drop['x']] = (char, 'dim')
                        
            # Remove drops that have fallen off screen
            if drop['y'] - drop['length'] > len(self.screen):
                self.drops.remove(drop)
                
        # Add new drops
        for x in range(self.width):
            if random.random() > 0.98 and not any(d['x'] == x for d in self.drops):
                self.drops.append({
                    'x': x,
                    'y': 0,
                    'speed': random.uniform(0.5, 2.0),
                    'length': random.randint(5, 20),
                    'chars': []
                })
                
    def draw(self):
        """Draw the screen"""
        clear_screen()
        
        for row in self.screen:
            line = ""
            for cell in row:
                if isinstance(cell, tuple):
                    char, style = cell
                    if style == 'bright':
                        line += f"{WHITE}{char}{RESET}"
                    elif style == 'normal':
                        line += f"{BRIGHT_GREEN}{char}{RESET}"
                    else:  # dim
                        line += f"{DIM_GREEN}{char}{RESET}"
                else:
                    line += " "
            print(line)
            
        print(f"\n{DIM_GREEN}Press Q to quit{RESET}")

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        hide_cursor()
        matrix = MatrixRain()
        
        while True:
            # Check for quit
            key = kb.get_key(0.01)
            if key and key.lower() == 'q':
                break
                
            matrix.update()
            matrix.draw()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()

if __name__ == "__main__":
    main() 