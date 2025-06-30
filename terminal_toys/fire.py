#!/usr/bin/env python3
"""
ASCII Fire - Cross-platform realistic fire animation effect
Press Q to quit, +/- to adjust intensity
Works on Windows, macOS, and Linux
"""

import sys
import time
import random
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput, flush_output,
    enable_alternate_screen, disable_alternate_screen, move_cursor
)

# Fire characters from cold to hot
FIRE_CHARS = [' ', '.', ':', ';', '+', '*', '#', '@']

# Fire colors from cold to hot
FIRE_COLORS = [
    '\033[30m',   # Black
    '\033[31m',   # Dark red
    '\033[91m',   # Red
    '\033[93m',   # Yellow
    '\033[33m',   # Orange
    '\033[97m',   # White
    '\033[97;1m', # Bright white
    '\033[97;1m', # Bright white
]
RESET = '\033[0m'

class FireEffect:
    def __init__(self):
        width, height = get_terminal_size()
        self.width = min(width, 80)
        self.height = min(height - 3, 30)
        
        # Fire buffer
        self.buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.intensity = 6  # Fire intensity (scaled to FIRE_CHARS length)
        self.wind = 0        # Wind effect
        
    def update(self):
        """Update fire animation"""
        # Set bottom row (fire source)
        for x in range(self.width):
            if random.random() > 0.2:  # Create hot spots
                self.buffer[self.height - 1][x] = random.randint(
                    max(0, self.intensity - 2), 
                    min(len(FIRE_CHARS) - 1, self.intensity)
                )
            else:
                self.buffer[self.height - 1][x] = 0
                
        # Add random hot spots in the middle of bottom row
        hot_spots = random.randint(2, 5)
        for _ in range(hot_spots):
            x = random.randint(self.width // 4, 3 * self.width // 4)
            if x < self.width:
                self.buffer[self.height - 1][x] = len(FIRE_CHARS) - 1
                
        # Propagate fire upwards
        for y in range(self.height - 2, -1, -1):
            for x in range(self.width):
                # Average surrounding pixels
                total = 0
                count = 0
                
                # Look at pixels below and around
                for dy in range(2):
                    for dx in range(-1, 2):
                        ny = y + dy + 1
                        nx = x + dx + self.wind
                        
                        if 0 <= nx < self.width and ny < self.height:
                            total += self.buffer[ny][nx]
                            count += 1
                            
                if count > 0:
                    avg = total / count
                    # Add decay and randomness
                    decay = random.uniform(0.8, 1.1)
                    new_val = int(avg * decay)
                    
                    # Clamp to valid range
                    self.buffer[y][x] = max(0, min(len(FIRE_CHARS) - 1, new_val))
                else:
                    self.buffer[y][x] = 0
                    
    def draw(self):
        """Draw the fire effect"""
        move_cursor(1, 1)
        
        output = []
        
        # Draw fire
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                val = self.buffer[y][x]
                if val > 0:
                    char = FIRE_CHARS[val]
                    color = FIRE_COLORS[min(val, len(FIRE_COLORS) - 1)]
                    line += f"{color}{char}{RESET}"
                else:
                    line += " "
            output.append(line)
            
        # Status line
        output.append(f"\nIntensity: {self.intensity} | Wind: {self.wind:+d}")
        output.append("Controls: Q to quit, +/- to adjust intensity, ← → to adjust wind")
        
        # Print all at once
        print('\n'.join(output))
        flush_output()

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        enable_alternate_screen()
        hide_cursor()
        clear_screen()
        
        fire = FireEffect()
        fire.draw()
        
        while True:
            # Handle input
            key = kb.get_key(0.01)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == '+' or key == '=':
                    fire.intensity = min(len(FIRE_CHARS) - 1, fire.intensity + 1)
                elif key == '-' or key == '_':
                    fire.intensity = max(1, fire.intensity - 1)
                elif key == 'LEFT':  # Wind left
                    fire.wind = max(-2, fire.wind - 1)
                elif key == 'RIGHT':  # Wind right
                    fire.wind = min(2, fire.wind + 1)
                    
            fire.update()
            fire.draw()
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        kb.cleanup()
        show_cursor()
        disable_alternate_screen()
        clear_screen()

if __name__ == "__main__":
    main() 