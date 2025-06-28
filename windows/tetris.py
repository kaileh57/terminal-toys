#!/usr/bin/env python3
"""
Terminal Tetris for Windows - A colorful Tetris game for the terminal
Controls: A/D or Arrow keys to move, W/Up to rotate, S/Down to drop faster, Q to quit
"""

import os
import sys
import time
import random
import msvcrt
from typing import List, Tuple, Optional

# Tetris pieces (each piece is a list of rotations)
PIECES = [
    # I piece
    [[[1,1,1,1]], [[1],[1],[1],[1]]],
    # O piece  
    [[[1,1],[1,1]]],
    # T piece
    [[[0,1,0],[1,1,1]], [[1,0],[1,1],[1,0]], [[1,1,1],[0,1,0]], [[0,1],[1,1],[0,1]]],
    # S piece
    [[[0,1,1],[1,1,0]], [[1,0],[1,1],[0,1]]],
    # Z piece
    [[[1,1,0],[0,1,1]], [[0,1],[1,1],[1,0]]],
    # J piece
    [[[1,0,0],[1,1,1]], [[1,1],[1,0],[1,0]], [[1,1,1],[0,0,1]], [[0,1],[0,1],[1,1]]],
    # L piece
    [[[0,0,1],[1,1,1]], [[1,0],[1,0],[1,1]], [[1,1,1],[1,0,0]], [[1,1],[0,1],[0,1]]]
]

# Colors for pieces (Windows console colors)
COLORS = ['\033[96m', '\033[93m', '\033[95m', '\033[92m', '\033[91m', '\033[94m', '\033[97m']
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

class Tetris:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        self.current_piece_type = 0
        self.drop_time = 1.0
        self.last_drop = time.time()
        
    def new_piece(self):
        """Generate a new random piece"""
        self.current_piece_type = random.randint(0, len(PIECES) - 1)
        self.current_rotation = 0
        piece = PIECES[self.current_piece_type][self.current_rotation]
        self.current_piece = piece
        self.current_x = self.width // 2 - len(piece[0]) // 2
        self.current_y = 0
        
        # Check if game over
        if not self.is_valid_position():
            self.game_over = True
            
    def is_valid_position(self, piece=None, x=None, y=None):
        """Check if piece position is valid"""
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = self.current_x
        if y is None:
            y = self.current_y
            
        for py, row in enumerate(piece):
            for px, cell in enumerate(row):
                if cell:
                    board_x = x + px
                    board_y = y + py
                    if (board_x < 0 or board_x >= self.width or 
                        board_y >= self.height or
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return False
        return True
        
    def rotate_piece(self):
        """Rotate current piece"""
        piece_rotations = PIECES[self.current_piece_type]
        new_rotation = (self.current_rotation + 1) % len(piece_rotations)
        new_piece = piece_rotations[new_rotation]
        
        if self.is_valid_position(piece=new_piece):
            self.current_piece = new_piece
            self.current_rotation = new_rotation
            
    def move_piece(self, dx, dy):
        """Move piece by dx, dy"""
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if self.is_valid_position(x=new_x, y=new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False
        
    def drop_piece(self):
        """Drop piece one row"""
        if not self.move_piece(0, 1):
            self.lock_piece()
            
    def hard_drop(self):
        """Drop piece all the way down"""
        while self.move_piece(0, 1):
            self.score += 2
            
    def lock_piece(self):
        """Lock piece in place and check for lines"""
        for py, row in enumerate(self.current_piece):
            for px, cell in enumerate(row):
                if cell:
                    board_y = self.current_y + py
                    board_x = self.current_x + px
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.current_piece_type + 1
                        
        # Check for complete lines
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0] * self.width)
                lines_cleared += 1
            else:
                y -= 1
                
        if lines_cleared:
            self.lines += lines_cleared
            self.score += [0, 100, 300, 500, 800][lines_cleared] * self.level
            self.level = 1 + self.lines // 10
            self.drop_time = max(0.1, 1.0 - (self.level - 1) * 0.1)
            
        self.new_piece()
        
    def draw(self):
        """Draw the game board"""
        os.system('cls')
        
        # Create display board
        display = [row[:] for row in self.board]
        
        # Add current piece
        if self.current_piece:
            for py, row in enumerate(self.current_piece):
                for px, cell in enumerate(row):
                    if cell:
                        board_y = self.current_y + py
                        board_x = self.current_x + px
                        if 0 <= board_y < self.height and 0 <= board_x < self.width:
                            display[board_y][board_x] = self.current_piece_type + 1
                            
        # Draw top border
        print("┌" + "─" * (self.width * 2) + "┐")
        
        # Draw board
        for row in display:
            print("│", end="")
            for cell in row:
                if cell:
                    print(f"{COLORS[cell-1]}██{RESET}", end="")
                else:
                    print("  ", end="")
            print("│")
            
        # Draw bottom border
        print("└" + "─" * (self.width * 2) + "┘")
        
        # Draw stats
        print(f"\nScore: {self.score}")
        print(f"Lines: {self.lines}")
        print(f"Level: {self.level}")
        print("\nControls: ← → ↓ (move), ↑ (rotate), Space (hard drop), Q (quit)")
        
        if self.game_over:
            print("\n*** GAME OVER ***")
            print("Press any key to exit...")

def get_key():
    """Get keyboard input (non-blocking) for Windows"""
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
        game = Tetris()
        game.new_piece()
        
        last_draw = time.time()
        needs_redraw = True
        
        while not game.game_over:
            # Handle input
            key = get_key()
            if key:
                needs_redraw = True
                if key == 'q' or key == 'Q':
                    break
                elif key == 'LEFT' or key == 'a' or key == 'A':
                    game.move_piece(-1, 0)
                elif key == 'RIGHT' or key == 'd' or key == 'D':
                    game.move_piece(1, 0)
                elif key == 'UP' or key == 'w' or key == 'W':
                    game.rotate_piece()
                elif key == 'DOWN' or key == 's' or key == 'S':
                    game.drop_piece()
                    game.score += 1
                elif key == ' ':  # Space (hard drop)
                    game.hard_drop()
                    
            # Auto drop
            if time.time() - game.last_drop > game.drop_time:
                game.drop_piece()
                game.last_drop = time.time()
                needs_redraw = True
                
            # Only redraw when necessary
            if needs_redraw or time.time() - last_draw > 0.5:
                game.draw()
                last_draw = time.time()
                needs_redraw = False
                
            time.sleep(0.05)  # Small delay for responsiveness
            
        # Wait for key press if game over
        if game.game_over:
            while not msvcrt.kbhit():
                time.sleep(0.1)
                
    finally:
        os.system('cls')

if __name__ == "__main__":
    main() 