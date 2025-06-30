# Terminal Toys 🎮

A collection of fun and interactive terminal animations and utilities! Each toy is available in two versions:
- **Cross-platform versions** - Work on Windows, macOS, and Linux
- **Windows-optimized versions** - In the `windows/` directory

## 🎨 Animations & Utilities

### 1. **Bouncing Balls** ⚪
Physics-based bouncing ball animation.
- **Controls**: Space to add ball, C to clear, G to toggle gravity, T for trails, Q to quit
- **Features**: Realistic physics, ball collisions, trails, gravity toggle

### 2. **ASCII Clock** 🕐
Beautiful analog and digital clock display.
- **Controls**: A for analog, D for digital, B for both, Q to quit
- **Features**: Real-time updates, analog clock face, 7-segment digital display

### 3. **ASCII Fire** 🔥
Realistic fire animation effect.
- **Controls**: Q to quit, +/- to adjust intensity, ← → to adjust wind
- **Features**: Realistic fire physics, wind effects, adjustable intensity

### 4. **2048 Game** 🔢
The classic sliding tile puzzle game.
- **Controls**: Arrow keys or WASD to slide tiles, Q to quit
- **Features**: Colorful tiles, score tracking, win/loss conditions

### 5. **ASCII Paint** 🎨
A simple drawing application for your terminal.
- **Controls**: Arrow keys to move, Space to draw, C to change color, E to erase, L for line mode, F to fill, S to save, Q to quit
- **Features**: Drawing, erasing, line mode, flood fill, multiple colors, and saving your art.

### 6. **Conway's Game of Life** 🧬
Cellular automaton simulation.
- **Controls**: Arrow keys to move, Space to toggle cell, P to play/pause, C to clear, R to randomize, 1-5 for patterns, Q to quit
- **Features**: Classic Conway's Game of Life rules, adjustable speed, pre-defined patterns, manual cell toggling.

### 7. **Tic-Tac-Toe** ⭕
Classic game with an AI opponent.
- **Controls**: Arrow keys to move, Space to place, 1 for Easy AI, 2 for Hard AI, Q to quit
- **Features**: Play against another player or an AI with two difficulty levels.

### 8. **Pipes Screensaver** 🚰
Classic Windows pipes screensaver recreation.
- **Controls**: Q to quit, + to add pipe, - to remove pipe, C to clear all, R to reset
- **Features**: Animated colorful pipes that grow and change direction, realistic pipe connections, multiple simultaneous pipes.

### 9. **Tetris** 🧩
The classic falling block puzzle game.
- **Controls**: A/D or Arrow keys to move, W/Up to rotate, S/Down to drop faster, Space for hard drop, Q to quit
- **Features**: Classic Tetris gameplay, line clearing, scoring system, increasing difficulty levels, colorful blocks.

### 10. **Snake** 🐍
Classic snake game with colorful graphics.
- **Controls**: Arrow keys or WASD to move, Q to quit
- **Features**: Colorful snake and food, score tracking, increasing speed, wall and self-collision detection.

### 11. **Matrix Rain** 💻
Matrix-style falling characters.
- **Controls**: Q to quit
- **Features**: Green cascading characters with Japanese katakana, variable speeds, realistic matrix effect.

## 📋 Requirements

### Cross-Platform Versions
- Python 3.6+
- Works on Windows, macOS, and Linux
- No additional packages required (uses only Python standard library)

### Windows-Specific Versions
- Python 3.6+
- Windows 10 or later (for ANSI color support)
- Uses Windows-specific optimizations

## 🚀 Usage

### Cross-Platform (Windows/macOS/Linux)
```bash
# Run any toy directly
python bouncing_ball.py
python clock.py
python snake.py
python matrix_rain.py
# ... etc
```

### Windows-Specific Versions
```cmd
# Run Windows-optimized versions
cd windows
python bouncing_ball.py
python clock.py
python fire.py
# ... etc
```

### Examples:
```bash
# Cross-platform versions (work everywhere)
python bouncing_ball.py
python clock.py
python snake.py
python matrix_rain.py

# Windows-specific versions (Windows only)
python windows\bouncing_ball.py
python windows\clock.py
python windows\fire.py
python windows\game_2048.py
python windows\paint.py
python windows\life.py
python windows\tictactoe.py
python windows\pipes.py
python windows\tetris.py
python windows\snake.py
python windows\matrix_rain.py
```

## 🌟 Features

- **Cross-platform support**: Main versions work on Windows, macOS, and Linux
- **Colorful**: All animations use ANSI colors for a vibrant experience
- **No dependencies**: Uses only Python standard library
- **Keyboard controls**: Responsive keyboard input handling
- **Single file**: Each toy is self-contained in a single Python file

## 🐛 Troubleshooting

### Colors not working?
- **Windows**: Make sure you're using Windows 10 or later, or try Windows Terminal
- **macOS/Linux**: Most modern terminals support ANSI colors by default

### Game crashes on startup?
- Check Python version: `python --version` (should be 3.6+)
- Make sure terminal_utils.py is in the same directory for cross-platform versions
- Try the Windows-specific versions if on Windows

### Arrow keys not working on macOS/Linux?
- Make sure your terminal emulator properly sends escape sequences
- Try using WASD keys as an alternative (where supported)

## 🔧 Technical Details

The cross-platform versions use a `terminal_utils.py` module that handles:
- Platform detection
- Cross-platform keyboard input (using `msvcrt` on Windows, `termios` on Unix)
- Screen clearing and cursor control
- ANSI color support

Windows-specific versions are optimized with:
- Direct `msvcrt` usage for faster input
- Windows console API features
- Optimized screen clearing

## 🎉 Enjoy!

Have fun playing with these terminal toys! Feel free to modify and extend them as you like. Each one is designed to be simple enough to understand and modify while being fun to play with.

---
Made with ❤️ for terminal enthusiasts everywhere!
