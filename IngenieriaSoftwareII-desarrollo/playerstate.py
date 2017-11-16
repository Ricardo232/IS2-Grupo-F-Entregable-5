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
        self.lines = game.lines
        self.x = x
        self.y = y
        self.last_update = 0
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.load_data()
        self.load_attributes()

    def load_data(self):
        self.states = {"Idle": Idle(self),
                       "Walk": Walk(self),
                       "Attack": Attack(self),
                       "GetHit": GetHit(self),
                       "Die": Die(self),
                       "Fire": Fire(self),
                       "Lightning": Lightning(self),
                       "Smoke": Smoke(self)}

        self.image_manager = ImageManager.get_instance()
        self.keyhandler = KeyHandler.get_instance()
        self.image_manager.load_player_images(self.states, self.keyhandler)
        self.state_name = "Idle"
        self.state = self.states[self.state_name]
        self.hit_rect = PLAYER_HIT_RECT
        self.clock = pg.time.Clock()
        self.buffs = {"Fire": 0,
                      "Lightning": 0,
                      "Smoke": 0}

    def load_attributes(self):
        data = GAMEDATA[PLAYER_KEY][PLAYER_CLASS]["Stats"]
        self.basehealth = data["Health"]
        self.totalhealth = self.basehealth
        self.currenthealth = self.totalhealth
        self.previoushealth = self.totalhealth
        self.basemana = data["Mana"]
        self.totalmana = self.basemana
        self.currentmana = self.totalmana
        self.basedamage = data["Damage"]
        self.damage = self.basedamage
        self.base_hit_rate = data["Hit Rate"]
        self.hit_rate = self.base_hit_rate
        self.basedefense = data["Defense"]
        self.defense = self.basedefense
        self.baseblock = data["Block"]
        self.block = self.baseblock
        self.level = data["Level"]

    def flip_state(self, state_name):
        """Switch to the next game state."""
        self.state.done[state_name] = False
        self.state_name = state_name
        direction = self.state.direction
        self.state = self.states[self.state_name]
        self.state.start_up(direction)

    def events(self):
        self.state.events()

    def update(self, dt):
        self.buff()
        for key, value in self.state.done.items():
            if value:
                self.flip_state(key)

        self.state.update(dt)
        self.vel = self.state.vel
        self.image = self.state.image
        if not hasattr(self, "rect"):
            self.rect = self.image.get_rect()
        self.pos.x += round(self.vel.x, 0)
        self.pos.y += round(self.vel.y, 0)
        self.hit_rect.centerx = self.pos.x
        detect_collision(self, self.game.rect_sprites, "x")
        collide_line(self, self.lines, "x")
        self.hit_rect.centery = self.pos.y
        detect_collision(self, self.game.rect_sprites, "y")
        collide_line(self, self.lines, "y")
        self.rect.center = self.hit_rect.center

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

    def buff(self):
        self.clock.tick(FPS)
        now = pg.time.get_ticks() / 1000
        if self.totalhealth != self.basehealth:
            self.buffs["Fire"] -= self.clock.get_time() / 1000
            if self.buffs["Fire"] <= 0:
                self.totalhealth = self.basehealth
        if self.damage != self.basedamage:
            self.buffs["Lightning"] -= self.clock.get_time() / 1000
            if self.buffs["Lightning"] <= 0:
                self.damage = self.basedamage
        if self.defense != self.basedefense:
            self.buffs["Fire"] -= self.clock.get_time() / 1000
            if self.buffs["Fire"] <= 0:
                self.defense = self.basedefense

        if now - self.last_update > 5:
            self.last_update = now
            if self.totalhealth != self.currenthealth:
                self.currenthealth += 5
            if self.totalmana != self.currentmana:
                self.currentmana += 5

        n = 1 - self.currenthealth / self.totalhealth
        self.game.hud.update(n, "Life")
        n = 1 - self.currentmana / self.totalmana
        self.game.hud.update(n, "Mana")

class State:
    def __init__(self, player):
        pg.sprite.Sprite.__init__(self)
        self.image_manager = ImageManager.get_instance()
        self.keyhandler = KeyHandler.get_instance()
        self.game = player.game
        self.player = player
        self.inital_data()

    def inital_data(self):
        self.current_frame = 0
        self.last_update = 0
        self.direction = "down"

    def start_up(self, direction):
        self.direction = direction

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

class Idle(State):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Walk": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.direction = direction

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.player.gets_hit():
            self.done["GetHit"] = True
            return False

        for key, value in self.keyhandler.move_keys.items():
            if keys[value[2]]:
                self.done["Walk"] = True
                return False

        for key, value in self.keyhandler.action_keys.items():
            if keys[value]:
                self.done[key] = True
                return False

    def update(self, dt):
        self.vel = vec(0, 0)
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class Walk(State):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.keyhandler.move_keyspressed = []
        self.direction = direction

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.player.gets_hit():
            self.done["GetHit"] = True
        elif len(self.keyhandler.move_keyspressed) == 0:
            self.done["Idle"] = True
        else:
            for key, value in self.keyhandler.action_keys.items():
                if keys[value]:
                    self.done[key] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        for key, value in self.keyhandler.move_keys.items():
            if keys[value[2]]:
                self.keyhandler.insert_key(key)
                self.vel.x += value[0] * PLAYER_SPEED * dt
                self.vel.y += value[1] * PLAYER_SPEED * dt
            else:
                self.keyhandler.remove_key(key)

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

        self.keyhandler.previous_key = self.direction
        self.direction = self.keyhandler.get_move_direction()
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class Attack(State):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

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
        elif self.player.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            for key, value in self.keyhandler.action_keys.items():
                if keys[value]:
                    self.done[key] = True
                else:
                    self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        if self.current_frame == 9:
            self.check(self.direction)
        if self.current_frame == 0:
            self.try_hit = False
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class GetHit(State):
    def __init__(self, player):
        super().__init__(player)
        self.done = {"Idle": False,
                     "Die": False}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

    def events(self):
        if self.player.isdead():
            self.done["Die"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        if self.player.gets_hit():
            self.current_frame = 0
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)

class Die(State):
    def __init__(self, player):
        super().__init__(player)
        self.finish = False
        self.done = {"None": None}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

    def update(self, dt):
        self.vel = vec(0, 0)
        if not self.finish:
            self.action(self.image_manager.player[self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.player[self.__class__.__name__][self.direction]) - 1:
            self.finish = True
            self.player.remove(self.player.groups)
            self.player.add(self.game.dead_sprites)
            self.game.gameover = True

class Fire(State):
    def __init__(self, player):
        super().__init__(player)
        self.duration = 60
        self.bonus = 100
        self.manacost = 20
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.player.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            for key, value in self.keyhandler.action_keys.items():
                if keys[value]:
                    self.done[key] = True
                else:
                    self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.player[self.__class__.__name__][self.direction]) - 1:
            self.player.totalhealth = self.player.basehealth + self.bonus
            self.player.buffs[self.__class__.__name__] += self.duration
            self.player.currentmana -= self.manacost
            n = 1 - self.game.player.currentmana/self.game.player.totalmana
            self.game.hud.update(n, "Mana")

class Lightning(State):
    def __init__(self, player):
        super().__init__(player)
        self.duration = 60
        self.bonus = 20
        self.manacost = 20
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.player.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            for key, value in self.keyhandler.action_keys.items():
                if keys[value]:
                    self.done[key] = True
                else:
                    self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.player[self.__class__.__name__][self.direction]):
            self.player.damage = self.player.basedamage + self.bonus
            self.player.buffs[self.__class__.__name__] += self.duration
            self.player.currentmana -= self.manacost
            n = 1 - self.game.player.currentmana/self.game.player.totalmana
            self.game.hud.update(n, "Mana")

class Smoke(State):
    def __init__(self, player):
        super().__init__(player)
        self.duration = 60
        self.bonus = 100
        self.manacost = 20
        self.done = {"Idle": False,
                     "Attack": False,
                     "GetHit": False,
                     "Die": False,
                     "Fire": False,
                     "Lightning": False,
                     "Smoke": False}

    def start_up(self, direction):
        self.current_frame = 0
        self.direction = direction

    def events(self):
        keys = pg.key.get_pressed()
        if self.player.isdead():
            self.done["Die"] = True
        elif self.player.gets_hit():
            self.done["GetHit"] = True
        elif (self.current_frame + 1) % len(self.image_manager.player[self.__class__.__name__][self.direction]) == 0:
            for key, value in self.keyhandler.action_keys.items():
                if keys[value]:
                    self.done[key] = True
                else:
                    self.done["Idle"] = True

    def update(self, dt):
        self.vel = vec(0, 0)
        self.action(self.image_manager.player[self.__class__.__name__], self.direction)
        if self.current_frame == len(self.image_manager.player[self.__class__.__name__][self.direction]):
            self.player.defense = self.player.basedefense + self.bonus
            self.player.buffs[self.__class__.__name__] += self.duration
            self.player.currentmana -= self.manacost
            n = 1 - self.game.player.currentmana/self.game.player.totalmana
            self.game.hud.update(n, "Mana")
