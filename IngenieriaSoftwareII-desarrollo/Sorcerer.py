import pygame as pg
from settings import *
from keyhandler import *
from mechanics import *
from imagemanager import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.rect_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
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
        self.image_manager.load_player_images(self.states, self.keyhandler)
        self.state_name = "Idle"
        self.state = self.states[self.state_name]
        self.hit_rect = PLAYER_HIT_RECT

    def load_attributes(self):
        self.totalhealth = 500
        self.currenthealth = 500
        self.previoushealth = 500
        self.damage = 40
        self.hit_rate = 200
        self.defense = 75
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

    def update(self):
        for key, value in self.state.done.items():
            if value:
                self.flip_state(key)

        self.state.update()
        self.vel = self.state.vel
        self.image = self.state.image
        if not hasattr(self, "rect"):
            self.rect = self.image.get_rect()
        self.pos.x += round(self.vel.x, 0)
        self.pos.y += round(self.vel.y, 0)
        self.hit_rect.centerx = self.pos.x
        detect_collision(self, self.game.rect_sprites, "x")
        self.hit_rect.centery = self.pos.y
        detect_collision(self, self.game.rect_sprites, "y")
        self.rect.center = self.hit_rect.center

    def isdead(self):
        if self.currenthealth <= 0:
            self.previoushealth = self.currenthealth
            return True
        return False

class PlayerState(pg.sprite.Sprite):
    def __init__(self, player):
        pg.sprite.Sprite.__init__(self)
        self.image_manager = ImageManager.get_instance()
        self.keyhandler = KeyHandler.get_instance()
        self.game = player.game
        self.player = player
        self.hit_rect = PLAYER_HIT_RECT
        self.inital_data()

    def inital_data(self):
        self.current_frame = 0
        self.last_update = 0
        self.direction = "down"
        self.persistence = {"direction": self.direction}

    def start_up(self, direction_persistence):
        self.persistence = direction_persistence

    def gets_hit(self):
        if self.player.previoushealth > self.player.currenthealth:
            self.player.previoushealth = self.player.currenthealth
            return True
        return False

    def events(self):
        pass

    def update(self):
        pass

    def action(self, action_type, action_dir):
        self.last_dir = action_dir
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(action_type[action_dir])
            self.image = action_type[action_dir][self.current_frame]

class Idle(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Walk": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.direction = self.persistence["direction"]

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.gets_hit():
            self.done["GetHit"] = True
            return False

        for key, value in self.keyhandler.move_keys.items():
            if keys[value[2]]:
                self.done["Walk"] = True
                return False

        for key, value in self.keyhandler.action_keys.items():
            if keys[value]:
                self.done["Attack"] = True
                return False

    def update(self):
        self.vel = vec(0, 0)
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

# class IdleTown(PlayerState):
#
# class TownWalk(PlayerState):


class Walk(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.keyhandler.move_keyspressed = []
        self.direction = self.persistence["direction"]

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.gets_hit():
            self.done["GetHit"] = True
        elif len(self.keyhandler.move_keyspressed) == 0:
            self.persistence["direction"] = self.direction
            self.done["Idle"] = True
        elif keys[pg.K_q]:
            self.persistence["direction"] = self.direction
            self.done["Attack"] = True

    def update(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        for key, value in self.keyhandler.move_keys.items():
            if keys[value[2]]:
                self.keyhandler.insert_key(key)
                self.vel.x += value[0] * PLAYER_SPEED
                self.vel.y += value[1] * PLAYER_SPEED
            else:
                self.keyhandler.remove_key(key)

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

        self.keyhandler.previous_key = self.direction
        self.direction = self.keyhandler.get_move_direction()
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class Attack(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "GetHit": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def check(self, direction):
        if not self.try_hit:
            self.try_hit = True
            posx = self.player.pos.x + self.keyhandler.vel_directions[self.direction][1] * (self.player.hit_rect.width / 2 + 1)
            posy = self.player.pos.y + self.keyhandler.vel_directions[self.direction][2] * (self.player.hit_rect.height / 2 + 1)
            for mob in self.game.mob_sprites.sprites():
                if mob.hit_rect.collidepoint(posx, posy) and hit(self.player.hit_rate, mob.defense, self.player.level, mob.level):
                    mob.currenthealth -= self.player.damage

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            for key, value in self.keyhandler.action_keys.items():
                if not keys[value]:
                    self.done["Idle"] = True

    def update(self):
        self.vel = vec(0, 0)
        if self.current_frame == 9:
            self.check(self.direction)
        if self.current_frame == 0:
            self.try_hit = False
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class GetHit(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "Die": False}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def events(self):
        if self.player.isdead():
            self.done["Die"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            self.done["Idle"] = True

    def update(self):
        self.vel = vec(0, 0)
        if self.gets_hit():
            self.current_frame = 0
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class Die(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.finish = False
        self.done = {"None": None}

    def start_up(self, persistence):
        self.persistence = persistence
        self.current_frame = 0
        self.direction = self.persistence["direction"]

    def update(self):
        self.vel = vec(0, 0)
        if not self.finish:
            self.action(self.image_manager.player[self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.player[self.__class__.__name__][self.direction]) - 1:
            print(len(self.image_manager.player[self.__class__.__name__][self.direction]) - 1)
            self.finish = True
            self.player.remove(self.player.groups)
            self.player.add(self.game.dead_sprites)
            self.game.gameover = True
