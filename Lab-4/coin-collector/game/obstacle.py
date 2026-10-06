"""
Obstacle: a static square the player must avoid. Touching one costs a life.
"""

import pygame


class Obstacle:
    def __init__(self, x, y, size=36, color=(200, 50, 50)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2), int(self.y - self.size / 2),
            self.size, self.size,
        )
