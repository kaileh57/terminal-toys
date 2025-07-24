#!/usr/bin/env python3
"""
Terminal Toys - Bundled CLI interface for PyInstaller
This version imports and runs games directly instead of using subprocess
"""

import sys
import os
import platform

# Import all games
from terminal_toys.windows import (
    bouncing_ball, clock, fire, game_2048, life,
    matrix_rain, paint, pipes, snake, tetris, tictactoe
)

def clear_screen():
    """Clear the screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def wait_for_key():
    """Wait for a key press"""
    if platform.system() == 'Windows':
        import msvcrt
        print("\nPress any key to return to menu...")
        msvcrt.getch()
    else:
        input("\nPress Enter to return to menu...")

def run_game(game_module, game_name):
    """Run a game module"""
    try:
        clear_screen()
        print(f"Starting {game_name}...\n")
        print("Press Ctrl+C to return to menu\n")
        # Small delay to let user see the message
        import time
        time.sleep(0.5)
        game_module.main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted.")
    except Exception as e:
        print(f"\nError running {game_name}: {e}")
    finally:
        wait_for_key()
        clear_screen()

def main():
    """Main CLI entry point"""
    games = {
        '1': (bouncing_ball, 'Bouncing Balls - Physics-based animation'),
        '2': (clock, 'ASCII Clock - Analog and digital clock'),
        '3': (fire, 'ASCII Fire - Realistic fire animation'),
        '4': (game_2048, '2048 Game - Classic sliding tile puzzle'),
        '5': (paint, 'ASCII Paint - Terminal drawing application'),
        '6': (life, "Conway's Game of Life - Cellular automaton"),
        '7': (tictactoe, 'Tic-Tac-Toe - Classic game with AI'),
        '8': (pipes, 'Pipes Screensaver - Classic Windows pipes'),
        '9': (tetris, 'Tetris - Classic falling blocks game'),
        '10': (snake, 'Snake - Classic snake game'),
        '11': (matrix_rain, 'Matrix Rain - Matrix-style animation'),
    }
    
    while True:
        clear_screen()
        print("🎮 Terminal Toys 🎮")
        print("=" * 50)
        print("\nAvailable games and animations:\n")
        
        for key, (_, desc) in games.items():
            print(f"  {key}. {desc}")
        
        print("\n  Q. Quit")
        print("\n" + "=" * 50)
        
        choice = input("\nSelect a game (1-11, Q to quit): ").strip().upper()
        
        if choice == 'Q':
            print("Thanks for playing! 👋")
            sys.exit(0)
        elif choice in games:
            game_module, desc = games[choice]
            game_name = desc.split(' - ')[0]
            run_game(game_module, game_name)
        else:
            print("Invalid choice. Please try again.")
            wait_for_key()

if __name__ == "__main__":
    main() 