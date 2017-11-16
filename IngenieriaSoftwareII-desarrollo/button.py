import pygame as pg
from os import path
from settings import *

class Button:
    def __init__(self, text):
        self.font = pg.font.SysFont("Arial", 25)
        self.text = self.font.render(text, True, WHITE)
        self.textrect = self.text.get_rect()
        self.width = WIDTH * 0.2
        self.height = HEIGHT * 0.1
        self.surface = pg.Surface((self.width, self.height))
        self.rect = self.surface.get_rect()
        self.textrect.center = self.rect.center

    def color(self, color):
        self.surface.fill(color)
        self.surface.blit(self.text, self.textrect)

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def update(self, mouse, click):
        if self.rect.left <= mouse[0] <= self.rect.right and self.rect.top <= mouse[1] <= self.rect.bottom:
            self.color(DOWN_RED)
            if click[0] == 1:
                self.clicked = True
        else:
            self.color(LIGHT_BLACK)
