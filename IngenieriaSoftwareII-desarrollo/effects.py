import pygame as pg
from settings import *
vec = pg.math.Vector2

class Fireball(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups = game.effect_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.pos = vec(pos)
