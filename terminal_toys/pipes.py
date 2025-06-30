#!/usr/bin/env python3
"""
Pipes Screensaver - Cross-platform animated colorful pipes that grow and change direction
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

# Pipe characters
PIPES = {
    'horizontal': '─',
    'vertical': '│',
    'top_left': '┌',
    'top_right': '┐',
    'bottom_left': '└',
    'bottom_right': '┘',
    'cross': '┼',
    't_down': '┬',
    't_up': '┴',
    't_right': '├',
    't_left': '┤'
}

# Colors
COLORS = [
    '\033[91m',  # Red
    '\033[92m',  # Green
    '\033[93m',  # Yellow
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
    '\033[97m',  # White
]
RESET = '\033[0m'

class Pipe:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.alive = True
        self.trail = [(x, y)]
        
    def get_next_position(self):
        """Get next position based on direction"""
        dx, dy = 0, 0
        if self.direction == 'up':
            dy = -1
        elif self.direction == 'down':
            dy = 1
        elif self.direction == 'left':
            dx = -1
        elif self.direction == 'right':
            dx = 1
        return self.x + dx, self.y + dy
        
    def get_pipe_char(self, prev_dir, next_dir):
        """Get appropriate pipe character for connection"""
        if prev_dir == next_dir:
            if prev_dir in ['left', 'right']:
                return PIPES['horizontal']
            else:
                return PIPES['vertical']
        else:
            # Corners
            if (prev_dir == 'right' and next_dir == 'down') or (prev_dir == 'up' and next_dir == 'left'):
                return PIPES['top_left']
            elif (prev_dir == 'left' and next_dir == 'down') or (prev_dir == 'up' and next_dir == 'right'):
                return PIPES['top_right']
            elif (prev_dir == 'right' and next_dir == 'up') or (prev_dir == 'down' and next_dir == 'left'):
                return PIPES['bottom_left']
            elif (prev_dir == 'left' and next_dir == 'up') or (prev_dir == 'down' and next_dir == 'right'):
                return PIPES['bottom_right']
        return PIPES['cross']

class PipesScreensaver:
    def __init__(self):
        width, height = get_terminal_size()
        self.width = width
        self.height = min(height - 2, 40)  # Leave space for status
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.pipes = []
        self.max_pipes = 5
        
    def add_pipe(self):
        """Add a new pipe at random position"""
        if len(self.pipes) < self.max_pipes:
            x = random.randint(5, min(self.width - 5, 75))
            y = random.randint(5, self.height - 7)
            color = random.choice(COLORS)
            self.pipes.append(Pipe(x, y, color))
            
    def update(self):
        """Update all pipes"""
        # Add new pipes occasionally
        if random.random() > 0.95:
            self.add_pipe()
            
        # Update existing pipes
        for pipe in self.pipes[:]:
            if not pipe.alive:
                self.pipes.remove(pipe)
                continue
                
            # Get next position
            next_x, next_y = pipe.get_next_position()
            
            # Check boundaries
            if (next_x < 1 or next_x >= min(self.width - 1, 79) or 
                next_y < 1 or next_y >= len(self.screen) - 1):
                # Change direction
                directions = ['up', 'down', 'left', 'right']
                directions.remove(pipe.direction)
                pipe.direction = random.choice(directions)
                next_x, next_y = pipe.get_next_position()
                
                # If still out of bounds, kill pipe
                if (next_x < 1 or next_x >= min(self.width - 1, 79) or 
                    next_y < 1 or next_y >= len(self.screen) - 1):
                    pipe.alive = False
                    continue
                    
            # Check collision with other pipes
            if self.screen[next_y][next_x] != ' ':
                # Try changing direction
                directions = ['up', 'down', 'left', 'right']
                directions.remove(pipe.direction)
                random.shuffle(directions)
                
                found_valid = False
                for new_dir in directions:
                    old_dir = pipe.direction
                    pipe.direction = new_dir
                    test_x, test_y = pipe.get_next_position()
                    
                    if (1 <= test_x < min(self.width - 1, 79) and 
                        1 <= test_y < len(self.screen) - 1 and
                        self.screen[test_y][test_x] == ' '):
                        next_x, next_y = test_x, test_y
                        found_valid = True
                        break
                    else:
                        pipe.direction = old_dir
                        
                if not found_valid:
                    pipe.alive = False
                    continue
                    
            # Move pipe
            pipe.x, pipe.y = next_x, next_y
            pipe.trail.append((next_x, next_y))
            
            # Occasionally change direction
            if random.random() > 0.9:
                directions = ['up', 'down', 'left', 'right']
                directions.remove(pipe.direction)
                pipe.direction = random.choice(directions)
                
    def draw(self):
        """Draw the screen"""
        clear_screen()
        
        # Clear screen
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw pipes
        for pipe in self.pipes:
            for i, (x, y) in enumerate(pipe.trail):
                if 0 <= x < self.width and 0 <= y < len(self.screen):
                    if i == 0:
                        self.screen[y][x] = '●'
                    else:
                        # Determine pipe character based on direction changes
                        if i < len(pipe.trail) - 1:
                            prev_x, prev_y = pipe.trail[i-1]
                            next_x, next_y = pipe.trail[i+1]
                            
                            # Determine directions
                            if prev_x < x:
                                prev_dir = 'right'
                            elif prev_x > x:
                                prev_dir = 'left'
                            elif prev_y < y:
                                prev_dir = 'down'
                            else:
                                prev_dir = 'up'
                                
                            if next_x < x:
                                next_dir = 'left'
                            elif next_x > x:
                                next_dir = 'right'
                            elif next_y < y:
                                next_dir = 'up'
                            else:
                                next_dir = 'down'
                                
                            char = pipe.get_pipe_char(prev_dir, next_dir)
                        else:
                            # Last segment
                            if pipe.direction in ['left', 'right']:
                                char = PIPES['horizontal']
                            else:
                                char = PIPES['vertical']
                                
                        self.screen[y][x] = char
                        
        # Print screen with colors
        for y, row in enumerate(self.screen):
            line = ""
            for x, cell in enumerate(row[:80]):  # Limit width
                # Find which pipe this belongs to
                colored = False
                for pipe in self.pipes:
                    if (x, y) in pipe.trail:
                        line += f"{pipe.color}{cell}{RESET}"
                        colored = True
                        break
                if not colored:
                    line += cell
            print(line)
            
        print(f"\n{COLORS[2]}Press Q to quit{RESET}")

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        hide_cursor()
        screensaver = PipesScreensaver()
        
        while True:
            # Check for quit
            key = kb.get_key(0.01)
            if key and key.lower() == 'q':
                break
                
            screensaver.update()
            screensaver.draw()
            time.sleep(0.15)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()

if __name__ == "__main__":
    main() 