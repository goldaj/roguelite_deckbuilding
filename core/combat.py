# core/combat.py
"""Système de combat avec altérations permanentes"""

from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import random
from copy import deepcopy

from entities import (
    Card, CombatState, StatusEffect, Keyword,
    Biome, Rarity
)


class TargetingRule(Enum):
    FRONT = auto()  # Cible la ligne avant
    BACK = auto()  # Cible la ligne arrière
    WEAKEST = auto()  # Bond - cible la plus faible
    STRONGEST = auto()  # Cible la plus forte
    PIERCE = auto()  # Percée - traverse les boucliers


class CombatAction:
    """Représente une action de combat"""

    def __init__(self, action_type: str, **kwargs):
        self.type = action_type
        self.params = kwargs

    def execute(self, combat: 'CombatResolver', source: Optional[Card] = None):
        """Exécute l'action dans le contexte du combat"""
        method = getattr(combat, f'action_{self.type}', None)
        if method:
            method(source, **self.params)


class CombatResolver:
    """Moteur de résolution de combat"""

    def __init__(self, state: CombatState, rng_seed: Optional[int] = None):
        self.state = state
        self.rng = random.Random(rng_seed)
        self.action_log: List[str] = []
        self.animation_queue: List[Dict] = []

    def start_combat(self):
        """Initialise le combat - applique les effets de début"""
        self.log("=== Début du combat ===")

        # Appliquer les effets de début de combat sur toutes les cartes
        for card in self._all_cards():
            if card:
                # Venin tick au début
                if StatusEffect.VENIN in card.permanent_statuses:
                    damage = card.permanent_statuses[StatusEffect.VENIN]
                    self.log(f"{card.name} subit {damage} dégâts de Venin")
                    card.take_damage(damage)

                # Malédiction réduit la vitesse
                if StatusEffect.MALEDICTION in card.permanent_statuses:
                    card.current_spd = max(1, card.current_spd - 1)
                    self.log(f"{card.name} est ralenti par Malédiction")

        # Mélanger le deck et piocher la main
        self.rng.shuffle(self.state.deck)
        self.draw_cards(5)

        # Appliquer les modificateurs de terrain
        self._apply_terrain_modifiers()

    def process_turn(self):
        """Traite un tour complet de combat"""
        self.state.turn += 1
        self.log(f"\n--- Tour {self.state.turn} ---")

        # Réinitialiser l'énergie
        self.state.energy = 3

        # Phase d'initiative - résoudre par vitesse décroissante
        units = self._get_units_by_speed()

        for unit, is_player, position in units:
            if unit and unit.current_dur > 0:
                self._unit_attack(unit, is_player, position)

        # Vérifier la fin du combat
        if self.state.is_combat_over() is not None:
            self.end_combat()

    def _unit_attack(self, attacker: Card, is_player: bool, position: int):
        """Une unité effectue son attaque"""
        # Déterminer la cible
        target, target_pos = self._find_target(attacker, is_player, position)

        if not target:
            return

        # Calculer les dégâts
        damage = attacker.get_effective_atk()

        # Appliquer Saignement si l'attaquant en a
        if StatusEffect.SAIGNEMENT in attacker.permanent_statuses:
            bleed = attacker.permanent_statuses[StatusEffect.SAIGNEMENT]
            attacker.take_damage(bleed)
            self.log(f"{attacker.name} saigne et perd {bleed} DUR")

        # Résoudre l'attaque
        self._resolve_attack(attacker, target, damage)

        # Effets "on_attack"
        for effect_data in attacker.on_attack:
            self._apply_effect(effect_data, attacker, target)

    def _find_target(self, attacker: Card, is_player: bool, position: int) -> Tuple[Optional[Card], int]:
        """Trouve la cible appropriée selon les règles"""
        enemy_field = self.state.enemy_field if is_player else self.state.player_field

        # Gestion du Bond
        if Keyword.BOND in attacker.keywords:
            # Cible la créature avec le moins de DUR
            weakest = None
            weakest_pos = -1
            for i, card in enumerate(enemy_field):
                if card and (not weakest or card.current_dur < weakest.current_dur):
                    weakest = card
                    weakest_pos = i
            return weakest, weakest_pos

        # Gestion de Percée
        if Keyword.PERCEE in attacker.keywords:
            # Peut frapper l'arrière si l'avant a des boucliers
            front = enemy_field[position % 3]  # Position correspondante en face
            if front and front.shields > 0:
                # Chercher derrière
                back_pos = (position % 3) + 3
                if back_pos < 6 and enemy_field[back_pos]:
                    return enemy_field[back_pos], back_pos

        # Ciblage standard - la créature en face
        if position < 3:  # Ligne avant
            # Cherche en face sur la ligne avant ennemie
            for i in range(3):
                target_pos = i
                if enemy_field[target_pos]:
                    return enemy_field[target_pos], target_pos
        else:  # Ligne arrière
            # Cherche d'abord ligne arrière, puis avant
            for i in range(3, 6):
                if enemy_field[i]:
                    return enemy_field[i], i
            for i in range(3):
                if enemy_field[i]:
                    return enemy_field[i], i

        # Cible par défaut - première créature trouvée
        for i, card in enumerate(enemy_field):
            if card:
                return card, i

        return None, -1

    def _resolve_attack(self, attacker: Card, target: Card, damage: int):
        """Résout une attaque avec gestion des boucliers et effets"""
        self.log(f"{attacker.name} attaque {target.name} pour {damage} dégâts")

        # Gestion de Garde
        if Keyword.GARDE in target.keywords:
            # Intercepte l'attaque destinée à l'arrière
            pass  # Déjà géré dans find_target

        # Gestion de Carapace
        if Keyword.CARAPACE in target.keywords and target.shields > 0:
            # Convertit le coup en réduction d'ATQ temporaire
            attacker.current_atk = max(1, attacker.current_atk - 1)
            target.shields -= 1
            self.log(f"{target.name} active Carapace, {attacker.name} perd 1 ATQ")
            return

        # Application des dégâts
        if target.shields > 0:
            target.shields -= 1
            self.log(f"{target.name} bloque avec un bouclier")
        else:
            survived = target.take_damage(damage)
            self.log(f"{target.name} subit {damage} dégâts (DUR: {target.current_dur})")

            if not survived:
                self._on_creature_death(target, attacker)

        # Effets "on_hit" de l'attaquant
        for effect_data in attacker.on_hit:
            self._apply_effect(effect_data, attacker, target)

    def _apply_effect(self, effect_data: Dict, source: Card, target: Card):
        """Applique un effet de carte"""
        effect_type = effect_data.get('effect')
        value = effect_data.get('value', 1)

        if isinstance(effect_type, StatusEffect):
            target.apply_status(effect_type, value)
            self.log(f"{source.name} applique {effect_type.value} {value} à {target.name}")

        # Autres effets spéciaux
        if effect_data.get('type') == 'shield':
            target.shields += value
            self.log(f"{target.name} gagne {value} Bouclier(s)")

    def play_card(self, card: Card, position: int) -> bool:
        """Joue une carte depuis la main"""
        if card.cost > self.state.energy:
            return False

        if position < 0 or position >= 6:
            return False

        if self.state.player_field[position] is not None:
            return False

        # Déployer la carte
        self.state.player_field[position] = card
        self.state.energy -= card.cost
        self.state.hand.remove(card)

        self.log(f"Déploiement: {card.name} en position {position}")

        # Effets "on_deploy"
        for effect_data in card.on_deploy:
            self._apply_on_deploy_effect(effect_data, card)

        # Gestion de Tirailleur - bonus contre les nouvelles invocations
        for enemy in self.state.enemy_field:
            if enemy and Keyword.TIRAILLEUR in enemy.keywords:
                # +1 ATQ temporaire ce tour contre cette invocation
                pass

        return True

    def _apply_on_deploy_effect(self, effect_data: Dict, source: Card):
        """Applique les effets de déploiement"""
        effect_type = effect_data.get('type')

        if effect_type == 'shield_ally':
            # Donne bouclier à un allié
            target_pos = effect_data.get('target', 'back')
            if target_pos == 'back':
                # Cherche un allié sur la ligne arrière
                for i in range(3, 6):
                    if self.state.player_field[i]:
                        self.state.player_field[i].shields += effect_data.get('value', 1)
                        break

        elif effect_type == 'buff_allies':
            # Buff tous les alliés
            for ally in self.state.player_field:
                if ally and ally != source:
                    ally.current_atk += effect_data.get('atk', 0)

    def _on_creature_death(self, creature: Card, killer: Optional[Card] = None):
        """Gère la mort d'une créature"""
        self.log(f"{creature.name} est détruit!")

        # Effets "on_death"
        for effect_data in creature.on_death:
            if killer:
                self._apply_effect(effect_data, creature, killer)

        # Retirer du terrain
        for i, card in enumerate(self.state.player_field):
            if card == creature:
                self.state.player_field[i] = None
                return

        for i, card in enumerate(self.state.enemy_field):
            if card == creature:
                self.state.enemy_field[i] = None
                return

    def end_combat(self):
        """Termine le combat et applique les effets de fin"""
        self.log("\n=== Fin du combat ===")

        # Appliquer Brûlure sur toutes les créatures
        for card in self._all_cards():
            if card and StatusEffect.BRULURE in card.permanent_statuses:
                damage = card.permanent_statuses[StatusEffect.BRULURE]
                self.log(f"{card.name} brûle pour {damage} dégâts")
                card.take_damage(damage)

        # Calculer les récompenses
        victory = self.state.is_combat_over()
        if victory:
            self.log("VICTOIRE!")
            return self._calculate_rewards()
        else:
            self.log("DÉFAITE...")
            return {}

    def _calculate_rewards(self) -> Dict:
        """Calcule les récompenses de victoire"""
        rewards = {
            'fragments': self.rng.randint(10, 30),
            'cards': [],
            'eggs': 0,
            'genes': 0
        }

        # Chance de drop de carte
        if self.rng.random() < 0.3:
            rewards['cards'].append(self._generate_reward_card())

        # Chance d'oeuf
        if self.rng.random() < 0.1:
            rewards['eggs'] = 1

        return rewards

    def _generate_reward_card(self) -> str:
        """Génère une carte comme récompense"""
        # Logique pour générer une carte appropriée au biome/acte
        return "forest_spine_frog"  # Placeholder

    def draw_cards(self, count: int):
        """Pioche des cartes du deck vers la main"""
        for _ in range(count):
            if self.state.deck and len(self.state.hand) < 10:
                card = self.state.deck.pop(0)
                self.state.hand.append(card)
                self.log(f"Pioche: {card.name}")
            elif self.state.discard:
                # Remélanger la défausse
                self.state.deck = self.state.discard[:]
                self.state.discard = []
                self.rng.shuffle(self.state.deck)
                if self.state.deck:
                    card = self.state.deck.pop(0)
                    self.state.hand.append(card)

    def _get_units_by_speed(self) -> List[Tuple[Card, bool, int]]:
        """Retourne toutes les unités triées par vitesse décroissante"""
        units = []

        # Ajouter les unités du joueur
        for i, card in enumerate(self.state.player_field):
            if card:
                units.append((card, True, i))

        # Ajouter les unités ennemies
        for i, card in enumerate(self.state.enemy_field):
            if card:
                units.append((card, False, i))

        # Trier par vitesse décroissante (en cas d'égalité, ordre aléatoire)
        units.sort(key=lambda x: (x[0].current_spd, self.rng.random()), reverse=True)

        return units

    def _all_cards(self) -> List[Card]:
        """Retourne toutes les cartes sur le terrain"""
        cards = []
        for card in self.state.player_field + self.state.enemy_field:
            if card:
                cards.append(card)
        return cards

    def _apply_terrain_modifiers(self):
        """Applique les modificateurs de terrain"""
        terrain = self.state.terrain_modifiers.get('type')

        if terrain == 'LAVE':
            # Les créatures non-volantes en ligne avant subissent Brûlure
            for i in range(3):
                if self.state.player_field[i] and Keyword.VOL not in self.state.player_field[i].keywords:
                    self.state.player_field[i].apply_status(StatusEffect.BRULURE, 1)
                if self.state.enemy_field[i] and Keyword.VOL not in self.state.enemy_field[i].keywords:
                    self.state.enemy_field[i].apply_status(StatusEffect.BRULURE, 1)

        elif terrain == 'BROUILLARD':
            # -1 Vitesse pour les créatures à distance
            for i in range(3, 6):
                if self.state.player_field[i]:
                    self.state.player_field[i].current_spd = max(1, self.state.player_field[i].current_spd - 1)
                if self.state.enemy_field[i]:
                    self.state.enemy_field[i].current_spd = max(1, self.state.enemy_field[i].current_spd - 1)

    def log(self, message: str):
        """Ajoute un message au journal de combat"""
        self.action_log.append(message)

    def add_animation(self, anim_type: str, **params):
        """Ajoute une animation à la queue"""
        self.animation_queue.append({
            'type': anim_type,
            'params': params
        })