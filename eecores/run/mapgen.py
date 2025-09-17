
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal
import random

NodeType = Literal["COMBAT","ELITE","EVENT","MARCHAND","ALCHIMIE","SANCTUAIRE","BOSS"]

@dataclass
class MapNode:
    node_type: NodeType
    label: str

@dataclass
class ActMap:
    nodes: List[MapNode]

def generate_act(rng: random.Random, act_index:int) -> ActMap:
    choices = ["COMBAT","COMBAT","EVENT","MARCHAND","ALCHIMIE","SANCTUAIRE"]
    rng.shuffle(choices)
    seq = []
    for i in range(4):
        t = rng.choice(choices)
        seq.append(MapNode(t, f"{t.title()} {i+1}"))
    idx = rng.randrange(4)
    seq[idx] = MapNode("ELITE", f"ELITE {idx+1}")
    seq.append(MapNode("BOSS", f"Boss de l'Acte {act_index}"))
    return ActMap(seq)
