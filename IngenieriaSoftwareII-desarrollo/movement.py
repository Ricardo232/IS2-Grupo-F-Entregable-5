import pygame

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (0, 255, 0)
BLUE = (0, 0, 200)

screen_width, screen_height = 800, 600

size = (screen_width, screen_height)
GameDisplay = pygame.display.set_mode(size)
