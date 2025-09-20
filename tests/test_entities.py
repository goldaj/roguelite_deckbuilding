# tests/test_entities.py
"""Tests pour les entités du jeu"""

import pytest
from hypothesis import given, strategies as st
from typing import List

from bestiaire.core.entities import (
    Card, StatusEffect, Keyword, Rarity, Biome,
    CombatState, RunState, CardDatabase
)


class TestCard:
    """Tests pour la classe Card"""

    def test_card_creation(self):
        """Test de création basique d'une carte"""
        card = Card(
            id="test_card",
            name="Test Card",
            biome=Biome.FORET,
            rarity=Rarity.COMMON,
            cost=1,
            base_atk=2,
            base_dur=3,
            base_spd=2
        )

        assert card.id == "test_card"
        assert card.current_dur == 3
        assert card.current_atk == 2
        assert card.current_spd == 2

    def test_take_damage(self):
        """Test des dégâts permanents"""
        card = Card(
            id="test",
            name="Test",
            biome=Biome.FORET,
            rarity=Rarity.COMMON,
            cost=1,
            base_atk=2,
            base_dur=5,
            base_spd=2
        )

        # Dégâts normaux
        survived = card.take_damage(2)
        assert survived is True
        assert card.current_dur == 3

        # Dégâts létaux
        survived = card.take_damage(4)
        assert survived is False
        assert card.current_dur == -1

    def test_shields_absorb_damage(self):
        """Test que les boucliers absorbent les dégâts"""
        card = Card(
            id="test",
            name="Test",
            biome=Biome.FORET,
            rarity=Rarity.COMMON,
            cost=1,
            base_atk=2,
            base_dur=5,
            base_spd=2
        )
        card.shields = 2

        # Les boucliers absorbent
        card.take_damage(3)
        assert card.shields == 0
        assert card.current_dur == 4

    def test_status_effects(self):
        """Test des altérations permanentes"""
        card = Card(
            id="test",
            name="Test",
            biome=Biome.FORET,
            rarity=Rarity.COMMON,
            cost=1,
            base_atk=3,
            base_dur=5,
            base_spd=2
        )

        # Appliquer Venin
        card.apply_status(StatusEffect.VENIN, 2)
        assert card.permanent_statuses[StatusEffect.VENIN] == 2

        # Appliquer Fracture
        card.apply_status(StatusEffect.FRACTURE, 1)
        assert card.current_atk == 2  # Réduit immédiatement

        # Offense émoussée
        card.apply_status(StatusEffect.OFFENSE_EMOUSSEE, 1)
        assert card.get_effective_atk() == 1  # Plafonné à 1

    @given(
        atk=st.integers(min_value=1, max_value=10),
        dur=st.integers(min_value=1, max_value=10),
        spd=st.integers(min_value=1, max_value=3),
        damage=st.integers(min_value=0, max_value=20)
    )
    def test_damage_consistency(self, atk: int, dur: int, spd: int, damage: int):
        """Test de cohérence des dégâts avec Hypothesis"""
        card = Card(
            id="test",
            name="Test",
            biome=Biome.FORET,
            rarity=Rarity.COMMON,
            cost=1,
            base_atk=atk,
            base_dur=dur,
            base_spd=spd
        )

        initial_dur = card.current_dur
        card.take_damage(damage)

        # La durabilité doit diminuer ou la carte meurt
        assert card.current_dur <= initial_dur
        assert card.current_dur == initial_dur - damage

    def test_serialization(self):
        """Test de sérialisation/désérialisation"""
        card = Card(
            id="test",
            name="Test Card",
            biome=Biome.FORET,
            rarity=Rarity.RARE,
            cost=2,
            base_atk=3,
            base_dur=4,
            base_spd=2
        )
        card.apply_status(StatusEffect.VENIN, 1)
        card.shields = 1

        # Sérialiser
        data = card.to_dict()

        # Désérialiser
        restored = Card.from_dict(data)

        assert restored.id == card.id
        assert restored.name == card.name
        assert restored.shields == 1
        assert StatusEffect.VENIN in restored.permanent_statuses


class TestCombatState:
    """Tests pour l'état de combat"""

    def test_presence_calculation(self):
        """Test du calcul de présence"""
        state = CombatState()

        card1 = Card("test1", "Test 1", Biome.FORET, Rarity.COMMON, 1, 2, 3, 1)
        card2 = Card("test2", "Test 2", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)

        state.player_field[0] = card1
        state.player_field[2] = card2

        assert state.get_presence(True) == 7  # 3 + 4
        assert state.get_presence(False) == 0

    def test_combat_over_conditions(self):
        """Test des conditions de fin de combat"""
        state = CombatState()

        # Pas de créatures = match nul (None)
        assert state.is_combat_over() is None

        # Joueur a des créatures, ennemi non = victoire
        card = Card("test", "Test", Biome.FORET, Rarity.COMMON, 1, 2, 3, 1)
        state.player_field[0] = card
        assert state.is_combat_over() is True

        # Ennemi a des créatures, joueur non = défaite
        state.player_field[0] = None
        state.enemy_field[0] = card
        assert state.is_combat_over() is False
