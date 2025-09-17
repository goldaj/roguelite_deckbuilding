from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Trigger:
    event: str
    apply: str
    value: int
    target: str

@dataclass
class CardData:
    id: str
    name: str
    biome: str
    rarity: str
    cost: int
    atk: int
    dur: int
    spd: int
    keywords: List[str] = field(default_factory=list)
    keyword_values: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Trigger] = field(default_factory=list)
    notes: str = ""

@dataclass
class Unit:
    data: CardData
    current_dur: int
    atk_bonus: int = 0
    spd_bonus: int = 0
    dur_bonus: int = 0

    @property
    def alive(self) -> bool:
        return self.current_dur > 0

    @property
    def atk(self) -> int:
        return max(0, self.data.atk + self.atk_bonus)

    @property
    def spd(self) -> int:
        return max(0, self.data.spd + self.spd_bonus)

    def take_damage(self, amount: int):
        self.current_dur = max(0, self.current_dur - amount)
