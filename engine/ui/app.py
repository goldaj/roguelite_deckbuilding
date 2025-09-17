import os, random
from engine.core.loader import load_all_cards, make_player_deck, pick_enemy_cards
from engine.core.state import GameState, PlayerState, BOARD_COLS
from engine.models.card import Unit
from engine.ui.menu import MainMenuUI
from engine.ui.game import GameUI
from engine.ui.victory import VictoryUI

MAX_COMBATS = 10

class App:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.cards = load_all_cards(os.path.join(base_dir, 'assets', 'cards.json'))

    def start(self):
        while True:
            # Main Menu
            menu = MainMenuUI()
            action = menu.run()
            if action != 'start':
                break

            # New run
            stage = 1
            while stage <= MAX_COMBATS:
                is_boss = (stage == MAX_COMBATS)
                gs = self._build_stage(stage, is_boss)
                ui = GameUI(gs, stage, is_boss)
                outcome = ui.run()
                if outcome == 'quit' or outcome == 'loss':
                    # back to menu on quit or defeat
                    break
                # outcome == 'win'
                stage += 1

            # Victory screen if boss cleared
            if stage > MAX_COMBATS:
                victory = VictoryUI(is_boss=True)
                act = victory.run()
                # regardless of act, loop returns to menu

    def _build_stage(self, stage: int, is_boss: bool) -> GameState:
        # Player setup
        player_deck = make_player_deck(self.cards, 10)
        random.shuffle(player_deck)

        gs = GameState()
        gs.player.deck = player_deck
        gs.player.hp = 10
        gs.enemy.hp = 10 + (stage-1)*2 + (10 if is_boss else 0)  # scale enemy HP, boss +10
        gs.draw(gs.player, 5)

        # Enemy board with scaling: small atk bonus per stage, extra for boss
        atk_bonus = (stage-1)//2  # +1 atk every 2 stages
        if is_boss:
            atk_bonus += 2
        enemy_cards = pick_enemy_cards(self.cards, BOARD_COLS)
        for i, c in enumerate(enemy_cards):
            unit = Unit(c, c.dur, atk_bonus=atk_bonus)
            gs.enemy.board[i] = unit
        return gs
