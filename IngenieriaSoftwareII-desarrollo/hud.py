import pygame as pg
from os import *
from settings import *
from imagemanager import *

class HUD:
    def __init__(self, game):
        self.image_manager = ImageManager.get_instance()
        self.image = (Life(game, WIDTH * 0.2, HEIGHT * 0.2,), Mana(game, WIDTH * 0.2, HEIGHT * 0.2,))
        self.load_images()

    def load_images(self):
        self.image_manager.load_hud_images()
        for images in self.image_manager.hud.values():
            images[2].set_colorkey((0, 1, 0))
            for i in range(1, len(images)):
                self.image[images[0]].image.blit(images[i], (0, 0))

    def update(self, n, decide):
        if decide == "Life":
            self.image[0].get_life(n, self.image_manager)
        if decide == "Mana":
            self.image[1].get_mana(n, self.image_manager)

class Life(pg.sprite.Sprite):
    def __init__(self, game, w, h):
        self.groups = game.hud_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.y = (0, h * 0.875)
        self.image = pg.Surface((w, h))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.rect.bottomleft = ((0, HEIGHT))

    def get_life(self, n, manager):
        self.image.fill(WHITE)
        self.image.blit(manager.hud["Life"][1], (0, 0))
        self.image.blit(manager.hud["Life"][2], (0, self.y[1] * n), (0, self.y[1] * n, self.width, self.height))

class Mana(pg.sprite.Sprite):
    def __init__(self, game, w, h):
        self.groups = game.hud_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.y = (h * 0.125, h * 0.875)
        self.image = pg.Surface((w, h))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.rect.bottomright = ((WIDTH, HEIGHT))

    def get_mana(self, n, manager):
        self.image.fill(WHITE)
        self.image.blit(manager.hud["Mana"][1], (0, 0))
        self.image.blit(manager.hud["Mana"][2], (0, self.y[0] + self.y[1] * n), (0, self.y[0] + self.y[1] * n, self.width, self.height))
