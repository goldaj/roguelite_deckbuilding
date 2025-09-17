from dataclasses import dataclass, field
from typing import List, Optional
from engine.models.card import Unit, CardData

BOARD_COLS = 4

@dataclass
class PlayerState:
    hp: int = 10
    deck: List[CardData] = field(default_factory=list)
    hand: List[CardData] = field(default_factory=list)
    board: List[Optional[Unit]] = field(default_factory=lambda: [None]*BOARD_COLS)

@dataclass
class GameState:
    player: PlayerState = field(default_factory=PlayerState)
    enemy: PlayerState = field(default_factory=PlayerState)
    turn_index: int = 1  # 1-based

    def draw(self, who: PlayerState, n: int = 1):
        for _ in range(n):
            if not who.deck:
                break
            who.hand.append(who.deck.pop())

    def is_over(self) -> bool:
        return self.player.hp <= 0 or self.enemy.hp <= 0

    def winner(self) -> Optional[str]:
        if self.player.hp <= 0 and self.enemy.hp <= 0:
            return "tie"
        if self.player.hp <= 0:
            return "enemy"
        if self.enemy.hp <= 0:
            return "player"
        return None
