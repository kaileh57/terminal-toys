# WSL Compatibility Fixes for Terminal Toys

## The Problem

When running terminal-toys in WSL (Windows Subsystem for Linux), the games display incorrectly with scrambled Unicode box-drawing characters and misaligned text. This is due to WSL's different handling of:

1. Unicode box-drawing characters (╔╗╚╝║═├┤┬┴┼)
2. Cursor positioning ANSI escape sequences
3. Alternate screen buffer
4. Terminal size detection

## The Solution

The fix involves detecting when running in WSL and using simpler ASCII characters instead of Unicode, along with adjusted rendering methods.

### Key Changes Made:

1. **Terminal Utils (`terminal_utils.py`)**:
   - Added WSL detection via `/proc/version`
   - Disabled cursor positioning in WSL
   - Disabled alternate screen buffer in WSL
   - Added `render_frame_wsl()` function for proper frame rendering
   - Improved keyboard input handling for WSL

2. **Game Updates**:
   - Import `IS_WSL` and `render_frame_wsl` from terminal_utils
   - Check `IS_WSL` when drawing UI elements
   - Use simple ASCII characters when in WSL
   - Use `render_frame_wsl()` for output in WSL

### Character Replacements for WSL:

| Unicode | ASCII | Usage |
|---------|-------|-------|
| ╔ ╗ ╚ ╝ | + | Box corners |
| ║ | \| | Vertical lines |
| ═ | = or - | Horizontal lines |
| ├ ┤ ┬ ┴ ┼ | + | Box intersections |
| ● ○ | O o | Snake game pieces |
| ♦ | * | Food/items |
| █ ▓ ▒ ░ | # * : . | Shading blocks |
| ← ↑ → ↓ | < ^ > v | Arrow indicators |

### Pattern for Updating Games:

```python
# Import WSL detection
from .terminal_utils import IS_WSL, render_frame_wsl

# In drawing code:
if IS_WSL:
    # Use simple ASCII
    border_char = '+'
    wall_char = '|'
    snake_head = 'O'
else:
    # Use Unicode
    border_char = '╔'
    wall_char = '║'
    snake_head = '●'

# For rendering:
if IS_WSL:
    render_frame_wsl(output_lines)
else:
    clear_screen()
    print('\n'.join(output_lines))
    flush_output()
```

## Games Updated:

1. **2048** ✅ - Uses +=-| for borders, maintains colored tiles
2. **Snake** ✅ - Uses +=-| for walls, O/o for snake, * for food

## Games Still Needing Updates:

3. **Bouncing Ball** - Replace box borders
4. **Clock** - Simplify clock face characters
5. **Fire** - Should work as-is (uses simple chars)
6. **Life** - Replace grid characters
7. **Matrix Rain** - Should work as-is
8. **Paint** - Replace box borders
9. **Pipes** - Replace pipe characters with simpler versions
10. **Tetris** - Replace box borders
11. **Tic-Tac-Toe** - Replace grid characters

## Testing in WSL

To test if the fixes are working:

```bash
# In WSL terminal
cd /path/to/terminal-toys
pip install -e .

# Test individual games
2048      # Should show simple ASCII borders
snake     # Should show simple ASCII walls

# Run the test script
python -c "from terminal_toys.terminal_utils import IS_WSL; print('Running in WSL:', IS_WSL)"
```

## Quick Fix for Remaining Games

For games that haven't been updated yet, you can run them with a workaround:

```bash
# Force simple terminal mode
export TERM=dumb
game-name

# Or use the Windows-specific versions which might work better
python terminal_toys/windows/game_name.py
```

## Implementation Priority

1. Games with heavy box-drawing (Tetris, Paint, Tic-Tac-Toe)
2. Animation-heavy games (Bouncing Ball, Pipes)
3. Games that already use simple characters (Fire, Matrix Rain)

The key is to maintain the visual appeal while ensuring compatibility across all terminal environments. 