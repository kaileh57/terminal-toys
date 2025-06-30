#!/usr/bin/env python3
"""
Terminal Snake - Cross-platform snake game with colorful graphics
Controls: Arrow keys or WASD to move, Q to quit
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

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class Snake:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.snake = [(width//2, height//2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 0.15  # Slightly slower for better rendering in WSL
        
    def spawn_food(self):
        """Spawn food at random location"""
        while True:
            food = (random.randint(1, self.width-2), 
                   random.randint(1, self.height-2))
            if food not in self.snake:
                return food
                
    def move(self):
        """Move snake in current direction"""
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], 
                   head[1] + self.direction[1])
        
        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.width-1 or
            new_head[1] <= 0 or new_head[1] >= self.height-1):
            self.game_over = True
            return
            
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            # Increase speed
            self.speed = max(0.05, self.speed - 0.005)
        else:
            self.snake.pop()
            
    def change_direction(self, dx, dy):
        """Change snake direction (prevent reversing)"""
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)
            
    def draw(self):
        """Draw the game"""
        # Create game board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw walls - use simple characters for WSL
        if IS_WSL:
            # Simple ASCII borders
            for x in range(self.width):
                board[0][x] = '='
                board[self.height-1][x] = '='
            for y in range(self.height):
                board[y][0] = '|'
                board[y][self.width-1] = '|'
            # Corners
            board[0][0] = '+'
            board[0][self.width-1] = '+'
            board[self.height-1][0] = '+'
            board[self.height-1][self.width-1] = '+'
        else:
            # Unicode box drawing
            for x in range(self.width):
                board[0][x] = '═'
                board[self.height-1][x] = '═'
            for y in range(self.height):
                board[y][0] = '║'
                board[y][self.width-1] = '║'
            # Corners
            board[0][0] = '╔'
            board[0][self.width-1] = '╗'
            board[self.height-1][0] = '╚'
            board[self.height-1][self.width-1] = '╝'
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                board[y][x] = 'O' if IS_WSL else '●'  # Head
            else:
                board[y][x] = 'o' if IS_WSL else '○'  # Body
                
        # Draw food
        board[self.food[1]][self.food[0]] = '*' if IS_WSL else '♦'
        
        # Build output with colors
        output = []
        for y, row in enumerate(board):
            line = ""
            for x, cell in enumerate(row):
                if IS_WSL:
                    # Simple ASCII characters
                    if cell in '=|+':
                        line += f"{BLUE}{cell}{RESET}"
                    elif cell == 'O':  # Snake head
                        line += f"{GREEN}{cell}{RESET}"
                    elif cell == 'o':  # Snake body
                        line += f"{GREEN}{cell}{RESET}"
                    elif cell == '*':  # Food
                        line += f"{RED}{cell}{RESET}"
                    else:
                        line += cell
                else:
                    # Unicode characters
                    if cell in '═║╔╗╚╝':
                        line += f"{BLUE}{cell}{RESET}"
                    elif cell == '●':
                        line += f"{GREEN}{cell}{RESET}"
                    elif cell == '○':
                        line += f"{GREEN}{cell}{RESET}"
                    elif cell == '♦':
                        line += f"{RED}{cell}{RESET}"
                    else:
                        line += cell
            output.append(line)
        
        output.append(f"\nScore: {self.score}")
        output.append("Controls: Arrow keys or WASD to move, Q to quit")
        
        if self.game_over:
            output.append(f"\n{RED}*** GAME OVER ***{RESET}")
            output.append(f"Final Score: {self.score}")
        
        # Render based on platform
        if IS_WSL:
            render_frame_wsl(output)
        else:
            # Move cursor to top-left for consistent rendering
            move_cursor(1, 1)
            print('\n'.join(output))
            flush_output()

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        # Use alternate screen buffer for cleaner display
        if not IS_WSL:
            enable_alternate_screen()
        hide_cursor()
        clear_screen()
        
        # Get terminal size and create appropriately sized game
        term_width, term_height = get_terminal_size()
        game_width = min(60, term_width - 2)
        game_height = min(25, term_height - 5)
        
        game = Snake(game_width, game_height)
        last_move = time.time()
        
        # Initial draw
        game.draw()
        
        while not game.game_over:
            # Handle input
            key = kb.get_key(0.01)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'UP' or key == 'w' or key == 'W':
                    game.change_direction(0, -1)
                elif key == 'DOWN' or key == 's' or key == 'S':
                    game.change_direction(0, 1)
                elif key == 'LEFT' or key == 'a' or key == 'A':
                    game.change_direction(-1, 0)
                elif key == 'RIGHT' or key == 'd' or key == 'D':
                    game.change_direction(1, 0)
                    
            # Move snake at regular intervals
            current_time = time.time()
            if current_time - last_move > game.speed:
                game.move()
                game.draw()
                last_move = current_time
                
            # Small sleep to prevent CPU spinning
            time.sleep(0.01)
            
        # Wait for key press if game over
        if game.game_over:
            flush_output()
            print("\nPress any key to exit...")
            kb.get_key()
            
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