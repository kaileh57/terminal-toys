#!/usr/bin/env python3
"""
Bouncing Ball for Windows - Physics-based ball animation
Controls: Space to add ball, C to clear, G to toggle gravity, Q to quit
"""

import os
import sys
import time
import random
import math
import msvcrt
import shutil

# Ball characters
BALL_CHARS = ['●', '○', '◉', '◎', '◯', '⬤']

# Colors
COLORS = [
    '\033[91m',  # Red
    '\033[92m',  # Green
    '\033[93m',  # Yellow
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
    '\033[97m',  # White
]
RESET = '\033[0m'

# Enable ANSI colors in Windows
os.system('color')

class Ball:
    def __init__(self, x, y, vx, vy, char, color):
        self.x = x
        self.y = y
        self.vx = vx  # Velocity X
        self.vy = vy  # Velocity Y
        self.char = char
        self.color = color
        self.trail = []  # Trail positions
        self.max_trail = 5
        
    def update(self, width, height, gravity, damping):
        """Update ball position and velocity"""
        # Store trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Apply gravity
        self.vy += gravity
        
        # Bounce off walls
        if self.x <= 0 or self.x >= width - 1:
            self.vx = -self.vx * damping
            self.x = max(0, min(width - 1, self.x))
            
        if self.y <= 0 or self.y >= height - 1:
            self.vy = -self.vy * damping
            self.y = max(0, min(height - 1, self.y))
            
            # Add some randomness to prevent getting stuck
            if abs(self.vy) < 0.1:
                self.vy = random.uniform(-0.5, -0.2)

class BouncingBalls:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size()
        self.width = min(self.width - 2, 78)
        self.height = min(self.height - 3, 28)
        self.balls = []
        self.gravity = 0.1
        self.damping = 0.9
        self.show_trails = True
        
        # Add initial balls
        for _ in range(3):
            self.add_random_ball()
            
    def add_random_ball(self):
        """Add a ball with random properties"""
        x = random.randint(5, self.width - 5)
        y = random.randint(2, 10)
        vx = random.uniform(-2, 2)
        vy = random.uniform(-1, 1)
        char = random.choice(BALL_CHARS)
        color = random.choice(COLORS)
        self.balls.append(Ball(x, y, vx, vy, char, color))
        
    def update(self):
        """Update all balls"""
        for ball in self.balls:
            ball.update(self.width, self.height, self.gravity, self.damping)
            
        # Check for collisions between balls
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                # Simple collision detection
                dx = ball2.x - ball1.x
                dy = ball2.y - ball1.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist < 2:  # Collision threshold
                    # Elastic collision
                    # Swap velocities (simplified)
                    ball1.vx, ball2.vx = ball2.vx * 0.9, ball1.vx * 0.9
                    ball1.vy, ball2.vy = ball2.vy * 0.9, ball1.vy * 0.9
                    
                    # Separate balls
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        ball1.x -= dx
                        ball1.y -= dy
                        ball2.x += dx
                        ball2.y += dy
                        
    def draw(self):
        """Draw the animation"""
        os.system('cls')
        
        # Create screen buffer
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw balls and trails
        for ball in self.balls:
            # Draw trail
            if self.show_trails:
                for i, (tx, ty) in enumerate(ball.trail):
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        opacity = i / len(ball.trail)
                        if opacity < 0.3:
                            screen[ty][tx] = '.'
                        elif opacity < 0.6:
                            screen[ty][tx] = '·'
                        else:
                            screen[ty][tx] = '•'
                            
            # Draw ball
            x, y = int(ball.x), int(ball.y)
            if 0 <= x < self.width and 0 <= y < self.height:
                screen[y][x] = (ball.char, ball.color)
                
        # Draw border
        print("┌" + "─" * self.width + "┐")
        
        # Draw screen
        for row in screen:
            print("│", end="")
            for cell in row:
                if isinstance(cell, tuple):
                    char, color = cell
                    print(f"{color}{char}{RESET}", end="")
                else:
                    print(cell, end="")
            print("│")
            
        print("└" + "─" * self.width + "┘")
        
        # Status
        print(f"Balls: {len(self.balls)} | Gravity: {self.gravity:.2f} | Trails: {'ON' if self.show_trails else 'OFF'}")
        print("Controls: Space add ball, C clear, G toggle gravity, T toggle trails, Q quit")

def get_key():
    """Get keyboard input (non-blocking) for Windows"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        return key.decode('utf-8', errors='ignore')
    return None

def main():
    try:
        # Hide cursor
        print('\033[?25l', end='', flush=True)
        
        animation = BouncingBalls()
        
        while True:
            # Handle input
            key = get_key()
            if key:
                if key == 'q' or key == 'Q':
                    break
                elif key == ' ':
                    animation.add_random_ball()
                elif key == 'c' or key == 'C':
                    animation.balls = []
                elif key == 'g' or key == 'G':
                    animation.gravity = -animation.gravity
                elif key == 't' or key == 'T':
                    animation.show_trails = not animation.show_trails
                    
            animation.update()
            animation.draw()
            time.sleep(0.1)  # Slower update to reduce flickering
            
    finally:
        # Show cursor
        print('\033[?25h', end='', flush=True)
        os.system('cls')

if __name__ == "__main__":
    main() 