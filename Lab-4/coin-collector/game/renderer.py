"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (35, 45, 35)
COLOR_PLAYER = (80, 180, 255)
COLOR_TEXT = (255, 255, 255)


def draw_scene(surface, player, coins, obstacles=(), hide_player=False):
    surface.fill(COLOR_BG)
    for ob in obstacles:
        pygame.draw.rect(surface, ob.color, ob.get_rect(), border_radius=3)
    for coin in coins:
        pygame.draw.circle(surface, coin.color, (int(coin.x), int(coin.y)), coin.radius)
    if not hide_player:
        pygame.draw.rect(surface, COLOR_PLAYER, player.get_rect(), border_radius=4)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)


def draw_game_over(surface, font, score):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))
    cx, cy = surface.get_width() // 2, surface.get_height() // 2
    for text, dy, color in (
        ("GAME OVER", -50, (255, 220, 80)),
        (f"Final Score: {score}", 0, COLOR_TEXT),
        ("Press R to play again", 50, COLOR_TEXT),
    ):
        surf = font.render(text, True, color)
        surface.blit(surf, surf.get_rect(center=(cx, cy + dy)))
