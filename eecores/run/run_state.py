
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random, json, os

from eecores.core.entities import *
from eecores.core.combat import CombatEngine, CombatResult

def load_cards(path:str) -> Dict[str, CardBlueprint]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    bps: Dict[str, CardBlueprint] = {}
    for item in raw["cards"]:
        trig = []
        for t in item.get("triggers", []):
            trig.append(Trigger(
                event=t.get("event",""),
                apply=t.get("apply"),
                value=int(t.get("value",0)),
                target=t.get("target","ENEMY"),
                grant_keyword=tuple(t.get("grant_keyword")) if t.get("grant_keyword") else None,
                note=t.get("note","")
            ))
        bp = CardBlueprint(
            id=item["id"],
            name=item["name"],
            biome=item.get("biome","NEUTRE"),
            rarity=item.get("rarity","C"),
            cost=int(item.get("cost",1)),
            atk=int(item.get("atk",1)),
            dur=int(item.get("dur",1)),
            spd=int(item.get("spd",2)),
            keywords=item.get("keywords",[]),
            keyword_values=item.get("keyword_values",{}),
            triggers=trig,
            notes=item.get("notes",""),
        )
        bps[bp.id] = bp
    return bps

@dataclass
class RunState:
    rng: random.Random
    cards: Dict[str, CardBlueprint]
    deck_blueprints: List[CardBlueprint]
    card_instances: Dict[str, Creature] = field(default_factory=dict)
    fragments: int = 0
    eggs: List[int] = field(default_factory=list)
    genes: int = 0
    act: int = 1
    destroyed_ids: List[str] = field(default_factory=list)

    def get_or_create_card_instance(self, bp: CardBlueprint) -> Creature:
        if bp.id not in self.card_instances:
            inst = bp.instantiate(self.rng)
            self.card_instances[bp.id] = inst
        return self.card_instances[bp.id]

    def draw_hand(self, size:int=5) -> List[Creature]:
        return Deck(cards=self.deck_blueprints).draw_hand(self.rng, self, size=size)

    def persist_post_combat(self, survivors: List[Creature]):
        ids_survived = set()
        for c in survivors:
            ids_survived.add(c.blueprint.id)
            self.card_instances[c.blueprint.id] = c.copy_persistent()
        # Non jouées
        for bp in self.deck_blueprints:
            if bp.id not in self.card_instances:
                self.card_instances[bp.id] = bp.instantiate(self.rng)
        # Retirer détruites
        to_remove = []
        for bp in list(self.deck_blueprints):
            inst = self.card_instances.get(bp.id)
            if inst is None or inst.current_dur <= 0:
                to_remove.append(bp)
        for bp in to_remove:
            self.deck_blueprints.remove(bp)
            self.destroyed_ids.append(bp.id)

    def apply_erosion(self):
        for inst in self.card_instances.values():
            er = inst.statuses.get(ST_EROSION,0)
            if er>0 and inst.current_dur>0:
                inst.current_dur -= 1

    def hatch_eggs(self):
        new_cards = []
        for i in range(len(self.eggs)):
            self.eggs[i] -= 1
        hatched = sum(1 for e in self.eggs if e<=0)
        self.eggs = [e for e in self.eggs if e>0]
        for _ in range(hatched):
            bp = self.cards["neutral_jeune"]
            self.deck_blueprints.append(bp)
            new_cards.append(bp.name)
        return new_cards

    def grant_shield_to_random(self, amount:int=1):
        candidates = [self.get_or_create_card_instance(bp) for bp in self.deck_blueprints if self.get_or_create_card_instance(bp).alive()]
        if not candidates:
            return None
        c = self.rng.choice(candidates)
        c.shields += amount
        return c.blueprint.name

def build_enemy_team(rng: random.Random, cards: Dict[str, CardBlueprint], difficulty:int=1) -> List[Creature]:
    pool_ids = [
        "forest_spine_frog","forest_azure_spider","dunes_ember_scorpion","cliffs_echo_bat",
        "river_mud_turtle","ruins_curse_gargoyle","neutral_dog","neutral_crab"
    ]
    rng.shuffle(pool_ids)
    team = []
    for cid in pool_ids[:min(4, len(pool_ids))]:
        c = cards[cid].instantiate(rng)
        c.owner = "ENEMY"
        c.current_atk += max(0,difficulty-1)
        c.current_dur += difficulty
        team.append(c)
    return team
