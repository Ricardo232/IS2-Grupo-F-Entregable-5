# game options/settings
import pygame as pg
import json
from os import path

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (0, 200, 0)
LIGHT_BLACK = (60, 60, 55)
DARK_GREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
DOWN_RED = (216, 40, 35)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
FUCHSIA = (255, 0, 255)
COLORKEY = (34, 177, 76)


TITLE = "Zombie"
WIDTH = 800 #1024
HEIGHT = 640 #800
TILESIZE = 40
BGCOLOR = DARK_GREY
FPS = 60
GAME_FOLDER = path.dirname(__file__)
IMAGE_FOLDER = path.join(GAME_FOLDER, "img")
IMAGE_KEY = "Images"

#Load Data
DATAFILE = path.join(path.join(GAME_FOLDER, "data"), "data.json")
with open(DATAFILE) as json_data:
    GAMEDATA = json.load(json_data)

#Intro Settings
INTRO_TITLE = "DOOM KINGDOM"
INTRO_FOLDER = path.join(IMAGE_FOLDER, "Background")

#Map Settings
MAP_FOLDER = path.join(IMAGE_FOLDER, "Maps")
TILEDMAP_FOLDER = path.join(MAP_FOLDER, "Act_1")

# Player Settings
PLAYER_KEY = "Player"
PLAYER_SPEED = 200
PLAYER_HIT_RECT = pg.Rect(0, 0, 32, 32)
PLAYER_CLASS = "Warrior"
PLAYER_LETTER = "P"

#Player Image Settings
PLAYER_EQUIPMENT = "Light Armor with Sword & Shield"
PLAYER_SPRITESHEET_GENERATOR = "%s in %s.png"
PLAYER_FOLDER = path.join(IMAGE_FOLDER, "Class")
PLAYER_CLASS_FOLDER = path.join(PLAYER_FOLDER, PLAYER_CLASS)

# Mob Settings
MOB_KEY = "Mob"
MOB_SPEED = 100
MOB_HIT_RECT = pg.Rect(0, 0, 32, 32)
MOB_LETTER = "M"

# Mob Image Settings
MOB_FOLDER = path.join(IMAGE_FOLDER, "Enemies")
MOB_FILETYPE = "%s.png"

# HUD Folder
HUD_FOLDER = path.join(IMAGE_FOLDER, "HUD")
