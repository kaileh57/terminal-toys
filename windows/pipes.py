#!/usr/bin/env python3
"""
Pipes Screensaver for Windows - Animated colorful pipes that grow and change direction
Controls:
- Q: Quit
- +: Add pipe
- -: Remove pipe
- C: Clear all pipes
- R: Reset screensaver
- Space: Pause/unpause
"""

import os
import sys
import time
import random
import msvcrt
import shutil
from collections import deque

# Pipe characters (using box drawing characters)
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
    't_left': '┤',
    'start': '●',
    'end': '■'
}

# Enhanced color palette
COLORS = [
    '\033[91m',  # Bright Red
    '\033[92m',  # Bright Green
    '\033[93m',  # Bright Yellow
    '\033[94m',  # Bright Blue
    '\033[95m',  # Bright Magenta
    '\033[96m',  # Bright Cyan
    '\033[97m',  # Bright White
    '\033[31m',  # Red
    '\033[32m',  # Green
    '\033[33m',  # Yellow
    '\033[34m',  # Blue
    '\033[35m',  # Magenta
    '\033[36m',  # Cyan
]
RESET = '\033[0m'
BOLD = '\033[1m'

# Enable ANSI colors in Windows
os.system('color')

class Pipe:
    def __init__(self, x, y, color, max_length=150):
        self.x = x
        self.y = y
        self.color = color
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.alive = True
        self.trail = deque([(x, y)], maxlen=max_length)
        self.age = 0
        self.direction_changes = 0
        self.max_direction_changes = random.randint(15, 40)
        self.steps_since_turn = 0
        self.min_steps_before_turn = random.randint(3, 8)
        
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
        
    def get_pipe_char(self, prev_pos, current_pos, next_pos=None):
        """Get appropriate pipe character based on position context"""
        if len(self.trail) == 1:
            return PIPES['start']
            
        if not prev_pos:
            return PIPES['start']
            
        # Calculate directions
        prev_x, prev_y = prev_pos
        curr_x, curr_y = current_pos
        
        # Determine incoming direction
        if prev_x < curr_x:
            from_dir = 'left'
        elif prev_x > curr_x:
            from_dir = 'right'
        elif prev_y < curr_y:
            from_dir = 'up'
        else:
            from_dir = 'down'
            
        # If this is the end of the pipe
        if not next_pos:
            return PIPES['end']
            
        # Determine outgoing direction
        next_x, next_y = next_pos
        if next_x < curr_x:
            to_dir = 'left'
        elif next_x > curr_x:
            to_dir = 'right'
        elif next_y < curr_y:
            to_dir = 'up'
        else:
            to_dir = 'down'
            
        # Choose appropriate pipe character
        if from_dir == to_dir:
            if from_dir in ['left', 'right']:
                return PIPES['horizontal']
            else:
                return PIPES['vertical']
        else:
            # Corner pieces
            if (from_dir == 'left' and to_dir == 'down') or (from_dir == 'up' and to_dir == 'right'):
                return PIPES['top_left']
            elif (from_dir == 'right' and to_dir == 'down') or (from_dir == 'up' and to_dir == 'left'):
                return PIPES['top_right']
            elif (from_dir == 'left' and to_dir == 'up') or (from_dir == 'down' and to_dir == 'right'):
                return PIPES['bottom_left']
            elif (from_dir == 'right' and to_dir == 'up') or (from_dir == 'down' and to_dir == 'left'):
                return PIPES['bottom_right']
                
        return PIPES['cross']

class PipesScreensaver:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size()
        self.width = min(self.width, 120)  # Limit width
        self.height = min(self.height - 3, 40)  # Leave room for status
        self.pipes = []
        self.max_pipes = 6
        self.paused = False
        self.frame_count = 0
        
    def add_pipe(self):
        """Add a new pipe at random position"""
        if len(self.pipes) < self.max_pipes:
            # Start pipes from edges or random positions
            if random.choice([True, False]):
                # Start from edge
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                if edge == 'top':
                    x, y = random.randint(5, self.width - 5), 2
                elif edge == 'bottom':
                    x, y = random.randint(5, self.width - 5), self.height - 3
                elif edge == 'left':
                    x, y = 2, random.randint(5, self.height - 5)
                else:  # right
                    x, y = self.width - 3, random.randint(5, self.height - 5)
            else:
                # Random position
                x = random.randint(5, self.width - 5)
                y = random.randint(5, self.height - 5)
                
            color = random.choice(COLORS)
            pipe_length = random.randint(80, 200)
            self.pipes.append(Pipe(x, y, color, pipe_length))
            
    def remove_pipe(self):
        """Remove the oldest pipe"""
        if self.pipes:
            self.pipes.pop(0)
            
    def clear_pipes(self):
        """Clear all pipes"""
        self.pipes.clear()
        
    def reset(self):
        """Reset the screensaver"""
        self.pipes.clear()
        self.frame_count = 0
        for _ in range(3):
            self.add_pipe()
            
    def update(self):
        """Update all pipes"""
        if self.paused:
            return
            
        self.frame_count += 1
        
        # Add new pipes occasionally
        if self.frame_count % 120 == 0 and len(self.pipes) < self.max_pipes:
            self.add_pipe()
            
        # Update existing pipes
        for pipe in self.pipes[:]:
            if not pipe.alive:
                self.pipes.remove(pipe)
                continue
                
            pipe.age += 1
            pipe.steps_since_turn += 1
            
            # Get next position
            next_x, next_y = pipe.get_next_position()
            
            # Check boundaries
            if (next_x < 1 or next_x >= self.width - 1 or 
                next_y < 1 or next_y >= self.height - 1):
                
                # Try to find a valid direction
                valid_directions = []
                for test_dir in ['up', 'down', 'left', 'right']:
                    if test_dir == pipe.direction:
                        continue
                        
                    old_dir = pipe.direction
                    pipe.direction = test_dir
                    test_x, test_y = pipe.get_next_position()
                    
                    if (1 <= test_x < self.width - 1 and 
                        1 <= test_y < self.height - 1):
                        valid_directions.append(test_dir)
                    
                    pipe.direction = old_dir
                    
                if valid_directions:
                    pipe.direction = random.choice(valid_directions)
                    next_x, next_y = pipe.get_next_position()
                    pipe.direction_changes += 1
                    pipe.steps_since_turn = 0
                else:
                    pipe.alive = False
                    continue
                    
            # Occasionally change direction (more natural behavior)
            should_turn = False
            if (pipe.steps_since_turn >= pipe.min_steps_before_turn and
                pipe.direction_changes < pipe.max_direction_changes):
                
                # Higher chance to turn based on age and random factor
                turn_chance = 0.02 + (pipe.age * 0.0001)
                if random.random() < turn_chance:
                    should_turn = True
                    
            if should_turn:
                # Choose a perpendicular direction
                if pipe.direction in ['up', 'down']:
                    new_directions = ['left', 'right']
                else:
                    new_directions = ['up', 'down']
                    
                # Filter valid directions
                valid_dirs = []
                for test_dir in new_directions:
                    old_dir = pipe.direction
                    pipe.direction = test_dir
                    test_x, test_y = pipe.get_next_position()
                    
                    if (1 <= test_x < self.width - 1 and 
                        1 <= test_y < self.height - 1):
                        valid_dirs.append(test_dir)
                    
                    pipe.direction = old_dir
                    
                if valid_dirs:
                    pipe.direction = random.choice(valid_dirs)
                    next_x, next_y = pipe.get_next_position()
                    pipe.direction_changes += 1
                    pipe.steps_since_turn = 0
                    pipe.min_steps_before_turn = random.randint(3, 12)
                    
            # Move pipe
            pipe.x, pipe.y = next_x, next_y
            pipe.trail.append((next_x, next_y))
            
            # Kill pipe if it's lived too long
            if pipe.direction_changes >= pipe.max_direction_changes:
                pipe.alive = False
                
    def draw(self):
        """Draw the screen"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        # Create screen buffer
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        color_map = {}
        
        # Draw pipes
        for pipe in self.pipes:
            trail_list = list(pipe.trail)
            for i, (x, y) in enumerate(trail_list):
                if 0 <= x < self.width and 0 <= y < self.height:
                    prev_pos = trail_list[i-1] if i > 0 else None
                    next_pos = trail_list[i+1] if i < len(trail_list) - 1 else None
                    
                    char = pipe.get_pipe_char(prev_pos, (x, y), next_pos)
                    screen[y][x] = char
                    color_map[(x, y)] = pipe.color
                    
        # Print screen with colors
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = screen[y][x]
                if (x, y) in color_map:
                    line += f"{color_map[(x, y)]}{BOLD}{cell}{RESET}"
                else:
                    line += cell
            print(line)
            
        # Status line
        status = f"Pipes: {len(self.pipes)}/{self.max_pipes}"
        if self.paused:
            status += " [PAUSED]"
        status += f" | Frame: {self.frame_count}"
        
        print(f"\n{COLORS[6]}{status}{RESET}")
        print(f"{COLORS[2]}Controls: Q=Quit, +=Add pipe, -=Remove pipe, C=Clear, R=Reset, Space=Pause{RESET}")

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
        
        screensaver = PipesScreensaver()
        
        # Start with a few pipes
        for _ in range(3):
            screensaver.add_pipe()
        
        while True:
            # Check for input
            key = get_key()
            if key:
                if key.lower() == 'q':
                    break
                elif key == '+':
                    screensaver.add_pipe()
                elif key == '-':
                    screensaver.remove_pipe()
                elif key.lower() == 'c':
                    screensaver.clear_pipes()
                elif key.lower() == 'r':
                    screensaver.reset()
                elif key == ' ':
                    screensaver.paused = not screensaver.paused
                    
            screensaver.update()
            screensaver.draw()
            time.sleep(0.08)  # Smooth animation
            
    except KeyboardInterrupt:
        pass
    finally:
        # Show cursor and clear screen
        print('\033[?25h\033[2J\033[H', end='', flush=True)

if __name__ == "__main__":
    main()
