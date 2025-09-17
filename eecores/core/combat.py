
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random

from .entities import *

@dataclass
class CombatResult:
    victory: bool
    summary: str
    player_survivors: List[Creature]
    loot_fragments: int = 0
    loot_shield_tokens: int = 0
    loot_egg: int = 0
    loot_gene: int = 0

class CombatEngine:
    def __init__(self, rng: random.Random, board: Board, player_team: List[Creature], enemy_team: List[Creature], max_turns:int=8):
        self.rng = rng
        self.board = board
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.turn = 1
        self.max_turns = max_turns
        self.log: List[str] = []

    def logf(self, msg:str):
        self.log.append(msg)

    def setup(self):
        # Place enemies
        col = 0
        for c in self.enemy_team:
            lane = "A" if col<3 else "B"
            idx = col if col<3 else col-3
            placed = self.board.place("ENEMY", c, lane, idx)
            if not placed:
                for i in range(3):
                    for L in ("A","B"):
                        if self.board.place("ENEMY", c, L, i):
                            placed=True;break
                    if placed: break
            self.apply_start_of_combat(c)
            col += 1
        for c in self.player_team:
            self.apply_start_of_combat(c)

    def apply_start_of_combat(self, cr: Creature):
        ven = cr.statuses.get(ST_VENIN,0)
        if ven>0:
            cr.current_dur -= ven
            self.logf(f"{cr.blueprint.name} subit VENIN {ven} au début du combat (-{ven} DUR).")
        if cr.statuses.get(ST_MALEDICTION,0)>0:
            cr.temp_spd_mod -= 1

    def apply_end_of_combat(self, cr: Creature):
        br = cr.statuses.get(ST_BRULURE,0)
        if br>0:
            cr.current_dur -= br
            self.logf(f"{cr.blueprint.name} subit BRULURE {br} en fin de combat (-{br} DUR).")

    def target_for(self, attacker: Creature) -> Optional[Creature]:
        opp = self.board.opposing(attacker.owner)
        lane, col = attacker.pos or ("A",0)
        front = opp.get(("A",col))
        back = opp.get(("B",col))

        if KW_BOND in attacker.blueprint.keywords:
            choices = [c for (_,c) in self.board.iter_side("ENEMY" if attacker.owner=="PLAYER" else "PLAYER")]
            choices = [c for c in choices if c and c.alive()]
            if choices:
                return min(choices, key=lambda x:x.current_dur)

        if KW_PERCLEE in attacker.blueprint.keywords and front is not None:
            if front.shields>0 and back is not None:
                return back

        if back is not None and front is not None:
            if KW_GARDE in front.blueprint.keywords:
                return front

        return front or back

    def apply_on_attack_effects(self, attacker: Creature, target: Optional[Creature]):
        for tr in attacker.blueprint.triggers:
            if tr.event != "on_attack":
                continue
            if tr.apply and target is not None:
                target.statuses[tr.apply] = target.statuses.get(tr.apply,0) + tr.value
                self.logf(f"{attacker.blueprint.name} applique {tr.apply} {tr.value} à {target.blueprint.name}.")
            if tr.grant_keyword and tr.target=="ALLY_LINE" and attacker.pos:
                mylane, col = attacker.pos
                otherlane = "B" if mylane=="A" else "A"
                slots = self.board.player_slots if attacker.owner=="PLAYER" else self.board.enemy_slots
                ally = slots.get((otherlane,col))
                if ally is not None:
                    kw, val = tr.grant_keyword
                    if kw==KW_BOUCLIER:
                        ally.shields += val
                        self.logf(f"{attacker.blueprint.name} donne BOUCLIER({val}) à {ally.blueprint.name}.")

    def receive_hit(self, target: Creature, raw_dmg:int, attacker: Creature):
        if raw_dmg<=0:
            return
        if target.carapace>0:
            target.carapace -= 1
            attacker.temp_atk_mod -= 1
            self.logf(f"{target.blueprint.name} convertit le coup en -1 ATQ temporaire sur {attacker.blueprint.name} (CARAPACE).")
            return
        if target.shields>0:
            target.shields -= 1
            self.logf(f"{target.blueprint.name} bloque l'impact avec BOUCLIER. (reste {target.shields})")
            return
        target.current_dur -= raw_dmg
        for tr in target.blueprint.triggers:
            if tr.event != "on_hit":
                continue
            if tr.apply and attacker is not None:
                attacker.statuses[tr.apply] = attacker.statuses.get(tr.apply,0) + tr.value
                self.logf(f"{target.blueprint.name} applique {tr.apply} {tr.value} à {attacker.blueprint.name} (on_hit).")

    def handle_attack(self, attacker: Creature):
        if not attacker.alive() or attacker.pos is None:
            return
        target = self.target_for(attacker)
        base_atk = attacker.atk
        if KW_TIRAILLEUR in attacker.blueprint.keywords and target is not None and target.just_deployed:
            base_atk += 1
        if target is not None:
            self.logf(f"{attacker.blueprint.name} attaque {target.blueprint.name} pour {base_atk}.")
            self.receive_hit(target, base_atk, attacker)
            sa = attacker.statuses.get(ST_SAIGNEMENT,0)
            if sa>0:
                attacker.current_dur -= sa
                self.logf(f"{attacker.blueprint.name} perd {sa} (SAIGNEMENT) en attaquant.")
            self.apply_on_attack_effects(attacker, target)

    def cleanup_corpses(self):
        for owner in ("PLAYER","ENEMY"):
            slots = self.board.player_slots if owner=="PLAYER" else self.board.enemy_slots
            for pos, c in list(slots.items()):
                if c is not None and c.current_dur <= 0:
                    self.logf(f"{c.blueprint.name} est détruit.")
                    slots[pos] = None

    def presence(self, owner:str) -> int:
        slots = self.board.player_slots if owner=="PLAYER" else self.board.enemy_slots
        total = 0
        for c in slots.values():
            if c is not None:
                total += max(0, c.current_dur)
        return total

    def run_one_turn(self):
        all_units: List[Creature] = []
        for _,c in self.board.iter_side("PLAYER"):
            all_units.append(c)
        for _,c in self.board.iter_side("ENEMY"):
            all_units.append(c)
        self.rng.shuffle(all_units)
        all_units.sort(key=lambda c: c.spd, reverse=True)
        for u in all_units:
            u.just_deployed = False
        for u in list(all_units):
            if u.alive() and u.pos is not None:
                self.handle_attack(u)
                self.cleanup_corpses()
        self.turn += 1

    def run(self) -> CombatResult:
        self.setup()
        while self.turn <= self.max_turns and self.presence("PLAYER")>0 and self.presence("ENEMY")>0:
            self.run_one_turn()
        for owner in ("PLAYER","ENEMY"):
            for _, c in self.board.iter_side(owner):
                self.apply_end_of_combat(c)
        self.cleanup_corpses()
        victory = self.presence("ENEMY")==0 and self.presence("PLAYER")>0
        survivors = [c.copy_persistent() for _,c in self.board.iter_side("PLAYER")]
        loot_frag = 12 if victory else 4
        loot_gene = 1 if victory and self.rng.random()<0.25 else 0
        loot_shield = 1 if victory and self.rng.random()<0.30 else 0
        loot_egg = 1 if victory and self.rng.random()<0.20 else 0
        summary = "\n".join(self.log)
        return CombatResult(victory, summary, survivors, loot_frag, loot_shield, loot_egg, loot_gene)
