#!/usr/bin/env python3
"""
Pipes Screensaver - Cross-platform animated pipe generation
Press Q to quit, C to clear, R to change colors
Works on Windows, macOS, and Linux
"""

import sys
import time
import random
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput, flush_output,
    enable_alternate_screen, disable_alternate_screen, move_cursor,
    IS_WSL, render_frame_wsl
)

# Pipe characters - use simple ASCII for WSL
if IS_WSL:
    PIPES = {
        'horizontal': '-',
        'vertical': '|',
        'corner_tl': '+',
        'corner_tr': '+',
        'corner_bl': '+',
        'corner_br': '+',
        'cross': '+'
    }
else:
    PIPES = {
        'horizontal': '═',
        'vertical': '║',
        'corner_tl': '╔',
        'corner_tr': '╗',
        'corner_bl': '╚',
        'corner_br': '╝',
        'cross': '╬'
    }

# Colors
COLORS = [
    '\033[91m',  # Red
    '\033[92m',  # Green
    '\033[93m',  # Yellow
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
]
RESET = '\033[0m'

# Directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class Pipe:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.alive = True
        self.length = 0
        
    def get_next_pos(self):
        """Get next position based on direction"""
        if self.direction == UP:
            return self.x, self.y - 1
        elif self.direction == RIGHT:
            return self.x + 1, self.y
        elif self.direction == DOWN:
            return self.x, self.y + 1
        elif self.direction == LEFT:
            return self.x - 1, self.y
            
    def get_pipe_char(self, old_dir, new_dir):
        """Get the appropriate pipe character for direction change"""
        if old_dir == new_dir:
            if old_dir in [UP, DOWN]:
                return PIPES['vertical']
            else:
                return PIPES['horizontal']
        else:
            # Corner pieces
            if (old_dir == UP and new_dir == RIGHT) or (old_dir == LEFT and new_dir == DOWN):
                return PIPES['corner_tl']
            elif (old_dir == UP and new_dir == LEFT) or (old_dir == RIGHT and new_dir == DOWN):
                return PIPES['corner_tr']
            elif (old_dir == DOWN and new_dir == RIGHT) or (old_dir == LEFT and new_dir == UP):
                return PIPES['corner_bl']
            elif (old_dir == DOWN and new_dir == LEFT) or (old_dir == RIGHT and new_dir == UP):
                return PIPES['corner_br']
            else:
                return PIPES['cross']

class PipesAnimation:
    def __init__(self):
        width, height = get_terminal_size()
        self.width = width
        self.height = height - 2  # Leave space for status
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.pipes = []
        self.max_pipes = 5
        self.color_mode = 0  # 0: random, 1: single color
        
    def add_pipe(self):
        """Add a new pipe at random position"""
        if len(self.pipes) < self.max_pipes:
            # Random edge position
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x = random.randint(1, self.width - 2)
                y = 0
                direction = DOWN
            elif edge == 'bottom':
                x = random.randint(1, self.width - 2)
                y = self.height - 1
                direction = UP
            elif edge == 'left':
                x = 0
                y = random.randint(1, self.height - 2)
                direction = RIGHT
            else:  # right
                x = self.width - 1
                y = random.randint(1, self.height - 2)
                direction = LEFT
                
            if self.color_mode == 0:
                color = random.choice(COLORS)
            else:
                color = COLORS[self.color_mode - 1]
                
            self.pipes.append(Pipe(x, y, direction, color))
            
    def update(self):
        """Update all pipes"""
        # Update existing pipes
        for pipe in self.pipes[:]:
            if not pipe.alive:
                continue
                
            # Get next position
            next_x, next_y = pipe.get_next_pos()
            
            # Check boundaries
            if not (0 <= next_x < self.width and 0 <= next_y < self.height):
                pipe.alive = False
                self.pipes.remove(pipe)
                continue
                
            # Check collision with existing pipes
            if self.screen[next_y][next_x] != ' ':
                # Small chance to cross
                if random.random() > 0.1:
                    pipe.alive = False
                    self.pipes.remove(pipe)
                    continue
                    
            # Randomly change direction
            old_dir = pipe.direction
            if random.random() > 0.7 or pipe.length > 10:
                # Choose new direction (not reverse)
                new_dirs = [UP, RIGHT, DOWN, LEFT]
                new_dirs.remove((old_dir + 2) % 4)  # Remove reverse direction
                pipe.direction = random.choice(new_dirs)
                pipe.length = 0
            else:
                pipe.length += 1
                
            # Draw pipe segment
            char = pipe.get_pipe_char(old_dir, pipe.direction)
            self.screen[pipe.y][pipe.x] = char
            self.colors[pipe.y][pipe.x] = pipe.color
            
            # Move pipe
            pipe.x, pipe.y = next_x, next_y
            
        # Add new pipes
        if random.random() > 0.9:
            self.add_pipe()
            
    def clear_screen_buffer(self):
        """Clear the screen buffer"""
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.pipes = []
        
    def draw(self):
        """Draw the screen"""
        output = []
        
        # Draw pipes
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                char = self.screen[y][x]
                if char != ' ' and self.colors[y][x]:
                    line += f"{self.colors[y][x]}{char}{RESET}"
                else:
                    line += char
            output.append(line)
            
        # Status
        color_mode_str = "Random" if self.color_mode == 0 else f"Color {self.color_mode}"
        output.append(f"\nPipes: {len(self.pipes)} | Colors: {color_mode_str} | Q quit, C clear, R change colors")
        
        # Render based on platform
        if IS_WSL:
            render_frame_wsl(output)
        else:
            move_cursor(1, 1)
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
        
        animation = PipesAnimation()
        animation.draw()
        
        while True:
            # Handle input
            key = kb.get_key(0.01)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'c' or key == 'C':
                    animation.clear_screen_buffer()
                elif key == 'r' or key == 'R':
                    animation.color_mode = (animation.color_mode + 1) % (len(COLORS) + 1)
                    
            animation.update()
            animation.draw()
            time.sleep(0.05)
            
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