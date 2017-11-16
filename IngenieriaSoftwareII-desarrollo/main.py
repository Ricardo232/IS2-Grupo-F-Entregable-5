import sys
import pygame as pg
from settings import *
from spritesheet import *
from button import *
from warrior import *
from mobstate import *
from tilemap import *
from hud import *
from line import *
from obstacle import *

class Game(object):
    """
    A single instance of this class is responsible for
    managing which individual game state is active
    and keeping it updated. It also handles many of
    pygame's nuts and bolts (managing the event
    queue, framerate, updating the display, etc.).
    and its run method serves as the "game loop".
    """
    def __init__(self, screen, states, start_state):
        """
        Initialize the Game object.

        screen: the pygame display surface
        states: a dict mapping state-names to GameState objects
        start_state: name of the first active game state
        Game(screen, states, "SPLASH")
        """
        self.done = False
        self.screen = screen
        self.clock = pg.time.Clock()
        self.fps = 60
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.state.startup()

    def events(self):
        """Events are passed for handling to the current state."""
        self.state.events()

    def flip_state(self, state_name):
        """Switch to the next game state."""
        self.state.done[state_name] = False
        self.state_name = state_name
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)

    def update(self, dt):
        """
        Check for state flip and update active state.

        dt: milliseconds since last frame
        """
        if self.state.quit:
            self.done = True
        else:
            for key, value in self.state.done.items():
                if value:
                    self.flip_state(key)
        self.state.update(dt)

    def draw(self):
        """Pass display surface to active state for drawing."""
        self.state.draw(self.screen)

    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """
        while not self.done:
            dt = self.clock.tick(self.fps) / 1000
            self.events()
            self.update(dt)
            self.draw()
            pg.display.update()


class GameState(object):
    """
    Parent class for individual game states to inherit from.
    """
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.persist = {}
        self.spritesheet = SpriteSheet.get_instance()
        self.image_manager = ImageManager.get_instance()

    def startup(self, persistent = {}):
        """
        Called when a state resumes being active.
        Allows information to be passed between states.

        persistent: a dict passed from state to state
        """
        self.persist = persistent

    def events(self, event):
        """
        Handle a single event passed by the Game object.
        """
        pass


    def update(self, dt):
        """
        Update the state. Called by the Game object once
        per frame.

        dt: time since last frame
        """
        pass

    def draw(self, surface):
        """
        Draw everything to the screen.
        """
        pass

class MainScreen(GameState):
    def __init__(self):
        super().__init__()
        self.image_name = "Background.jpg"
        self.image_text_name = "Title.png"
        self.done = {"GAMEPLAY": False,
                     "TUTORIAL": False,
                     "QUIT": False}
        self.load_buttons()

    def load_buttons(self):
        self.buttons = {"GAMEPLAY": Button("Nueva Partida"),
                        "TUTORIAL": Button("Tutorial"),
                        "QUIT": Button("Salir")}
        x = WIDTH / 2
        y = 0.3
        for button in self.buttons.values():
            button.set_pos(x, HEIGHT * y)
            y += 0.25

    def startup(self, persistent = {}):
        self.spritesheet.clear_sprites()
        self.spritesheet.add_sprite(INTRO_FOLDER, self.image_name, True)
        self.spritesheet.add_sprite(INTRO_FOLDER, self.image_text_name)
        self.spritesheet.get_sprite(self.image_text_name[:-4]).set_colorkey(BLACK)
        for button in self.buttons.values():
            button.clicked = False

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

        for key, button in self.buttons.items():
            if button.clicked:
                if key == "QUIT":
                    self.quit = True
                self.done[key] = True

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        for key, button in self.buttons.items():
            button.update(mouse, click)

    def draw(self, screen):
        screen.fill(WHITE)
        screen.blit(self.spritesheet.get_sprite(self.image_name[:-4]), (0, 0))
        screen.blit(self.spritesheet.get_sprite(self.image_text_name[:-4]), (0, 0))
        for key, button in self.buttons.items():
            screen.blit(button.surface, button.rect)

class TutorialScreen(GameState):
    def __init__(self):
        super().__init__()
        self.image_name = "Tutorial.jpg"
        self.done = { "MAINSCREEN": False}
        self.load_button()

    def load_button(self):
        self.button = Button("Regresar")
        x = 0.12
        y = 0.93
        self.button.set_pos(WIDTH * x, HEIGHT * y)


    def startup(self, persistent = {}):
        self.spritesheet.clear_sprites()
        self.spritesheet.add_sprite(INTRO_FOLDER, self.image_name, True)
        self.button.clicked = False

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
        if self.button.clicked:
            self.done["MAINSCREEN"] = True

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        self.button.update(mouse, click)

    def draw(self, screen):
        screen.fill(WHITE)
        screen.blit(self.spritesheet.get_sprite(self.image_name[:-4]), (0, 0))
        screen.blit(self.button.surface, self.button.rect)

class GamePlay(GameState):
    def __init__(self):
        super().__init__()
        self.lines = []
        self.all_sprites = pg.sprite.Group()
        self.rect_sprites = pg.sprite.Group()
        self.mob_sprites = pg.sprite.Group()
        self.dead_sprites = pg.sprite.Group()
        self.hud_sprites = pg.sprite.Group()
        self.sprite_groups = (self.all_sprites, self.rect_sprites, self.mob_sprites, self.dead_sprites, self.hud_sprites)
        self.done = {"MAINSCREEN": False,
                     "GAMEOVER": False}

    def startup(self, persistent):
        screen = pg.display.get_surface()
        generator = self.image_manager.loading_screen(7440, screen)
        self.gameover = False
        for group in self.sprite_groups:
            group.empty()
        self.hud = HUD(self)
        next(generator)
        self.map = TiledMap(path.join(TILEDMAP_FOLDER, "Mapa_Cueva.tmx"))
        self.map_img = self.map.make_map(generator)
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "Line":
                if tile_object.properties["Slope"] == "-1":
                    self.lines.append(Line(tile_object.x, tile_object.y + tile_object.height, tile_object.x + tile_object.width, tile_object.y))
            if tile_object.name == "Player":
                self.player = Warrior(self, tile_object.x, tile_object.y)
            if tile_object.name == "Obstacle":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "Mob":
                Mob(self, tile_object.x, tile_object.y)
            next(generator)

        self.camera = Camera(self.map.width, self.map.height)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

        for sprite in self.all_sprites:
            sprite.events()

        if self.gameover:
            self.done["GAMEOVER"] = True

    def update(self, dt):
        self.all_sprites.update(dt)
        self.camera.update(self.player)

    def draw(self, screen):
        screen.fill(WHITE)
        screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.dead_sprites:
            screen.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health(screen)
            screen.blit(sprite.image, self.camera.apply(sprite))
        self.hud_sprites.draw(screen)
        pg.display.flip()

class GameOver(GameState):
    def __init__(self):
        super().__init__()
        self.image_name = "Game Over.png"
        self.done = {"GAMEPLAY": False}

    def startup(self, persistent = {}):
        self.spritesheet.clear_sprites()
        self.spritesheet.add_sprite(INTRO_FOLDER, self.image_name, True)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.done["GAMEPLAY"] = True
                if event.key == pg.K_ESCAPE:
                    self.quit = True

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(WHITE)
        screen.blit(self.spritesheet.get_sprite(self.image_name[:-4]), (0, 0))
        pg.display.flip()

if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    states = {"MAINSCREEN": MainScreen(),
              "GAMEPLAY": GamePlay(),
              "TUTORIAL": TutorialScreen(),
              "GAMEOVER": GameOver()}
    game = Game(screen, states, "MAINSCREEN")
    game.run()
    pg.quit()
    sys.exit()
