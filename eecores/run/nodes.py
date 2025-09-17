
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random

from eecores.core.entities import *
from eecores.core.combat import *
from eecores.run.run_state import RunState, build_enemy_team

def node_event(state:RunState):
    # Returns text outcome
    if state.rng.random()<0.5:
        bp = state.cards["forest_spine_frog"]
        inst = state.get_or_create_card_instance(bp)
        inst.current_dur = max(1, inst.current_dur-1)
        state.deck_blueprints.append(bp)
        return "Vous recrutez une Grenouille Épineuse abîmée."
    else:
        # -1 DUR random alive, gain Lamproie
        alive = [state.get_or_create_card_instance(bp) for bp in state.deck_blueprints if state.get_or_create_card_instance(bp).alive()]
        if alive:
            target = state.rng.choice(alive)
            target.current_dur = max(0, target.current_dur-1)
        state.deck_blueprints.append(state.cards["river_lamprey"])
        return "Vous gagnez Lamproie et blessez une carte aléatoire."

def shop_offer(state:RunState) -> List[CardBlueprint]:
    pool = ["forest_spine_frog","river_lamprey","ruins_curse_gargoyle","neutral_dog","neutral_crab"]
    state.rng.shuffle(pool)
    return [state.cards[cid] for cid in pool[:3]]
