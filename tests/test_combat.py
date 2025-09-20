# tests/test_combat.py
"""Tests pour le système de combat"""

import pytest
from unittest.mock import Mock, patch
import random

from bestiaire.core.entities import Card, CombatState, StatusEffect, Keyword, Biome, Rarity
from core.combat import CombatResolver, TargetingRule


class TestCombatResolver:
    """Tests pour le résolveur de combat"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.state = CombatState()
        self.resolver = CombatResolver(self.state, rng_seed=42)

    def test_start_combat_applies_venin(self):
        """Test que le Venin s'applique au début du combat"""
        card = Card("test", "Test", Biome.FORET, Rarity.COMMON, 1, 2, 5, 1)
        card.apply_status(StatusEffect.VENIN, 2)
        self.state.player_field[0] = card

        self.resolver.start_combat()

        assert card.current_dur == 3  # 5 - 2 de Venin

    def test_end_combat_applies_brulure(self):
        """Test que la Brûlure s'applique en fin de combat"""
        card = Card("test", "Test", Biome.FORET, Rarity.COMMON, 1, 2, 5, 1)
        card.apply_status(StatusEffect.BRULURE, 3)
        self.state.player_field[0] = card

        self.resolver.end_combat()

        assert card.current_dur == 2  # 5 - 3 de Brûlure

    def test_targeting_bond(self):
        """Test du ciblage avec Bond"""
        attacker = Card("attacker", "Attacker", Biome.FORET, Rarity.COMMON, 1, 3, 4, 2)
        attacker.keywords.add(Keyword.BOND)

        enemy1 = Card("enemy1", "Enemy 1", Biome.FORET, Rarity.COMMON, 1, 2, 5, 1)
        enemy2 = Card("enemy2", "Enemy 2", Biome.FORET, Rarity.COMMON, 1, 2, 3, 1)
        enemy3 = Card("enemy3", "Enemy 3", Biome.FORET, Rarity.COMMON, 1, 2, 7, 1)

        self.state.enemy_field[0] = enemy1
        self.state.enemy_field[1] = enemy2
        self.state.enemy_field[2] = enemy3

        target, pos = self.resolver._find_target(attacker, True, 0)

        assert target == enemy2  # Cible avec le moins de DUR
        assert pos == 1

    def test_targeting_percee_through_shields(self):
        """Test de Percée qui traverse les boucliers"""
        attacker = Card("attacker", "Attacker", Biome.FORET, Rarity.COMMON, 1, 3, 4, 2)
        attacker.keywords.add(Keyword.PERCEE)

        front_enemy = Card("front", "Front", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)
        front_enemy.shields = 1
        back_enemy = Card("back", "Back", Biome.FORET, Rarity.COMMON, 1, 2, 3, 1)

        self.state.enemy_field[0] = front_enemy
        self.state.enemy_field[3] = back_enemy  # Ligne arrière

        target, pos = self.resolver._find_target(attacker, True, 0)

        assert target == back_enemy  # Frappe l'arrière car l'avant a un bouclier
        assert pos == 3

    def test_carapace_reduces_attacker_atk(self):
        """Test que Carapace réduit l'ATQ de l'attaquant"""
        attacker = Card("attacker", "Attacker", Biome.FORET, Rarity.COMMON, 1, 3, 4, 2)
        defender = Card("defender", "Defender", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)
        defender.keywords.add(Keyword.CARAPACE)
        defender.shields = 1

        self.resolver._resolve_attack(attacker, defender, 3)

        assert attacker.current_atk == 2  # Réduit de 1
        assert defender.shields == 0  # Bouclier consommé
        assert defender.current_dur == 4  # Pas de dégâts

    def test_play_card_cost_energy(self):
        """Test que jouer une carte coûte de l'énergie"""
        card = Card("test", "Test", Biome.FORET, Rarity.COMMON, 2, 2, 3, 1)
        self.state.hand.append(card)
        self.state.energy = 3

        success = self.resolver.play_card(card, 0)

        assert success is True
        assert self.state.energy == 1  # 3 - 2
        assert self.state.player_field[0] == card
        assert card not in self.state.hand

    def test_play_card_insufficient_energy(self):
        """Test qu'on ne peut pas jouer sans énergie"""
        card = Card("test", "Test", Biome.FORET, Rarity.COMMON, 3, 2, 3, 1)
        self.state.hand.append(card)
        self.state.energy = 2

        success = self.resolver.play_card(card, 0)

        assert success is False
        assert self.state.energy == 2  # Inchangé
        assert self.state.player_field[0] is None

    def test_saignement_self_damage(self):
        """Test que le Saignement inflige des dégâts à l'attaquant"""
        attacker = Card("attacker", "Attacker", Biome.FORET, Rarity.COMMON, 1, 3, 5, 2)
        attacker.apply_status(StatusEffect.SAIGNEMENT, 2)
        defender = Card("defender", "Defender", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)

        self.state.player_field[0] = attacker
        self.state.enemy_field[0] = defender

        self.resolver._unit_attack(attacker, True, 0)

        assert attacker.current_dur == 3  # 5 - 2 de Saignement

    def test_terrain_lave_applies_brulure(self):
        """Test que le terrain Lave applique Brûlure"""
        card1 = Card("test1", "Test 1", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)
        card2 = Card("test2", "Test 2", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)
        card2.keywords.add(Keyword.VOL)

        self.state.player_field[0] = card1  # Ligne avant, pas Vol
        self.state.player_field[1] = card2  # Ligne avant, avec Vol
        self.state.terrain_modifiers['type'] = 'LAVE'

        self.resolver._apply_terrain_modifiers()

        assert StatusEffect.BRULURE in card1.permanent_statuses
        assert StatusEffect.BRULURE not in card2.permanent_statuses  # Vol ignore


class TestIntegrationCombat:
    """Tests d'intégration du combat"""

    def test_full_combat_scenario(self):
        """Test d'un scénario de combat complet"""
        state = CombatState()
        resolver = CombatResolver(state, rng_seed=42)

        # Setup joueur
        player_card1 = Card("p1", "Player 1", Biome.FORET, Rarity.COMMON, 1, 3, 5, 2)
        player_card2 = Card("p2", "Player 2", Biome.FORET, Rarity.COMMON, 1, 2, 4, 3)

        state.player_field[0] = player_card1
        state.player_field[1] = player_card2

        # Setup ennemi
        enemy_card1 = Card("e1", "Enemy 1", Biome.DUNES, Rarity.COMMON, 1, 2, 4, 1)
        enemy_card2 = Card("e2", "Enemy 2", Biome.DUNES, Rarity.COMMON, 1, 3, 3, 2)

        state.enemy_field[0] = enemy_card1
        state.enemy_field[3] = enemy_card2

        # Simuler plusieurs tours
        resolver.start_combat()

        for _ in range(3):
            resolver.process_turn()
            if state.is_combat_over() is not None:
                break

        # Vérifier que le combat s'est bien déroulé
        assert len(resolver.action_log) > 0

        # Au moins une créature doit avoir pris des dégâts
        damaged = False
        for field in [state.player_field, state.enemy_field]:
            for card in field:
                if card and card.current_dur < card.base_dur:
                    damaged = True
                    break

        assert damaged is True