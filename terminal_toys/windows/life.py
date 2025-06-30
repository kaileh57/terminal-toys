#!/usr/bin/env python3
"""
Conway's Game of Life for Windows - Cellular automaton simulation
Controls: Arrow keys to move, Space to toggle cell, P to play/pause,
         C to clear, R to randomize, 1-5 for patterns, Q to quit
"""

import os
import sys
import time
import random
import msvcrt
import shutil

# Cell characters
ALIVE = '█'
DEAD = ' '

# Colors
GREEN = '\033[92m'
DIM_GREEN = '\033[32;2m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

# Common patterns
PATTERNS = {
    '1': {  # Glider
        'name': 'Glider',
        'pattern': [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ]
    },
    '2': {  # Blinker
        'name': 'Blinker',
        'pattern': [
            [1],
            [1],
            [1]
        ]
    },
    '3': {  # Toad
        'name': 'Toad',
        'pattern': [
            [0, 1, 1, 1],
            [1, 1, 1, 0]
        ]
    },
    '4': {  # Beacon
        'name': 'Beacon',
        'pattern': [
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]
        ]
    },
    '5': {  # Pulsar
        'name': 'Pulsar',
        'pattern': [
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
        ]
    }
}

class GameOfLife:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size()
        self.width = min(self.width - 2, 78)
        self.height = min(self.height - 5, 28)
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = self.width // 2
        self.cursor_y = self.height // 2
        self.playing = False
        self.generation = 0
        self.population = 0
        self.speed = 0.1
        
    def count_neighbors(self, x, y):
        """Count living neighbors around a cell"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx]:
                        count += 1
        return count
        
    def update(self):
        """Update the grid according to Conway's rules"""
        new_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                
                if self.grid[y][x]:  # Living cell
                    # Survive with 2 or 3 neighbors
                    new_grid[y][x] = neighbors in [2, 3]
                else:  # Dead cell
                    # Birth with exactly 3 neighbors
                    new_grid[y][x] = neighbors == 3
                    
        self.grid = new_grid
        self.generation += 1
        self.population = sum(sum(row) for row in self.grid)
        
    def toggle_cell(self, x, y):
        """Toggle a cell's state"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]
            self.population = sum(sum(row) for row in self.grid)
            
    def clear(self):
        """Clear the grid"""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.population = 0
        
    def randomize(self):
        """Randomize the grid"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.random() > 0.7
        self.generation = 0
        self.population = sum(sum(row) for row in self.grid)
        
    def place_pattern(self, pattern_key):
        """Place a pattern at cursor position"""
        if pattern_key in PATTERNS:
            pattern = PATTERNS[pattern_key]['pattern']
            ph = len(pattern)
            pw = len(pattern[0]) if pattern else 0
            
            # Center pattern on cursor
            start_y = self.cursor_y - ph // 2
            start_x = self.cursor_x - pw // 2
            
            for y, row in enumerate(pattern):
                for x, cell in enumerate(row):
                    px, py = start_x + x, start_y + y
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.grid[py][px] = bool(cell)
                        
            self.population = sum(sum(row) for row in self.grid)
            
    def draw(self):
        """Draw the grid"""
        os.system('cls')
        
        # Draw top border
        print("┌" + "─" * self.width + "┐")
        
        # Draw grid
        for y in range(self.height):
            print("│", end="")
            for x in range(self.width):
                if x == self.cursor_x and y == self.cursor_y and not self.playing:
                    # Draw cursor
                    if self.grid[y][x]:
                        print(f"{YELLOW}{ALIVE}{RESET}", end="")
                    else:
                        print(f"{YELLOW}·{RESET}", end="")
                else:
                    if self.grid[y][x]:
                        # Color based on neighbor count for visual interest
                        neighbors = self.count_neighbors(x, y)
                        if neighbors in [2, 3]:
                            print(f"{GREEN}{ALIVE}{RESET}", end="")
                        else:
                            print(f"{DIM_GREEN}{ALIVE}{RESET}", end="")
                    else:
                        print(DEAD, end="")
            print("│")
            
        # Draw bottom border
        print("└" + "─" * self.width + "┘")
        
        # Status bar
        status = "PLAYING" if self.playing else "PAUSED"
        print(f"\nGen: {self.generation} | Pop: {self.population} | Status: {status}")
        print("←↑→↓ move, Space toggle, P play/pause, C clear, R random, 1-5 patterns, Q quit")

def get_key():
    """Get keyboard input for Windows"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key in [b'\xe0', b'\x00']:  # Special keys (arrows)
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
    return None

def main():
    try:
        # Hide cursor
        print('\033[?25l', end='', flush=True)
        
        game = GameOfLife()
        last_update = time.time()
        last_draw = time.time()
        needs_redraw = True
        
        while True:
            # Handle input
            key = get_key()
            if key:
                needs_redraw = True
                if key == 'q' or key == 'Q':
                    break
                elif key == 'p' or key == 'P':
                    game.playing = not game.playing
                elif key == 'c' or key == 'C':
                    game.clear()
                elif key == 'r' or key == 'R':
                    game.randomize()
                elif key in PATTERNS:
                    game.place_pattern(key)
                elif not game.playing:
                    if key == 'UP':
                        game.cursor_y = max(0, game.cursor_y - 1)
                    elif key == 'DOWN':
                        game.cursor_y = min(game.height - 1, game.cursor_y + 1)
                    elif key == 'LEFT':
                        game.cursor_x = max(0, game.cursor_x - 1)
                    elif key == 'RIGHT':
                        game.cursor_x = min(game.width - 1, game.cursor_x + 1)
                    elif key == ' ':
                        game.toggle_cell(game.cursor_x, game.cursor_y)
                        
            # Update simulation if playing
            if game.playing and time.time() - last_update > game.speed:
                game.update()
                last_update = time.time()
                needs_redraw = True
                
            # Only redraw when necessary or every 0.2 seconds
            if needs_redraw or (time.time() - last_draw > 0.2):
                game.draw()
                last_draw = time.time()
                needs_redraw = False
                
            time.sleep(0.05)
            
    finally:
        # Show cursor
        print('\033[?25h', end='', flush=True)
        os.system('cls')

if __name__ == "__main__":
    main() 

