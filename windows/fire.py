#!/usr/bin/env python3
"""
ASCII Fire for Windows - Realistic fire animation effect
Press Q to quit, +/- to adjust intensity
"""

import os
import sys
import time
import random
import msvcrt
import shutil

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

# Enable ANSI colors in Windows
os.system('color')

class FireEffect:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size()
        self.width = min(self.width, 80)
        self.height = min(self.height - 3, 30)
        
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
        os.system('cls')
        
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
            print(line)
            
        # Status line
        print(f"\nIntensity: {self.intensity} | Wind: {self.wind:+d}")
        print("Controls: Q to quit, +/- to adjust intensity, ← → to adjust wind")

def get_key():
    """Get keyboard input (non-blocking) for Windows"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key in [b'\xe0', b'\x00']:  # Special keys (arrows)
            key = msvcrt.getch()
            if key == b'K':  # Left arrow
                return 'LEFT'
            elif key == b'M':  # Right arrow
                return 'RIGHT'
        else:
            return key.decode('utf-8', errors='ignore')
    return None

def main():
    try:
        # Hide cursor
        print('\033[?25l', end='', flush=True)
        
        fire = FireEffect()
        
        while True:
            # Handle input
            key = get_key()
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
            
    finally:
        # Show cursor
        print('\033[?25h', end='', flush=True)
        os.system('cls')

if __name__ == "__main__":
    main() 
