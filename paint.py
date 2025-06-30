#!/usr/bin/env python3
"""
ASCII Paint - Cross-platform terminal drawing application
Controls: Arrow keys to move, Space to draw, C to change color, 
         E to erase, L for line mode, F to fill, S to save, Q to quit
Works on Windows, macOS, and Linux
"""

import sys
from collections import deque
from terminal_utils import (
    clear_screen, enable_ansi_colors, hide_cursor, show_cursor,
    get_terminal_size, KeyboardInput
)

# Colors
COLORS = [
    ('\033[97m', '█'),  # White
    ('\033[91m', '█'),  # Red
    ('\033[92m', '█'),  # Green
    ('\033[93m', '█'),  # Yellow
    ('\033[94m', '█'),  # Blue
    ('\033[95m', '█'),  # Magenta
    ('\033[96m', '█'),  # Cyan
    ('\033[90m', '░'),  # Gray
    ('\033[37m', '▒'),  # Light gray
    ('\033[30m', '▓'),  # Dark gray
]
RESET = '\033[0m'

class ASCIIPaint:
    def __init__(self):
        width, height = get_terminal_size()
        self.canvas_width = min(width - 2, 78)
        self.canvas_height = min(height - 5, 25)
        self.canvas = [[' ' for _ in range(self.canvas_width)] for _ in range(self.canvas_height)]
        self.cursor_x = self.canvas_width // 2
        self.cursor_y = self.canvas_height // 2
        self.current_color = 0
        self.drawing = False
        self.continuous_draw = False  # Track if space is held for drawing
        self.line_mode = False
        self.line_start = None
        self.erasing = False
        self.saved = False
        
    def draw_pixel(self, x, y):
        """Draw a pixel at the given position"""
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            if self.erasing:
                self.canvas[y][x] = ' '
            else:
                self.canvas[y][x] = (COLORS[self.current_color][0], COLORS[self.current_color][1])
                
    def draw_line(self, x1, y1, x2, y2):
        """Draw a line between two points using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.draw_pixel(x1, y1)
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
    def fill(self, x, y):
        """Flood fill from the given position"""
        if not (0 <= x < self.canvas_width and 0 <= y < self.canvas_height):
            return
            
        target = self.canvas[y][x]
        if target == (COLORS[self.current_color][0], COLORS[self.current_color][1]):
            return
            
        queue = deque([(x, y)])
        visited = set()
        
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
                
            if not (0 <= cx < self.canvas_width and 0 <= cy < self.canvas_height):
                continue
                
            if self.canvas[cy][cx] != target:
                continue
                
            visited.add((cx, cy))
            self.draw_pixel(cx, cy)
            
            # Add neighbors
            queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
            
    def save_canvas(self):
        """Save canvas to file"""
        filename = "ascii_art.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for row in self.canvas:
                line = ""
                for cell in row:
                    if isinstance(cell, tuple):
                        line += cell[1]
                    else:
                        line += cell
                f.write(line + '\n')
        self.saved = True
        
    def draw_screen(self):
        """Draw the entire screen"""
        clear_screen()
        
        # Draw top border
        print("┌" + "─" * self.canvas_width + "┐")
        
        # Draw canvas
        for y, row in enumerate(self.canvas):
            print("│", end="")
            for x, cell in enumerate(row):
                if x == self.cursor_x and y == self.cursor_y:
                    # Draw cursor
                    print('\033[7m', end='')  # Reverse video
                    
                if isinstance(cell, tuple):
                    print(f"{cell[0]}{cell[1]}{RESET}", end="")
                else:
                    print(cell, end="")
                    
                if x == self.cursor_x and y == self.cursor_y:
                    print('\033[27m', end='')  # Reset reverse video
            print("│")
            
        # Draw bottom border
        print("└" + "─" * self.canvas_width + "┘")
        
        # Draw status bar
        color_preview = f"{COLORS[self.current_color][0]}{COLORS[self.current_color][1]}{RESET}"
        if self.line_mode:
            mode = "LINE"
        elif self.erasing:
            mode = "ERASE"
        elif self.continuous_draw:
            mode = "DRAW (Continuous)"
        else:
            mode = "DRAW"
        print(f"\nMode: {mode} | Color: {color_preview} | Position: ({self.cursor_x},{self.cursor_y})")
        print("Controls: ←↑→↓ move, Space draw/toggle continuous, C color, E erase, L line, F fill, S save, Q quit")
        
        if self.saved:
            print("Saved to ascii_art.txt!")
            self.saved = False

def main():
    enable_ansi_colors()
    kb = KeyboardInput()
    
    try:
        hide_cursor()
        paint = ASCIIPaint()
        paint.draw_screen()  # Initial draw
        
        while True:
            # Get input
            key = kb.get_key()
            
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == 'UP':
                    paint.cursor_y = max(0, paint.cursor_y - 1)
                    # Draw if in continuous draw mode
                    if paint.continuous_draw and not paint.line_mode:
                        paint.draw_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'DOWN':
                    paint.cursor_y = min(paint.canvas_height - 1, paint.cursor_y + 1)
                    # Draw if in continuous draw mode
                    if paint.continuous_draw and not paint.line_mode:
                        paint.draw_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'LEFT':
                    paint.cursor_x = max(0, paint.cursor_x - 1)
                    # Draw if in continuous draw mode
                    if paint.continuous_draw and not paint.line_mode:
                        paint.draw_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'RIGHT':
                    paint.cursor_x = min(paint.canvas_width - 1, paint.cursor_x + 1)
                    # Draw if in continuous draw mode
                    if paint.continuous_draw and not paint.line_mode:
                        paint.draw_pixel(paint.cursor_x, paint.cursor_y)
                elif key == ' ':  # Space - draw/toggle continuous draw
                    if paint.line_mode:
                        if paint.line_start is None:
                            paint.line_start = (paint.cursor_x, paint.cursor_y)
                        else:
                            paint.draw_line(paint.line_start[0], paint.line_start[1],
                                          paint.cursor_x, paint.cursor_y)
                            paint.line_start = None
                    else:
                        # Toggle continuous draw mode
                        paint.continuous_draw = not paint.continuous_draw
                        if paint.continuous_draw:
                            # Draw current pixel when starting continuous draw
                            paint.draw_pixel(paint.cursor_x, paint.cursor_y)
                elif key == 'c' or key == 'C':  # Change color
                    paint.current_color = (paint.current_color + 1) % len(COLORS)
                    paint.continuous_draw = False  # Stop continuous draw when changing color
                elif key == 'e' or key == 'E':  # Toggle erase
                    paint.erasing = not paint.erasing
                    paint.continuous_draw = False  # Stop continuous draw
                    if paint.erasing:
                        paint.line_mode = False
                elif key == 'l' or key == 'L':  # Toggle line mode
                    paint.line_mode = not paint.line_mode
                    paint.line_start = None
                    paint.continuous_draw = False  # Stop continuous draw
                    if paint.line_mode:
                        paint.erasing = False
                elif key == 'f' or key == 'F':  # Fill
                    if not paint.erasing and not paint.line_mode:
                        paint.fill(paint.cursor_x, paint.cursor_y)
                    paint.continuous_draw = False  # Stop continuous draw
                elif key == 's' or key == 'S':  # Save
                    paint.save_canvas()
                
                # Redraw screen after action
                paint.draw_screen()
                    
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()

if __name__ == "__main__":
    main() 