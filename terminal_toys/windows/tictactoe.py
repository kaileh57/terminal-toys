#!/usr/bin/env python3
"""
Tic-Tac-Toe for Windows - Classic game with AI opponent
Controls: Arrow keys to move, Space to place, 1 for Easy AI, 2 for Hard AI, Q to quit
"""

import os
import sys
import msvcrt
import random

# Colors
BLUE = '\033[94m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.cursor_x = 1
        self.cursor_y = 1
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.ai_mode = None  # None, 'easy', 'hard'
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        
    def reset(self):
        """Reset the game"""
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        
    def make_move(self, x, y, player):
        """Make a move at position (x, y)"""
        if self.board[y][x] == ' ' and not self.game_over:
            self.board[y][x] = player
            return True
        return False
        
    def check_winner(self):
        """Check if there's a winner"""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != ' ':
                return row[0]
                
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                return self.board[0][col]
                
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]
            
        # Check for tie
        if all(self.board[y][x] != ' ' for y in range(3) for x in range(3)):
            return 'tie'
            
        return None
        
    def get_available_moves(self):
        """Get list of available moves"""
        moves = []
        for y in range(3):
            for x in range(3):
                if self.board[y][x] == ' ':
                    moves.append((x, y))
        return moves
        
    def minimax(self, depth, is_maximizing):
        """Minimax algorithm for AI"""
        winner = self.check_winner()
        
        if winner == self.ai_symbol:
            return 1
        elif winner == self.player_symbol:
            return -1
        elif winner == 'tie':
            return 0
            
        if is_maximizing:
            max_eval = float('-inf')
            for x, y in self.get_available_moves():
                self.board[y][x] = self.ai_symbol
                eval_score = self.minimax(depth + 1, False)
                self.board[y][x] = ' '
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for x, y in self.get_available_moves():
                self.board[y][x] = self.player_symbol
                eval_score = self.minimax(depth + 1, True)
                self.board[y][x] = ' '
                min_eval = min(min_eval, eval_score)
            return min_eval
            
    def ai_move_easy(self):
        """Easy AI - makes random moves"""
        moves = self.get_available_moves()
        if moves:
            x, y = random.choice(moves)
            self.make_move(x, y, self.ai_symbol)
            
    def ai_move_hard(self):
        """Hard AI - uses minimax algorithm"""
        best_score = float('-inf')
        best_move = None
        
        for x, y in self.get_available_moves():
            self.board[y][x] = self.ai_symbol
            score = self.minimax(0, False)
            self.board[y][x] = ' '
            
            if score > best_score:
                best_score = score
                best_move = (x, y)
                
        if best_move:
            x, y = best_move
            self.make_move(x, y, self.ai_symbol)
            
    def draw(self):
        """Draw the game board"""
        os.system('cls')
        
        print(f"{BLUE}╔═══════════════════════════╗{RESET}")
        print(f"{BLUE}║{RESET}      TIC-TAC-TOE          {BLUE}║{RESET}")
        print(f"{BLUE}╚═══════════════════════════╝{RESET}")
        print()
        
        # Draw board
        print("     0   1   2")
        print("   ┌───┬───┬───┐")
        
        for y in range(3):
            print(f" {y} │", end="")
            for x in range(3):
                # Determine what to display
                if self.board[y][x] == 'X':
                    symbol = f"{RED}X{RESET}"
                elif self.board[y][x] == 'O':
                    symbol = f"{BLUE}O{RESET}"
                else:
                    symbol = ' '
                    
                # Highlight cursor position
                if x == self.cursor_x and y == self.cursor_y and not self.game_over:
                    print(f"{YELLOW} {symbol} {RESET}", end="")
                else:
                    print(f" {symbol} ", end="")
                    
                if x < 2:
                    print("│", end="")
            print("│")
            
            if y < 2:
                print("   ├───┼───┼───┤")
                
        print("   └───┴───┴───┘")
        print()
        
        # Status
        if self.game_over:
            if self.winner == 'tie':
                print(f"{YELLOW}It's a tie!{RESET}")
            else:
                winner_color = RED if self.winner == 'X' else BLUE
                print(f"{winner_color}Player {self.winner} wins!{RESET}")
            print("\nPress R to play again")
        else:
            player_color = RED if self.current_player == 'X' else BLUE
            print(f"Current player: {player_color}{self.current_player}{RESET}")
            
            if self.ai_mode:
                mode = "Easy AI" if self.ai_mode == 'easy' else "Hard AI"
                print(f"Mode: vs {mode}")
            else:
                print("Mode: Two Players")
                
        print("\nControls: ←↑→↓ move, Space place, 1 Easy AI, 2 Hard AI, R reset, Q quit")

def get_key():
    """Get keyboard input for Windows"""
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
        game = TicTacToe()
        
        while True:
            game.draw()
            
            # Check for winner
            winner = game.check_winner()
            if winner and not game.game_over:
                game.winner = winner
                game.game_over = True
                
            # AI move
            if not game.game_over and game.ai_mode and game.current_player == game.ai_symbol:
                if game.ai_mode == 'easy':
                    game.ai_move_easy()
                else:
                    game.ai_move_hard()
                    
                game.current_player = game.player_symbol
                continue
                
            # Handle input
            key = get_key()
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'r' or key == 'R':
                    game.reset()
                elif key == '1':
                    game.reset()
                    game.ai_mode = 'easy'
                elif key == '2':
                    game.reset()
                    game.ai_mode = 'hard'
                elif not game.game_over:
                    if key == 'UP':
                        game.cursor_y = max(0, game.cursor_y - 1)
                    elif key == 'DOWN':
                        game.cursor_y = min(2, game.cursor_y + 1)
                    elif key == 'LEFT':
                        game.cursor_x = max(0, game.cursor_x - 1)
                    elif key == 'RIGHT':
                        game.cursor_x = min(2, game.cursor_x + 1)
                    elif key == ' ':
                        if game.make_move(game.cursor_x, game.cursor_y, game.current_player):
                            # Switch player
                            if game.ai_mode:
                                game.current_player = game.ai_symbol
                            else:
                                game.current_player = 'O' if game.current_player == 'X' else 'X'
                                
    finally:
        os.system('cls')

if __name__ == "__main__":
    main() 
