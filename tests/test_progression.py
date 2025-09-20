# tests/test_progression.py
"""Tests pour le système de progression"""

import pytest
from pathlib import Path
import tempfile
import json

from core.progression import (
    MapGenerator, MapNode, NodeType, ActMap,
    EventSystem, MerchantSystem, AlchemySystem, MetaProgression
)
from core.entities import Biome, RunState, Card, Rarity, CardDatabase, StatusEffect


class TestMapGenerator:
    """Tests pour la génération de cartes"""

    def test_generate_act_structure(self):
        """Test de la structure d'un acte généré"""
        generator = MapGenerator(seed=42)
        act_map = generator.generate_act(1, Biome.FORET)

        assert act_map.act_number == 1
        assert act_map.biome == Biome.FORET
        assert len(act_map.nodes) > 0

        # Vérifier qu'il y a un boss
        assert act_map.boss_node is not None
        boss = act_map.nodes[act_map.boss_node]
        assert boss.node_type == NodeType.BOSS

    def test_node_connections(self):
        """Test que les nœuds sont bien connectés"""
        generator = MapGenerator(seed=42)
        act_map = generator.generate_act(1, Biome.FORET)

        # Le premier nœud doit avoir des connexions
        start_node = act_map.nodes[0]
        assert len(start_node.connections) > 0

        # Les connexions doivent être valides
        for connection in start_node.connections:
            assert 0 <= connection < len(act_map.nodes)

    def test_available_paths(self):
        """Test des chemins disponibles"""
        generator = MapGenerator(seed=42)
        act_map = generator.generate_act(1, Biome.FORET)

        # Au début, on doit avoir des chemins disponibles
        paths = act_map.get_available_paths()
        assert len(paths) > 0

        # Après avoir visité un nœud
        act_map.nodes[paths[0]].visited = True
        act_map.current_node = paths[0]
        new_paths = act_map.get_available_paths()

        # Les nouveaux chemins ne doivent pas inclure les nœuds visités
        assert paths[0] not in new_paths


class TestEventSystem:
    """Tests pour le système d'événements"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.card_db = CardDatabase()
        self.event_system = EventSystem(self.card_db)

    def test_capture_wounded_event(self):
        """Test de l'événement de capture"""
        deck = []
        run_state = RunState(current_deck=deck)

        result = self.event_system.process_event("wounded_specimen", 0, run_state)

        assert len(run_state.current_deck) == 1
        captured = run_state.current_deck[0]
        assert captured.current_dur < captured.base_dur

    def test_gain_fragments_event(self):
        """Test de gain de fragments"""
        run_state = RunState(current_deck=[], fragments=10)

        result = self.event_system.process_event("wounded_specimen", 1, run_state)

        assert run_state.fragments == 15  # 10 + 5
        assert "Gagné 5 Fragments" in result["message"]

    def test_buff_poison_all_event(self):
        """Test d'application de poison à tous"""
        card1 = Card("test1", "Test 1", Biome.FORET, Rarity.COMMON, 1, 2, 4, 1)
        card2 = Card("test2", "Test 2", Biome.FORET, Rarity.COMMON, 1, 3, 5, 1)
        run_state = RunState(current_deck=[card1, card2])

        result = self.event_system.process_event("toxic_spring", 0, run_state)

        assert card1.current_atk == 3  # 2 + 1
        assert card2.current_atk == 4  # 3 + 1
        assert StatusEffect.VENIN in card1.permanent_statuses
        assert StatusEffect.VENIN in card2.permanent_statuses


class TestMerchantSystem:
    """Tests pour le système de marchand"""

    def test_generate_shop(self):
        """Test de génération d'une boutique"""
        merchant = MerchantSystem()
        rng = random.Random(42)

        shop = merchant.generate_shop(1, Biome.FORET, rng)

        assert "cards" in shop
        assert "consumables" in shop
        assert "services" in shop

        assert len(shop["cards"]) >= 4
        assert len(shop["consumables"]) >= 1

    def test_price_scaling(self):
        """Test que les prix augmentent avec les actes"""
        merchant = MerchantSystem()
        rng = random.Random(42)

        shop_act1 = merchant.generate_shop(1, Biome.FORET, rng)
        shop_act2 = merchant.generate_shop(2, Biome.FORET, random.Random(42))
        shop_act3 = merchant.generate_shop(3, Biome.FORET, random.Random(42))

        # Les prix devraient augmenter
        avg_price_1 = sum(c["price"] for c in shop_act1["cards"]) / len(shop_act1["cards"])
        avg_price_2 = sum(c["price"] for c in shop_act2["cards"]) / len(shop_act2["cards"])
        avg_price_3 = sum(c["price"] for c in shop_act3["cards"]) / len(shop_act3["cards"])

        assert avg_price_2 >= avg_price_1
        assert avg_price_3 >= avg_price_2


class TestAlchemySystem:
    """Tests pour le système d'alchimie"""

    def test_fusion_same_biome(self):
        """Test de fusion de cartes du même biome"""
        card_db = CardDatabase()
        alchemy = AlchemySystem(card_db)

        card1 = Card("test1", "Test 1", Biome.FORET, Rarity.COMMON, 1, 2, 4, 2)
        card2 = Card("test2", "Test 2", Biome.FORET, Rarity.COMMON, 1, 3, 3, 1)

        rng = random.Random(42)
        fusion = alchemy.fuse_cards(card1, card2, rng)

        assert fusion.biome == Biome.FORET
        assert fusion.base_atk >= 2  # Au moins la moyenne
        assert fusion.base_dur >= 3

    def test_cannot_fuse_legendaries(self):
        """Test qu'on ne peut pas fusionner les légendaires"""
        card_db = CardDatabase()
        alchemy = AlchemySystem(card_db)

        card1 = Card("test1", "Test 1", Biome.FORET, Rarity.LEGENDARY, 3, 5, 7, 2)
        card2 = Card("test2", "Test 2", Biome.FORET, Rarity.COMMON, 1, 2, 3, 1)

        assert alchemy.can_fuse(card1, card2, 5) is False


class TestMetaProgression:
    """Tests pour la méta-progression"""

    def test_profile_creation(self):
        """Test de création de profil"""
        with tempfile.TemporaryDirectory() as tmpdir:
            meta = MetaProgression(Path(tmpdir))

            assert meta.profile["total_runs"] == 0
            assert meta.profile["victories"] == 0
            assert meta.profile["unlocked_cards"] == []

    def test_complete_run_victory(self):
        """Test de complétion d'une run victorieuse"""
        with tempfile.TemporaryDirectory() as tmpdir:
            meta = MetaProgression(Path(tmpdir))

            run_state = RunState(current_deck=[], score=1500)
            meta.complete_run(run_state, victory=True)

            assert meta.profile["total_runs"] == 1
            assert meta.profile["victories"] == 1
            assert meta.profile["trophies"] > 0

    def test_unlock_cards_by_trophies(self):
        """Test du déblocage de cartes par trophées"""
        with tempfile.TemporaryDirectory() as tmpdir:
            meta = MetaProgression(Path(tmpdir))

            # Simuler assez de trophées
            meta.profile["trophies"] = 150

            run_state = RunState(current_deck=[], score=500)
            unlocks = meta.unlock_cards(run_state)

            # Devrait avoir débloqué les cartes du palier 100
            assert "variant_brood_myrmid" in meta.profile["unlocked_cards"]
            assert "variant_fire_caracal" in meta.profile["unlocked_cards"]

    def test_save_and_load_profile(self):
        """Test de sauvegarde et chargement"""
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir)

            # Créer et modifier un profil
            meta1 = MetaProgression(save_path)
            meta1.profile["total_runs"] = 5
            meta1.profile["victories"] = 2
            meta1.save_profile()

            # Charger dans une nouvelle instance
            meta2 = MetaProgression(save_path)

            assert meta2.profile["total_runs"] == 5
            assert meta2.profile["victories"] == 2