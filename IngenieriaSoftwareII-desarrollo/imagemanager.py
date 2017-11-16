import pygame as pg
import sys
from spritesheet import *
from os import path
from settings import *

class ImageManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = ImageManager()
        return cls._instance

    def load_hud_images(self):
        spritesheet = pg.image.load(path.join(HUD_FOLDER, "hud.png")).convert()
        self.hud = {"Life": (0, self.get_image(spritesheet, 0, 0, 160, 128), self.get_image(spritesheet, 0, 128, 160, 128)),
                    "Mana": (1, self.get_image(spritesheet, 160, 0, 160, 128), self.get_image(spritesheet, 160, 128, 160, 128))}


    def load_player_images(self, actions, keyhandler):
        self.player = {}
        data = GAMEDATA[PLAYER_KEY][PLAYER_CLASS][IMAGE_KEY]
        self.dtry_init(self.player, actions, keyhandler.vel_directions)
        spritesheet = pg.image.load(path.join(PLAYER_CLASS_FOLDER, PLAYER_SPRITESHEET_GENERATOR % (PLAYER_CLASS, PLAYER_EQUIPMENT))).convert()
        for actionkey, action in self.player.items():
            end = data[actionkey]["n"]
            for direction in action.values():
                for i in range(end):
                    direction.append(self.create_surface(data["BaseSurface"][0], data["BaseSurface"][1]))
        for key, action in self.player.items():
            end = data[key]["x"]
            y = data[key]["y"]
            for direction in action.values():
                x = end
                for image in direction:
                    surf = self.get_image(spritesheet, x, y, data[key]["w"], data[key]["h"])
                    image.blit(surf, (data[key]["offsetx"], data[key]["offsety"]))
                    x += data[key]["w"]
                y += data[key]["h"] + 1

    def load_mob_images(self, mob_type, actions, keyhandler):
        if not hasattr(self, "mob"):
            self.mob = {}
        if mob_type not in self.mob:
            self.mob[mob_type] = {}
            data = GAMEDATA[MOB_KEY][mob_type][IMAGE_KEY]
            self.dtry_init(self.mob[mob_type], actions, keyhandler.vel_directions)
            spritesheet = pg.image.load(path.join(MOB_FOLDER, MOB_FILETYPE % (mob_type)))
            for actionkey, action in self.mob[mob_type].items():
                end = data[actionkey]["n"]
                for direction in action.values():
                    for i in range(end):
                        direction.append(self.create_surface(data["BaseSurface"][0], data["BaseSurface"][1]))
            for key, action in self.mob[mob_type].items():
                end = data[key]["x"]
                y = data[key]["y"]
                for direction in action.values():
                    x = end
                    for image in direction:
                        surf = self.get_image(spritesheet, x, y, data[key]["w"], data[key]["h"])
                        image.blit(surf, (data[key]["offsetx"], data[key]["offsety"]))
                        x += data[key]["w"]
                    y += data[key]["h"] + 1

    def create_surface(self, width, height, color = WHITE):
        image = pg.Surface((width, height))
        image.fill(color)
        image.set_colorkey(color)
        return image

    def get_image(self, spritesheet, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(spritesheet, (0, 0), (x, y, width, height))
        return image

    def dtry_init(self, dtry, actions, directions):
        for action_key in actions:
            dtry[action_key] = {}
            for direction_key in directions:
                dtry[action_key][direction_key] = []

    def loading_screen(self, n, screen):
        bg = pg.image.load(path.join(INTRO_FOLDER, "Loading House.png")).convert()
        screen.blit(bg, (0, 0))
        bar = pg.Surface((674, 37))
        bar.fill(GREEN)
        rect = bar.get_rect()
        for i in range(n):
            screen.blit(bar, (63, 558), (0, 0, rect.width * i / (n - 1), rect.height))
            pg.display.flip()
            yield None
