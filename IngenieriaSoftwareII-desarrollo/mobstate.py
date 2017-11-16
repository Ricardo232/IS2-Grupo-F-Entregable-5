import pygame as pg
import random
import math
import copy
from settings import *
from keyhandler import *
from mechanics import *
from imagemanager import *

vec = pg.math.Vector2

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.rect_sprites, game.mob_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.player_detected = False
        self.mob_class = "Felltwin"
        self.load_data()
        self.load_attributes()

    def load_data(self):
        self.states = {"Idle": Idle(self),
                       "Walk": Walk(self),
                       "Attack": Attack(self),
                       "GetHit": GetHit(self),
                       "Die": Die(self)}

        self.image_manager = ImageManager.get_instance()
        self.keyhandler = KeyHandler.get_instance()
        self.image_manager.load_mob_images(self.mob_class, self.states, self.keyhandler)
        self.state_name = "Idle"
        self.state = self.states[self.state_name]
        self.hit_rect = copy.copy(MOB_HIT_RECT)
        self.player_collision = False

    def load_attributes(self):
        self.totalhealth = self.currenthealth = self.previoushealth = 200
        self.damage = 40
        self.hit_rate = 100
        self.defense = 50
        self.level = 1

    def flip_state(self, state_name):
        """Switch to the next game state."""
        self.state.done[state_name] = False
        self.state_name = state_name
        persistent = self.state.persistence
        self.state = self.states[self.state_name]
        self.state.start_up(persistent)

    def events(self):
        self.state.events()

    def update(self, dt):
        for key, value in self.state.done.items():
            if value:
                self.flip_state(key)
        self.state.update(dt)
        self.image = self.state.image
        if self.currenthealth <= 0:
            return None
        if not hasattr(self, "rect"):
            self.rect = self.image.get_rect()
            self.health = Health(self.rect.width, 7)
        self.vel = self.state.vel
        self.pos.x += round(self.vel.x, 0)
        self.pos.y += round(self.vel.y, 0)
        self.hit_rect.centerx = self.pos.x
        if collide_hit_rect(self, self.game.player):
            self.player_collision = True
        detect_collision(self, self.game.rect_sprites, "x")
        self.hit_rect.centery = self.pos.y
        if collide_hit_rect(self, self.game.player):
            self.player_collision = True
        detect_collision(self, self.game.rect_sprites, "y")
        self.rect.center = self.hit_rect.center

    def detect_player(self):
        if self.pos.distance_to(self.game.player.pos) < 400:
            self.player_detected = True

    def gets_hit(self):
        if self.previoushealth > self.currenthealth:
            self.previoushealth = self.currenthealth
            return True
        return False

    def isdead(self):
        if self.currenthealth <= 0:
            self.previoushealth = self.currenthealth
            return True
        return False

    def draw_health(self, screen):
        ratio = self.currenthealth / self.totalhealth
        width = int(self.rect.width * ratio)
        self.health.set_width(width, 7)
        self.health.set_pos(self.rect.x, self.rect.y)
        self.health.get_color(ratio)
        screen.blit(self.health.image, self.game.camera.apply(self.health))

class MobState(pg.sprite.Sprite):
    def __init__(self, mob):
        pg.sprite.Sprite.__init__(self)
        self.image_manager = ImageManager.get_instance()
        self.keyhandler = KeyHandler.get_instance()
        self.game = mob.game
        self.mob = mob
        self.mob_class = mob.mob_class
        self.inital_data()

    def inital_data(self):
        self.current_frame = 0
        self.last_update = 0
        self.direction = "down"
        self.persistence = {"direction": self.direction}

    def start_up(self, direction_persistence):
        self.persistence = direction_persistence

    def events(self):
        pass

    def update(self, dt):
        pass

    def action(self, action_type, action_dir):
        self.last_dir = action_dir
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(action_type[action_dir])
            self.image = action_type[action_dir][self.current_frame]
            self.rect = self.image.get_rect()

class Idle(MobState):
    def __init__(self, mob):
        super().__init__(mob)
        self.done = {"Walk": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def events(self):
        if self.mob.isdead():
            self.done["Die"] = True
        elif self.mob.gets_hit():
            self.done["GetHit"] = True
        elif self.mob.player_detected or (self.current_frame + 1) % len(self.image_manager.mob[self.mob_class][self.__class__.__name__][self.direction]) == 0:
            self.done["Walk"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        self.mob.detect_player()
        self.action(self.image_manager.mob[self.mob_class][self.__class__.__name__], self.direction)

class Walk(MobState):
    def __init__(self, mob):
        super().__init__(mob)
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.mob.player_collision = False
        self.persistence = persistence
        self.direction = self.persistence["direction"]
        self.random_direction = self.keyhandler.get_key(random.randint(0, 7))
        self.distancia = 0

    def follow(self, dt):
        direction = ""
        distance_vector = (self.game.player.pos - self.mob.pos)
        distance_vector.x = round(distance_vector.x, 2)
        distance_vector.y = round(distance_vector.y, 2)
        for key, value in self.keyhandler.move_keys.items():
            if distance_vector.y != 0:
                distance_vector.y = math.copysign(1, distance_vector.y)
                direction += key if value[1] == distance_vector.y else ""
        for key, value in self.keyhandler.move_keys.items():
            if distance_vector.x != 0:
                distance_vector.x = math.copysign(1, distance_vector.x)
                direction += key if value[0] == distance_vector.x else ""
        self.vel = distance_vector * MOB_SPEED * dt

        return direction

    def events(self):
        if self.mob.isdead():
            self.done["Die"] = True
        elif self.mob.gets_hit():
            self.done["GetHit"] = True
        elif self.distancia >= 160 and not self.mob.player_detected:
            self.persistence["direction"] = self.direction
            self.done["Idle"] = True
        elif self.mob.player_collision:
            self.persistence["direction"] = self.direction
            self.done["Attack"] = True

    def update(self, dt):
        self.mob.detect_player()
        self.vel = vec(0, 0)
        if not self.mob.player_detected:
            self.direction = self.random_direction
            self.vel.x += self.keyhandler.vel_directions[self.random_direction][0] * MOB_SPEED * dt
            self.vel.y += self.keyhandler.vel_directions[self.random_direction][1] * MOB_SPEED * dt
            self.distancia += MOB_SPEED
        else:
            self.direction = self.follow(dt)

        if self.vel.x != 0 and self.vel.y != 0:
            self.distancia *= 1.4142
            self.vel *= 0.7071
        self.action(self.image_manager.mob[self.mob_class][self.__class__.__name__], self.direction)

class Attack(MobState):
    def __init__(self, mob):
        super().__init__(mob)
        self.done = {"Idle": False,
                     "Walk": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def apply_damage(self):
        if not self.try_hit:
            self.try_hit = True
            if hit(self.mob.hit_rate, self.game.player.defense, self.mob.level, self.game.player.level):
                self.game.player.currenthealth -= self.mob.damage
                n = 1 - self.game.player.currenthealth/self.game.player.totalhealth
                self.game.hud.update(n, "Life")

    def events(self):
        if self.mob.isdead():
            self.done["Die"] = True
        elif self.mob.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.mob[self.mob_class][self.__class__.__name__][self.direction]) == 0 and self.mob.pos.distance_to(self.game.player.pos) > 32:
            self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        if self.current_frame == 0:
            self.try_hit = False
        if self.current_frame == 10:
            self.apply_damage()
        self.action(self.image_manager.mob[self.mob_class][self.__class__.__name__], self.persistence["direction"])

class GetHit(MobState):
    def __init__(self, mob):
        super().__init__(mob)
        self.done = {"Idle": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def events(self):
        if (self.current_frame + 1) % len(self.image_manager.mob[self.mob_class][self.__class__.__name__][self.direction]) == 0:
            self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        if self.mob.gets_hit():
            self.current_frame = 0
        self.action(self.image_manager.mob[self.mob_class][self.__class__.__name__], self.direction)

class Die(MobState):
    def __init__(self, mob):
        super().__init__(mob)
        self.hit_rect = pg.Surface((0, 0))
        self.finish = False
        self.done = {"None": None}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def update(self, dt):
        self.vel = vec(0, 0)
        if not self.finish:
            self.action(self.image_manager.mob[self.mob_class][self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.mob[self.mob_class][self.__class__.__name__][self.direction]) - 1:
            self.finish = True
            self.mob.remove(self.mob.groups)
            self.mob.add(self.game.dead_sprites)

class Health:
    def __init__(self, width, height):
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect()

    def get_color(self, ratio):
        if ratio > 0.6:
            self.image.fill(GREEN)
        elif ratio > 0.3:
            self.image.fill(YELLOW)
        else:
            self.image.fill(RED)

    def set_width(self, width, height):
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect()

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y
