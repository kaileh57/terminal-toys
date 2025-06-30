#!/usr/bin/env python3
"""
Terminal Paint - Cross-platform ASCII art drawing program
Controls: Arrow keys to move, Space to draw, C to clear, 1-8 for colors,
         B/N/M for brush size, E to erase, Q to quit
Works on Windows, macOS, and Linux
"""

import sys
import time
from .terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput, flush_output,
    enable_alternate_screen, disable_alternate_screen, move_cursor,
    IS_WSL, render_frame_wsl
)

# Colors
COLORS = {
    '1': ('\033[91m', 'Red'),     # Red
    '2': ('\033[92m', 'Green'),   # Green
    '3': ('\033[93m', 'Yellow'),  # Yellow
    '4': ('\033[94m', 'Blue'),    # Blue
    '5': ('\033[95m', 'Magenta'), # Magenta
    '6': ('\033[96m', 'Cyan'),    # Cyan
    '7': ('\033[97m', 'White'),   # White
    '8': ('\033[90m', 'Gray'),    # Gray
}
RESET = '\033[0m'

# Brush styles
BRUSHES = {
    'B': ('█' if not IS_WSL else '#', 'Block'),
    'N': ('●' if not IS_WSL else 'O', 'Circle'),
    'M': ('▓' if not IS_WSL else '=', 'Shade'),
}

class Paint:
    def __init__(self):
        width, height = get_terminal_size()
        self.width = min(width - 2, 78)
        self.height = min(height - 5, 28)
        self.canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        self.cursor_x = self.width // 2
        self.cursor_y = self.height // 2
        self.current_color = '7'  # White
        self.current_brush = 'B'  # Block
        self.drawing = False
        self.erasing = False
        
    def paint_pixel(self, x, y):
        """Paint a pixel on the canvas"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.erasing:
                self.canvas[y][x] = ' '
                self.colors[y][x] = None
            else:
                self.canvas[y][x] = BRUSHES[self.current_brush][0]
                self.colors[y][x] = self.current_color
                
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[None for _ in range(self.width)] for _ in range(self.height)]
        
    def draw(self):
        """Draw the paint program"""
        output = []
        
        # Draw canvas border - use simple characters for WSL
        if IS_WSL:
            output.append("+" + "-" * self.width + "+")
        else:
            output.append("┌" + "─" * self.width + "┐")
        
        # Draw canvas
        for y in range(self.height):
            line = "|" if IS_WSL else "│"
            for x in range(self.width):
                if x == self.cursor_x and y == self.cursor_y:
                    # Draw cursor
                    if self.erasing:
                        line += f"\033[7m \033[0m"  # Inverted space
                    else:
                        color = COLORS[self.current_color][0]
                        char = '+' if IS_WSL else '┼'
                        line += f"{color}{char}{RESET}"
                else:
                    char = self.canvas[y][x]
                    if char != ' ' and self.colors[y][x]:
                        color = COLORS[self.colors[y][x]][0]
                        line += f"{color}{char}{RESET}"
                    else:
                        line += char
            line += "|" if IS_WSL else "│"
            output.append(line)
            
        # Draw bottom border
        if IS_WSL:
            output.append("+" + "-" * self.width + "+")
        else:
            output.append("└" + "─" * self.width + "┘")
        
        # Status bar
        color_name = COLORS[self.current_color][1]
        brush_name = BRUSHES[self.current_brush][1]
        mode = "ERASE" if self.erasing else "DRAW"
        output.append(f"\nColor: {COLORS[self.current_color][0]}{color_name}{RESET} | Brush: {brush_name} | Mode: {mode}")
        output.append("<-^->v move, Space draw, C clear, 1-8 colors, B/N/M brush, E erase, Q quit")
        
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
        
        paint = Paint()
        paint.draw()
        
        while True:
            # Handle input
            key = kb.get_key(0.01)
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'c' or key == 'C':
                    paint.clear_canvas()
                elif key in COLORS:
                    paint.current_color = key
                    paint.erasing = False
                elif key.upper() in BRUSHES:
                    paint.current_brush = key.upper()
                elif key == 'e' or key == 'E':
                    paint.erasing = not paint.erasing
                elif key == 'UP':
                    paint.cursor_y = max(0, paint.cursor_y - 1)
                    if paint.drawing:
                        paint.paint_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'DOWN':
                    paint.cursor_y = min(paint.height - 1, paint.cursor_y + 1)
                    if paint.drawing:
                        paint.paint_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'LEFT':
                    paint.cursor_x = max(0, paint.cursor_x - 1)
                    if paint.drawing:
                        paint.paint_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'RIGHT':
                    paint.cursor_x = min(paint.width - 1, paint.cursor_x + 1)
                    if paint.drawing:
                        paint.paint_pixel(paint.cursor_x, paint.cursor_y)
                elif key == ' ':
                    paint.drawing = not paint.drawing
                    if paint.drawing:
                        paint.paint_pixel(paint.cursor_x, paint.cursor_y)
                        
                paint.draw()
            
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