#!/usr/bin/env python3
"""
2048 - Cross-platform sliding tile puzzle game
Controls: Arrow keys or WASD to slide tiles, Q to quit
Goal: Combine tiles to reach 2048!
Works on Windows, macOS, and Linux
"""

import sys
import random
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput
)

# Tile colors
TILE_COLORS = {
    0: '\033[90m',      # Empty - gray
    2: '\033[97m',      # White
    4: '\033[93m',      # Yellow
    8: '\033[96m',      # Cyan
    16: '\033[92m',     # Green
    32: '\033[94m',     # Blue
    64: '\033[95m',     # Magenta
    128: '\033[91m',    # Red
    256: '\033[33m',    # Orange
    512: '\033[35m',    # Purple
    1024: '\033[31m',   # Dark red
    2048: '\033[33;1m', # Bright orange
}
RESET = '\033[0m'

class Game2048:
    def __init__(self, size=4):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        self.add_new_tile()
        self.add_new_tile()
        
    def add_new_tile(self):
        """Add a new tile (2 or 4) to a random empty position"""
        empty = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty:
            i, j = random.choice(empty)
            self.board[i][j] = 4 if random.random() > 0.9 else 2
            
    def slide_row(self, row):
        """Slide and merge a single row to the left"""
        # Remove zeros
        non_zero = [x for x in row if x != 0]
        
        # Merge adjacent equal tiles
        merged = []
        skip = False
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i < len(non_zero) - 1 and non_zero[i] == non_zero[i + 1]:
                merged.append(non_zero[i] * 2)
                self.score += non_zero[i] * 2
                skip = True
            else:
                merged.append(non_zero[i])
                
        # Pad with zeros
        return merged + [0] * (self.size - len(merged))
        
    def move(self, direction):
        """Move tiles in the given direction"""
        old_board = [row[:] for row in self.board]
        
        if direction == 'left':
            for i in range(self.size):
                self.board[i] = self.slide_row(self.board[i])
        elif direction == 'right':
            for i in range(self.size):
                self.board[i] = self.slide_row(self.board[i][::-1])[::-1]
        elif direction == 'up':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)]
                new_col = self.slide_row(col)
                for i in range(self.size):
                    self.board[i][j] = new_col[i]
        elif direction == 'down':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)]
                new_col = self.slide_row(col[::-1])[::-1]
                for i in range(self.size):
                    self.board[i][j] = new_col[i]
                    
        # Check if board changed
        if self.board != old_board:
            self.add_new_tile()
            self.moves += 1
            
            # Check for win
            for row in self.board:
                if 2048 in row:
                    self.won = True
                    
            # Check for game over
            if self.is_game_over():
                self.game_over = True
                
    def is_game_over(self):
        """Check if no more moves are possible"""
        # Check for empty cells
        for row in self.board:
            if 0 in row:
                return False
                
        # Check for possible merges
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                # Check right
                if j < self.size - 1 and self.board[i][j + 1] == current:
                    return False
                # Check down
                if i < self.size - 1 and self.board[i + 1][j] == current:
                    return False
                    
        return True
        
    def draw(self):
        """Draw the game board"""
        clear_screen()
        
        print(f"╔{'═' * 31}╗")
        print(f"║{'2048 GAME':^31}║")
        print(f"╠{'═' * 31}╣")
        score_line = f"Score: {self.score:<10} Moves: {self.moves:<3}"
        print(f"║ {score_line:^29} ║")
        print(f"╚{'═' * 31}╝")
        print()
        
        # Draw board
        print("┌" + ("─" * 7 + "┬") * (self.size - 1) + "─" * 7 + "┐")
        
        for i, row in enumerate(self.board):
            print("│", end="")
            for j, val in enumerate(row):
                if val == 0:
                    print(f"       ", end="")
                else:
                    color = TILE_COLORS.get(val, '\033[97m')
                    print(f"{color}{val:^7}{RESET}", end="")
                    
                if j < self.size - 1:
                    print("│", end="")
            print("│")
            
            if i < self.size - 1:
                print("├" + ("─" * 7 + "┼") * (self.size - 1) + "─" * 7 + "┤")
                
        print("└" + ("─" * 7 + "┴") * (self.size - 1) + "─" * 7 + "┘")
        
        print("\nControls: ← ↑ → ↓ or WASD to move, Q to quit")
        
        if self.won:
            print(f"\n{TILE_COLORS[2048]}*** CONGRATULATIONS! YOU WON! ***{RESET}")
            print("Press C to continue playing or Q to quit")
        elif self.game_over:
            print(f"\n\033[91m*** GAME OVER ***{RESET}")
            print(f"Final Score: {self.score}")

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        hide_cursor()
        game = Game2048()
        
        while True:
            game.draw()
            
            # Handle input
            key = kb.get_key()
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif game.won and (key == 'c' or key == 'C'):
                    game.won = False  # Continue playing
                elif not game.game_over and not game.won:
                    if key == 'UP' or key == 'w' or key == 'W':
                        game.move('up')
                    elif key == 'DOWN' or key == 's' or key == 'S':
                        game.move('down')
                    elif key == 'LEFT' or key == 'a' or key == 'A':
                        game.move('left')
                    elif key == 'RIGHT' or key == 'd' or key == 'D':
                        game.move('right')
                        
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()

if __name__ == "__main__":
    main() 