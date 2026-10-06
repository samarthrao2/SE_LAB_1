"""
GameEngine: owns the player and all coins.

Starter version: one coin type, no obstacles, no timer yet. Coin
collection also has a known bug (see how `update` uses check_collection
below) that Task 1 asks you to fix - collected coins are never removed,
so standing on one keeps awarding points every frame.
"""

import random
import pygame

from game.player import Player
from game.coin import Coin
from game.obstacle import Obstacle
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT

NUM_COINS = 6
NUM_OBSTACLES = 4
STARTING_LIVES = 3
INVINCIBLE_FRAMES = 60  # ~1 second at 60 FPS after being hit
FPS = 60
ROUND_SECONDS = 30

# (name, value, color, spawn weight): bronze is common, gold is rare.
COIN_TYPES = [
    ("bronze", 1, (205, 127, 50), 6),
    ("silver", 3, (200, 200, 215), 3),
    ("gold", 5, (255, 215, 0), 1),
]


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        """Start a fresh round: score, lives, timer, and the field."""
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)
        self.obstacles = []
        for _ in range(NUM_OBSTACLES):
            self.obstacles.append(self._random_obstacle())
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]
        self.score = 0
        self.lives = STARTING_LIVES
        self.invincible = 0  # frames of hit-immunity remaining
        self.frames_left = ROUND_SECONDS * FPS
        self.game_over = False

    def _random_obstacle(self):
        # Keep the player's start area clear and obstacles fully inside the
        # play area and off each other.
        half = Obstacle(0, 0).size // 2
        start_zone = self.player.get_rect().inflate(120, 120)
        while True:
            x = random.randint(half, WIDTH - half)
            y = random.randint(half, HEIGHT - half)
            ob = Obstacle(x, y)
            rect = ob.get_rect()
            if rect.colliderect(start_zone):
                continue
            if any(rect.colliderect(o.get_rect()) for o in self.obstacles):
                continue
            return ob

    def _random_coin(self):
        while True:
            x = random.randint(30, WIDTH - 30)
            y = random.randint(30, HEIGHT - 30)
            spot = pygame.Rect(x - 12, y - 12, 24, 24)
            if not any(spot.colliderect(o.get_rect()) for o in self.obstacles):
                break
        name, value, color, _ = random.choices(
            COIN_TYPES, weights=[t[3] for t in COIN_TYPES]
        )[0]
        return Coin(x=x, y=y, radius=12, value=value, color=color, kind=name)

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed
        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return
        collected = check_collection(self.player, self.coins)
        for coin in collected:
            self.score += coin.value
            # Remove the coin so it can only be collected once, and spawn a
            # replacement so the play area never runs out of coins.
            self.coins.remove(coin)
            self.coins.append(self._random_coin())

        if self.invincible > 0:
            self.invincible -= 1
        elif any(self.player.get_rect().colliderect(o.get_rect())
                 for o in self.obstacles):
            # One life per hit; brief immunity so overlapping doesn't drain
            # a life every frame.
            self.lives = max(0, self.lives - 1)
            self.invincible = INVINCIBLE_FRAMES

        self.frames_left -= 1
        if self.frames_left <= 0 or self.lives <= 0:
            self.frames_left = max(0, self.frames_left)
            self.game_over = True

    @property
    def seconds_left(self):
        return (self.frames_left + FPS - 1) // FPS  # round up

    def draw(self, surface, font):
        from game import renderer
        # Flash the player while invincible.
        flashing = self.invincible > 0 and (self.invincible // 6) % 2 == 0
        renderer.draw_scene(surface, self.player, self.coins,
                            self.obstacles, hide_player=flashing)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 36))
        renderer.draw_text(surface, font, f"Time: {self.seconds_left}", (10, 62))
        if self.game_over:
            renderer.draw_game_over(surface, font, self.score)
