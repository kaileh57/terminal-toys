#!/usr/bin/env python3
"""
Tetris - Cross-platform classic falling blocks game
Controls: Arrow keys to move, Space/Up to rotate, Down to drop, P to pause, Q to quit
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

# Tetris pieces
PIECES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# Colors for pieces
COLORS = {
    'I': '\033[96m',  # Cyan
    'O': '\033[93m',  # Yellow
    'T': '\033[95m',  # Magenta
    'S': '\033[92m',  # Green
    'Z': '\033[91m',  # Red
    'J': '\033[94m',  # Blue
    'L': '\033[33m'   # Orange
}

# Block character
BLOCK = '#' if IS_WSL else '█'
RESET = '\033[0m'

class Tetris:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.board_colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        self.current_piece = None
        self.current_type = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        
        self.next_piece = None
        self.next_type = None
        
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        self.fall_time = 0
        self.fall_speed = 1.0
        
        # Spawn first piece
        self.new_piece()
        
    def rotate_piece(self, piece):
        """Rotate a piece 90 degrees clockwise"""
        return [list(row) for row in zip(*piece[::-1])]
        
    def new_piece(self):
        """Spawn a new piece"""
        if self.next_piece is None:
            self.next_type = random.choice(list(PIECES.keys()))
            self.next_piece = [row[:] for row in PIECES[self.next_type]]
            
        self.current_piece = self.next_piece
        self.current_type = self.next_type
        self.current_x = self.width // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        self.current_rotation = 0
        
        self.next_type = random.choice(list(PIECES.keys()))
        self.next_piece = [row[:] for row in PIECES[self.next_type]]
        
        # Check if game over
        if not self.is_valid_position():
            self.game_over = True
            
    def is_valid_position(self, piece=None, x=None, y=None):
        """Check if a piece position is valid"""
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = self.current_x
        if y is None:
            y = self.current_y
            
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    
                    # Check boundaries
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False
                        
                    # Check collision with placed pieces
                    if new_y >= 0 and self.board[new_y][new_x] != ' ':
                        return False
                        
        return True
        
    def place_piece(self):
        """Place the current piece on the board"""
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    y = self.current_y + row_idx
                    x = self.current_x + col_idx
                    if 0 <= y < self.height:
                        self.board[y][x] = BLOCK
                        self.board_colors[y][x] = self.current_type
                        
        # Check for completed lines
        self.check_lines()
        
        # Spawn new piece
        self.new_piece()
        
    def check_lines(self):
        """Check and clear completed lines"""
        lines_cleared = 0
        
        y = self.height - 1
        while y >= 0:
            if all(cell != ' ' for cell in self.board[y]):
                # Remove line
                del self.board[y]
                del self.board_colors[y]
                # Add empty line at top
                self.board.insert(0, [' ' for _ in range(self.width)])
                self.board_colors.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
                
        if lines_cleared > 0:
            self.lines += lines_cleared
            self.score += [40, 100, 300, 1200][min(lines_cleared - 1, 3)] * self.level
            self.level = 1 + self.lines // 10
            self.fall_speed = max(0.1, 1.0 - (self.level - 1) * 0.1)
            
    def move(self, dx):
        """Move piece horizontally"""
        if self.is_valid_position(x=self.current_x + dx):
            self.current_x += dx
            return True
        return False
        
    def rotate(self):
        """Rotate current piece"""
        rotated = self.rotate_piece(self.current_piece)
        if self.is_valid_position(piece=rotated):
            self.current_piece = rotated
            self.current_rotation = (self.current_rotation + 1) % 4
            return True
        return False
        
    def drop(self):
        """Drop piece by one row"""
        if self.is_valid_position(y=self.current_y + 1):
            self.current_y += 1
            return True
        else:
            self.place_piece()
            return False
            
    def hard_drop(self):
        """Drop piece all the way down"""
        while self.is_valid_position(y=self.current_y + 1):
            self.current_y += 1
        self.place_piece()
        
    def update(self, dt):
        """Update game state"""
        if self.game_over or self.paused:
            return
            
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            self.drop()
            
    def draw(self):
        """Draw the game"""
        output = []
        
        # Title
        output.append("")
        output.append("          TETRIS")
        output.append("")
        
        # Create display board with current piece
        display = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        display_colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Copy board
        for y in range(self.height):
            for x in range(self.width):
                display[y][x] = self.board[y][x]
                display_colors[y][x] = self.board_colors[y][x]
                
        # Add current piece
        if self.current_piece and not self.game_over:
            for row_idx, row in enumerate(self.current_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        y = self.current_y + row_idx
                        x = self.current_x + col_idx
                        if 0 <= y < self.height and 0 <= x < self.width:
                            display[y][x] = BLOCK
                            display_colors[y][x] = self.current_type
                            
        # Draw board with border - use simple characters for WSL
        for y in range(self.height):
            if IS_WSL:
                line = "     |"
            else:
                line = "     │"
            for x in range(self.width):
                if display[y][x] != ' ' and display_colors[y][x]:
                    color = COLORS[display_colors[y][x]]
                    line += f"{color}{display[y][x]}{RESET}"
                else:
                    line += display[y][x]
            line += "|" if IS_WSL else "│"
            
            # Add score info on the side
            if y == 2:
                line += f"  Score: {self.score}"
            elif y == 3:
                line += f"  Lines: {self.lines}"
            elif y == 4:
                line += f"  Level: {self.level}"
            elif y == 6:
                line += "  Next:"
            elif y == 7 and self.next_piece:
                # Show next piece
                for row in self.next_piece:
                    for cell in row:
                        if cell:
                            line += f"  {COLORS[self.next_type]}{BLOCK}{RESET}"
                            break
                    break
                    
            output.append(line)
            
        # Bottom border
        if IS_WSL:
            output.append("     +" + "-" * self.width + "+")
        else:
            output.append("     └" + "─" * self.width + "┘")
        
        # Status
        output.append("")
        if self.game_over:
            output.append("       GAME OVER!")
            output.append("    Press R to restart")
        elif self.paused:
            output.append("       PAUSED")
        
        # Controls
        output.append("")
        output.append("<--> move, <-^-> rotate, v drop, Space hard drop, P pause, Q quit")
        
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
        
        game = Tetris()
        last_time = time.time()
        
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle input
            key = kb.get_key(0.01)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'p' or key == 'P':
                    game.paused = not game.paused
                elif key == 'r' or key == 'R' and game.game_over:
                    game = Tetris()
                elif not game.game_over and not game.paused:
                    if key == 'LEFT':
                        game.move(-1)
                    elif key == 'RIGHT':
                        game.move(1)
                    elif key == 'UP':
                        game.rotate()
                    elif key == 'DOWN':
                        game.drop()
                    elif key == ' ':
                        game.hard_drop()
                        
            # Update
            game.update(dt)
            
            # Draw
            game.draw()
            
            time.sleep(0.01)
            
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