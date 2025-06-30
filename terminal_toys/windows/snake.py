#!/usr/bin/env python3
"""
Terminal Snake for Windows - Classic snake game with colorful graphics
Controls: Arrow keys or WASD to move, Q to quit
"""

import os
import sys
import time
import random
import msvcrt

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

class Snake:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.snake = [(width//2, height//2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 0.1
        
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
            self.speed = max(0.05, self.speed - 0.003)
        else:
            self.snake.pop()
            
    def change_direction(self, dx, dy):
        """Change snake direction (prevent reversing)"""
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)
            
    def draw(self):
        """Draw the game"""
        os.system('cls')
        
        # Create game board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw walls
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
                board[y][x] = '●'  # Head
            else:
                board[y][x] = '○'  # Body
                
        # Draw food
        board[self.food[1]][self.food[0]] = '♦'
        
        # Print board with colors
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if cell in '═║╔╗╚╝':
                    print(f"{BLUE}{cell}{RESET}", end='')
                elif cell == '●':
                    print(f"{GREEN}{cell}{RESET}", end='')
                elif cell == '○':
                    print(f"{GREEN}{cell}{RESET}", end='')
                elif cell == '♦':
                    print(f"{RED}{cell}{RESET}", end='')
                else:
                    print(cell, end='')
            print()
            
        print(f"\nScore: {self.score}")
        print("Controls: Arrow keys or WASD to move, Q to quit")
        
        if self.game_over:
            print(f"\n{RED}*** GAME OVER ***{RESET}")
            print(f"Final Score: {self.score}")

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
        game = Snake()
        last_move = time.time()
        
        while not game.game_over:
            # Handle input
            key = get_key()
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
                    
            # Move snake
            if time.time() - last_move > game.speed:
                game.move()
                game.draw()
                last_move = time.time()
                
            time.sleep(0.05)  # Adjusted for less flickering
            
        # Wait for key press if game over
        if game.game_over:
            time.sleep(2)
            
    finally:
        os.system('cls')

if __name__ == "__main__":
    main() 