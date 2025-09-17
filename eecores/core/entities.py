
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

import random

# Keywords
KW_BOUCLIER = "BOUCLIER"
KW_PERCLEE = "PERCEE"   # Percée
KW_BOND = "BOND"
KW_TIRAILLEUR = "TIRAILLEUR"
KW_GARDE = "GARDE"
KW_CARAPACE = "CARAPACE"
KW_ETHERE = "ETHERE"
KW_VOL = "VOL"

# Status (persistent across the run)
ST_VENIN = "VENIN"
ST_BRULURE = "BRULURE"
ST_SAIGNEMENT = "SAIGNEMENT"
ST_FRACTURE = "FRACTURE"
ST_MALEDICTION = "MALEDICTION"
ST_EROSION = "EROSION"

LANE_FRONT = "A"  # Avant
LANE_BACK = "B"   # Arrière

StatusList = [ST_VENIN, ST_BRULURE, ST_SAIGNEMENT, ST_FRACTURE, ST_MALEDICTION, ST_EROSION]

@dataclass
class Trigger:
    event: str  # "on_attack", "on_hit", "on_deploy", "on_kill", "start_combat", "end_combat"
    apply: Optional[str] = None   # status key
    value: int = 0
    target: str = "ENEMY"         # "ALLY", "SELF", "ALLY_LINE", etc.
    grant_keyword: Optional[Tuple[str,int]] = None  # e.g., ("BOUCLIER", 1)
    note: str = ""

@dataclass
class CardBlueprint:
    id: str
    name: str
    biome: str
    rarity: str
    cost: int
    atk: int
    dur: int
    spd: int
    keywords: List[str] = field(default_factory=list)
    keyword_values: Dict[str,int] = field(default_factory=dict)  # e.g. {"BOUCLIER": 1, "CARAPACE": 1}
    triggers: List[Trigger] = field(default_factory=list)
    notes: str = ""

    def instantiate(self, rng: random.Random) -> "Creature":
        shields = self.keyword_values.get(KW_BOUCLIER, 0)
        carapace = self.keyword_values.get(KW_CARAPACE, 0)
        return Creature(
            blueprint=self,
            current_atk=self.atk,
            current_dur=self.dur,
            base_spd=self.spd,
            shields=shields,
            carapace=carapace,
            statuses={k:0 for k in StatusList},
        )

@dataclass
class Creature:
    blueprint: CardBlueprint
    current_atk: int
    current_dur: int
    base_spd: int
    shields: int = 0
    carapace: int = 0
    statuses: Dict[str,int] = field(default_factory=dict)
    temp_atk_mod: int = 0     # resets each combat
    temp_spd_mod: int = 0     # resets each combat (malédiction)
    owner: str = "PLAYER"     # "PLAYER" or "ENEMY"
    pos: Optional[Tuple[str,int]] = None  # ("A"/"B", col 0..2)
    just_deployed: bool = False

    def alive(self) -> bool:
        return self.current_dur > 0

    @property
    def atk(self) -> int:
        return max(0, self.current_atk + self.temp_atk_mod - self.statuses.get(ST_FRACTURE,0))

    @property
    def spd(self) -> int:
        return max(1, self.base_spd + self.temp_spd_mod)

    def copy_persistent(self) -> "Creature":
        return Creature(
            blueprint=self.blueprint,
            current_atk=self.current_atk,
            current_dur=self.current_dur,
            base_spd=self.base_spd,
            shields=self.shields,
            carapace=self.carapace,
            statuses=self.statuses.copy(),
            temp_atk_mod=0,
            temp_spd_mod=0,
            owner=self.owner,
            pos=None,
            just_deployed=False,
        )

    def describe_short(self) -> str:
        kwords = []
        for k in self.blueprint.keywords:
            if k in (KW_BOUCLIER, KW_CARAPACE):
                v = (self.shields if k==KW_BOUCLIER else self.carapace)
                if v>0:
                    kwords.append(f"{k}({v})")
            else:
                kwords.append(k)
        if self.statuses.get(ST_FRACTURE,0):
            kwords.append(f"FRACTURE({self.statuses[ST_FRACTURE]})")
        for st in (ST_VENIN, ST_BRULURE, ST_SAIGNEMENT, ST_MALEDICTION, ST_EROSION):
            v = self.statuses.get(st,0)
            if v>0:
                kwords.append(f"{st}({v})")
        kw = ",".join(kwords) if kwords else "-"
        return f"{self.blueprint.name} {self.atk}/{self.current_dur}/V{self.spd} [{kw}]"

@dataclass
class Deck:
    cards: List[CardBlueprint]

    def draw_hand(self, rng: random.Random, state: "RunState", size:int=5) -> List[Creature]:
        pool = []
        for bp in self.cards:
            inst = state.get_or_create_card_instance(bp)
            if inst.alive():
                pool.append(inst)
        rng.shuffle(pool)
        hand = pool[:size]
        return [c.copy_persistent() for c in hand]

@dataclass
class Board:
    player_slots: Dict[Tuple[str,int], Optional[Creature]] = field(default_factory=lambda: {("A",i):None for i in range(3)} | {("B",i):None for i in range(3)})
    enemy_slots: Dict[Tuple[str,int], Optional[Creature]] = field(default_factory=lambda: {("A",i):None for i in range(3)} | {("B",i):None for i in range(3)})

    def place(self, owner: str, creature: Creature, lane: str, col: int) -> bool:
        slots = self.player_slots if owner=="PLAYER" else self.enemy_slots
        key = (lane, col)
        if key in slots and slots[key] is None:
            slots[key] = creature
            creature.owner = owner
            creature.pos = (lane, col)
            creature.just_deployed = True
            return True
        return False

    def remove(self, owner:str, lane:str, col:int) -> Optional[Creature]:
        slots = self.player_slots if owner=="PLAYER" else self.enemy_slots
        key = (lane,col)
        c = slots.get(key)
        slots[key] = None
        return c

    def iter_side(self, owner: str):
        slots = self.player_slots if owner=="PLAYER" else self.enemy_slots
        for pos, c in slots.items():
            if c is not None:
                yield pos, c

    def opposing(self, owner:str) -> Dict[Tuple[str,int], Optional[Creature]]:
        return self.enemy_slots if owner=="PLAYER" else self.player_slots
