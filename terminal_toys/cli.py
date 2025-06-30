#!/usr/bin/env python3
"""
Terminal Toys - Main CLI interface
"""

import sys
import subprocess
import platform

def main():
    """Main CLI entry point"""
    games = {
        '1': ('bouncing-ball', 'Bouncing Balls - Physics-based animation'),
        '2': ('terminal-clock', 'ASCII Clock - Analog and digital clock'),
        '3': ('fire', 'ASCII Fire - Realistic fire animation'),
        '4': ('2048', '2048 Game - Classic sliding tile puzzle'),
        '5': ('paint', 'ASCII Paint - Terminal drawing application'),
        '6': ('life', "Conway's Game of Life - Cellular automaton"),
        '7': ('tictactoe', 'Tic-Tac-Toe - Classic game with AI'),
        '8': ('pipes', 'Pipes Screensaver - Classic Windows pipes'),
        '9': ('tetris', 'Tetris - Classic falling blocks game'),
        '10': ('snake', 'Snake - Classic snake game'),
        '11': ('matrix-rain', 'Matrix Rain - Matrix-style animation'),
    }
    
    is_windows = platform.system() == 'Windows'
    
    print("🎮 Terminal Toys 🎮")
    print("=" * 50)
    print("\nAvailable games and animations:\n")
    
    for key, (cmd, desc) in games.items():
        print(f"  {key}. {desc}")
    
    if is_windows:
        print("\n  W. Use Windows-optimized versions")
    
    print("\n  Q. Quit")
    print("\n" + "=" * 50)
    
    while True:
        choice = input("\nSelect a game (1-11, W for Windows versions, Q to quit): ").strip().upper()
        
        if choice == 'Q':
            print("Thanks for playing! 👋")
            sys.exit(0)
        elif choice == 'W' and is_windows:
            # Show Windows versions menu
            print("\nWindows-optimized versions:")
            for key, (cmd, desc) in games.items():
                print(f"  W{key}. {desc} (Windows version)")
            continue
        elif choice.startswith('W') and is_windows and len(choice) > 1:
            # Run Windows version
            num = choice[1:]
            if num in games:
                cmd = games[num][0] + '-win'
                try:
                    subprocess.run([sys.executable, '-m', f'terminal_toys.windows.{cmd.replace("-win", "").replace("-", "_")}'])
                except KeyboardInterrupt:
                    print("\n\nReturning to menu...")
                except Exception as e:
                    print(f"Error running {cmd}: {e}")
        elif choice in games:
            cmd, _ = games[choice]
            try:
                subprocess.run([cmd])
            except KeyboardInterrupt:
                print("\n\nReturning to menu...")
            except FileNotFoundError:
                print(f"Command '{cmd}' not found. Make sure terminal-toys is properly installed.")
            except Exception as e:
                print(f"Error running {cmd}: {e}")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 