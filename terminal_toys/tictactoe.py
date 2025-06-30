#!/usr/bin/env python3
"""
Tic-Tac-Toe - Cross-platform classic game with AI opponent
Press 1-9 to place your mark, Q to quit
Works on Windows, macOS, and Linux
"""

import sys
import random
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput, flush_output,
    enable_alternate_screen, disable_alternate_screen, move_cursor,
    IS_WSL, render_frame_wsl
)

# Colors
BLUE = '\033[94m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'  # Human player
        self.game_over = False
        self.winner = None
        self.winning_line = None
        
    def make_move(self, position, player):
        """Make a move on the board"""
        if self.board[position] == ' ' and not self.game_over:
            self.board[position] = player
            return True
        return False
        
    def check_winner(self):
        """Check if there's a winner"""
        # All possible winning combinations
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in lines:
            if (self.board[line[0]] != ' ' and 
                self.board[line[0]] == self.board[line[1]] == self.board[line[2]]):
                self.winner = self.board[line[0]]
                self.winning_line = line
                self.game_over = True
                return True
                
        # Check for tie
        if ' ' not in self.board:
            self.game_over = True
            return True
            
        return False
        
    def get_ai_move(self):
        """Get AI move using minimax algorithm"""
        if self.game_over:
            return None
            
        # First move: take center or corner
        if self.board.count(' ') == 9:
            return random.choice([0, 2, 4, 6, 8])
            
        best_score = -float('inf')
        best_move = None
        
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O'
                score = self.minimax(self.board, 0, False)
                self.board[i] = ' '
                
                if score > best_score:
                    best_score = score
                    best_move = i
                    
        return best_move
        
    def minimax(self, board, depth, is_maximizing):
        """Minimax algorithm for AI"""
        # Check terminal states
        winner = self.check_board_winner(board)
        if winner == 'O':
            return 10 - depth
        elif winner == 'X':
            return depth - 10
        elif ' ' not in board:
            return 0
            
        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'O'
                    score = self.minimax(board, depth + 1, False)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'X'
                    score = self.minimax(board, depth + 1, True)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score
            
    def check_board_winner(self, board):
        """Check winner for a given board state"""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in lines:
            if (board[line[0]] != ' ' and 
                board[line[0]] == board[line[1]] == board[line[2]]):
                return board[line[0]]
        return None
        
    def draw(self):
        """Draw the game board"""
        output = []
        
        # Title
        output.append("")
        output.append(f"{CYAN}     TIC-TAC-TOE{RESET}")
        output.append("")
        
        # Board
        for row in range(3):
            line = "     "
            for col in range(3):
                idx = row * 3 + col
                cell = self.board[idx]
                
                # Color based on player
                if cell == 'X':
                    cell_str = f"{BLUE}X{RESET}"
                elif cell == 'O':
                    cell_str = f"{RED}O{RESET}"
                else:
                    # Show position number
                    cell_str = f"{YELLOW}{idx + 1}{RESET}"
                    
                # Highlight winning line
                if self.winning_line and idx in self.winning_line:
                    cell_str = f"{GREEN}{self.board[idx]}{RESET}"
                    
                line += f" {cell_str} "
                if col < 2:
                    line += "|" if IS_WSL else "│"
                    
            output.append(line)
            if row < 2:
                if IS_WSL:
                    output.append("     ---+---+---")
                else:
                    output.append("     ───┼───┼───")
                    
        output.append("")
        
        # Status
        if self.game_over:
            if self.winner:
                if self.winner == 'X':
                    output.append(f"{GREEN}     You win!{RESET}")
                else:
                    output.append(f"{RED}     AI wins!{RESET}")
            else:
                output.append(f"{YELLOW}     It's a tie!{RESET}")
            output.append("")
            output.append("  Press R to play again")
        else:
            if self.current_player == 'X':
                output.append("     Your turn (X)")
            else:
                output.append("     AI thinking...")
                
        output.append("")
        output.append("  Press 1-9 to play, Q to quit")
        
        # Render based on platform
        if IS_WSL:
            render_frame_wsl(output)
        else:
            clear_screen()
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
        
        game = TicTacToe()
        game.draw()
        
        while True:
            # Handle input
            key = kb.get_key(0.1)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'r' or key == 'R':
                    game = TicTacToe()
                    game.draw()
                elif key in '123456789' and not game.game_over:
                    position = int(key) - 1
                    if game.make_move(position, 'X'):
                        game.check_winner()
                        game.draw()
                        
                        # AI move
                        if not game.game_over:
                            # Small delay for AI "thinking"
                            import time
                            time.sleep(0.5)
                            
                            ai_move = game.get_ai_move()
                            if ai_move is not None:
                                game.make_move(ai_move, 'O')
                                game.check_winner()
                                game.draw()
                                
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