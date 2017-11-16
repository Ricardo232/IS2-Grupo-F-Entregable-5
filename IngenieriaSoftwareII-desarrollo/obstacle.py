import pygame as pg
from settings import *

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.rect_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((80, 40))
        self.image.fill(BLUE)
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
