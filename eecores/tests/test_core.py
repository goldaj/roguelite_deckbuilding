
import unittest, random, os
from eecores.core.entities import *
from eecores.core.combat import CombatEngine
from eecores.run.run_state import load_cards

DATA_CARDS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cards.json")

class TestCore(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(1234)
        self.cards = load_cards(DATA_CARDS)

    def test_carapace_converts_hit(self):
        frog = self.cards["forest_spine_frog"].instantiate(self.rng)
        crab = self.cards["neutral_crab"].instantiate(self.rng)  # CARAPACE(1)
        crab.owner = "ENEMY"
        board = Board()
        board.place("PLAYER", frog, "A", 0)
        board.place("ENEMY", crab, "A", 0)
        eng = CombatEngine(self.rng, board, [frog], [crab])
        eng.setup()
        eng.handle_attack(frog)
        self.assertEqual(crab.current_dur, crab.blueprint.dur)
        self.assertEqual(frog.temp_atk_mod, -1)

    def test_burn_end_of_combat(self):
        scorp = self.cards["dunes_ember_scorpion"].instantiate(self.rng)
        turtle = self.cards["river_mud_turtle"].instantiate(self.rng)
        turtle.owner = "ENEMY"
        board = Board()
        board.place("PLAYER", scorp, "A", 0)
        board.place("ENEMY", turtle, "A", 0)
        eng = CombatEngine(self.rng, board, [scorp], [turtle])
        eng.setup()
        eng.handle_attack(scorp)  # applies BRULURE 1
        self.assertEqual(turtle.statuses[ST_BRULURE], 1)
        eng.apply_end_of_combat(turtle)
        self.assertEqual(turtle.current_dur, turtle.blueprint.dur - 1)

    def test_venin_start_tick(self):
        spider = self.cards["forest_azure_spider"].instantiate(self.rng)
        turtle = self.cards["river_mud_turtle"].instantiate(self.rng)
        turtle.owner = "ENEMY"
        board = Board()
        board.place("PLAYER", spider, "A", 0)
        board.place("ENEMY", turtle, "A", 0)
        eng = CombatEngine(self.rng, board, [spider], [turtle])
        turtle.statuses[ST_VENIN] = 2
        eng.setup()
        self.assertEqual(turtle.current_dur, turtle.blueprint.dur - 2)

if __name__ == "__main__":
    unittest.main()
