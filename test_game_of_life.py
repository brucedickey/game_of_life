import unittest
import pygame
import numpy as np
from unittest.mock import Mock, patch
from game_of_life import (
    GameConfig, GameState, EventManager, ButtonAction, NextGenerationStrategy,
    PygameAdapter, GameBuilder, Grid, Cells, Button, Game, CompositeGraphic
)

class TestGameConfig(unittest.TestCase):
    def test_singleton(self):
        config1 = GameConfig.get_instance()
        config2 = GameConfig.get_instance()
        self.assertIs(config1, config2)

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.config = GameConfig.get_instance()
        self.game_state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game_state.state.shape, (self.config.n_cells_x, self.config.n_cells_y))

    def test_next_generation(self):
        initial_state = np.copy(self.game_state.state)
        self.game_state.next_generation()
        self.assertNotEqual(np.sum(initial_state), np.sum(self.game_state.state))

class TestEventManager(unittest.TestCase):
    def setUp(self):
        self.event_manager = EventManager()
        self.listener = Mock()

    def test_register_listener(self):
        self.event_manager.register(self.listener)
        self.assertIn(self.listener, self.event_manager.listeners)

    def test_notify_listener(self):
        self.event_manager.register(self.listener)
        event = Mock()
        self.event_manager.notify(event)
        self.listener.update.assert_called_with(event)

class TestButtonAction(unittest.TestCase):
    def setUp(self):
        self.game_state = Mock()
        self.strategy = NextGenerationStrategy(self.game_state)
        self.button_action = ButtonAction(self.strategy)

    def test_update(self):
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (400, 590)
        self.button_action.update(event)
        self.game_state.next_generation.assert_called_once()

class TestPygameAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.screen = pygame.Surface((800, 600))
        self.adapter = PygameAdapter(self.screen)

    def test_draw_button(self):
        self.adapter.draw_button(300, 540, 200, 50)
        # Assertions can be added here if needed to validate the draw_button functionality
        # For now, we just ensure it runs without errors

class TestCompositeGraphic(unittest.TestCase):
    def setUp(self):
        self.composite = CompositeGraphic()
        self.child = Mock()

    def test_add_remove_child(self):
        self.composite.add(self.child)
        self.assertIn(self.child, self.composite.children)
        self.composite.remove(self.child)
        self.assertNotIn(self.child, self.composite.children)

    def test_draw(self):
        self.composite.add(self.child)
        self.composite.draw()
        self.child.draw.assert_called_once()

class TestGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    # Return a Surface object instead of a mock object so that PygameAdapter in the file under test has the actual object.
    @patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600)))
    def setUp(self, mock_set_mode):
        self.builder = GameBuilder()
        self.game = self.builder.build()

    def test_run(self):
        with patch('pygame.event.get', return_value=[Mock(type=pygame.QUIT)]):
            with patch('pygame.display.flip'):
                with patch('pygame.quit'):
                    self.game.run()

if __name__ == '__main__':
    unittest.main()
