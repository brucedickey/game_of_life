'''
'Mathematicians Prove the "Omniperiodicity" of Conway's Game of Life':
https://www.msn.com/en-us/news/technology/mathematicians-prove-the-omniperiodicity-of-conway-s-game-of-life/ar-AA1lrFgu?rc=1&ocid=winp1taskbar&cvid=0e7f5d7057bd4578bc8931ebdc11fe83&ei=13
'''
import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Singleton pattern for the Game configuration
class GameConfig:
    _instance = None

    @staticmethod
    def get_instance():
        if GameConfig._instance is None:
            GameConfig()
        return GameConfig._instance

    def __init__(self):
        if GameConfig._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.width = 800
            self.height = 600
            self.n_cells_x = 40
            self.n_cells_y = 30
            self.cell_width = self.width // self.n_cells_x
            self.cell_height = self.height // self.n_cells_y
            GameConfig._instance = self

config = GameConfig.get_instance()

# State pattern for the game state
class GameState:
    def __init__(self):
        self.state = np.random.choice([0, 1], size=(config.n_cells_x, config.n_cells_y), p=[0.8, 0.2])

    def next_generation(self):
        new_state = np.copy(self.state)
        for y in range(config.n_cells_y):
            for x in range(config.n_cells_x):
                n_neighbors = self._count_neighbors(x, y)
                if self.state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                    new_state[x, y] = 0
                elif self.state[x, y] == 0 and n_neighbors == 3:
                    new_state[x, y] = 1
        self.state = new_state

    def _count_neighbors(self, x, y):
        return sum([self.state[(x + i) % config.n_cells_x, (y + j) % config.n_cells_y]
                    for i in [-1, 0, 1] for j in [-1, 0, 1] if not (i == 0 and j == 0)])

# Observer pattern for handling button events
class EventManager:
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def notify(self, event):
        for listener in self.listeners:
            listener.update(event)

class Listener:
    def update(self, event):
        raise NotImplementedError

# Strategy pattern for different button actions
class ButtonAction(Listener):
    def __init__(self, strategy):
        self.strategy = strategy

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                self.strategy.execute()

class NextGenerationStrategy:
    def __init__(self, game_state):
        self.game_state = game_state

    def execute(self):
        self.game_state.next_generation()

# Adapter pattern for drawing
class PygameAdapter:
    def __init__(self, screen):
        self.screen = screen

    def draw_button(self, button_x, button_y, button_width, button_height):
        pygame.draw.rect(self.screen, green, (button_x, button_y, button_width, button_height))
        font = pygame.font.Font(None, 36)
        text = font.render("Next Generation", True, black)
        text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        self.screen.blit(text, text_rect)

    def draw_grid(self, cell_width, cell_height, width, height):
        for y in range(0, height, cell_height):
            for x in range(0, width, cell_width):
                cell = pygame.Rect(x, y, cell_width, cell_height)
                pygame.draw.rect(self.screen, gray, cell, 1)

    def draw_cells(self, game_state, cell_width, cell_height):
        for y in range(config.n_cells_y):
            for x in range(config.n_cells_x):
                cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
                if game_state[x, y] == 1:
                    pygame.draw.rect(self.screen, black, cell)

# Composite pattern for graphical components
class GraphicComponent:
    def draw(self):
        raise NotImplementedError

class CompositeGraphic(GraphicComponent):
    def __init__(self):
        self.children = []

    def add(self, component):
        self.children.append(component)

    def remove(self, component):
        self.children.remove(component)

    def draw(self):
        for child in self.children:
            child.draw()

class Grid(GraphicComponent):
    def __init__(self, adapter):
        self.adapter = adapter

    def draw(self):
        self.adapter.draw_grid(config.cell_width, config.cell_height, config.width, config.height)

class Cells(GraphicComponent):
    def __init__(self, adapter, game_state):
        self.adapter = adapter
        self.game_state = game_state

    def draw(self):
        self.adapter.draw_cells(self.game_state.state, config.cell_width, config.cell_height)

class Button(GraphicComponent):
    def __init__(self, adapter):
        self.adapter = adapter

    def draw(self):
        self.adapter.draw_button(button_x, button_y, button_width, button_height)

# Builder pattern for constructing the game
class GameBuilder:
    def __init__(self):
        self.config = GameConfig.get_instance()
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        self.font = pygame.font.Font(None, 36)
        self.game_state = GameState()
        self.event_manager = EventManager()
        self.graphic = CompositeGraphic()

    def build(self):
        adapter = PygameAdapter(self.screen)
        next_gen_strategy = NextGenerationStrategy(self.game_state)
        button_action = ButtonAction(next_gen_strategy)
        self.event_manager.register(button_action)

        grid = Grid(adapter)
        cells = Cells(adapter, self.game_state)
        button = Button(adapter)

        self.graphic.add(grid)
        self.graphic.add(cells)
        self.graphic.add(button)

        return Game(self.graphic, self.event_manager, self.screen)

# Game class to encapsulate the main game loop
class Game:
    def __init__(self, graphic, event_manager, screen):
        self.graphic = graphic
        self.event_manager = event_manager
        self.screen = screen

    def run(self):
        running = True
        while running:
            self.screen.fill(white)
            self.graphic.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.event_manager.notify(event)

        pygame.quit()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

# Button dimensions
button_width, button_height = 200, 50
button_x, button_y = (config.width - button_width) // 2, config.height - button_height - 10

# Create and run the game
game_builder = GameBuilder()
game = game_builder.build()
game.run()