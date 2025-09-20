# core/progression.py
"""Système de progression, nœuds et meta-progression"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum, auto
import random
import json
from pathlib import Path

from entities import Card, RunState, Biome, Rarity, StatusEffect, CardDatabase


class NodeType(Enum):
    COMBAT = "combat"
    ELITE = "elite"
    EVENT = "event"
    MERCHANT = "merchant"
    ALCHEMY = "alchemy"
    SANCTUARY = "sanctuary"
    BOSS = "boss"
    REST = "rest"
    TREASURE = "treasure"


class EventType(Enum):
    CHOICE = auto()  # Choix risque/récompense
    CAPTURE = auto()  # Capture d'un spécimen blessé
    PACT = auto()  # Pacte avec conséquences
    TERRAIN = auto()  # Modification du prochain combat
    SACRIFICE = auto()  # Sacrifier pour gain


@dataclass
class MapNode:
    """Nœud sur la carte"""
    id: int
    node_type: NodeType
    biome: Biome
    x: int
    y: int
    connections: List[int] = field(default_factory=list)
    visited: bool = False
    revealed: bool = False

    # Données spécifiques au type
    enemy_pool: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    event_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.node_type.value,
            'biome': self.biome.value,
            'position': [self.x, self.y],
            'connections': self.connections,
            'visited': self.visited,
            'revealed': self.revealed
        }


@dataclass
class ActMap:
    """Carte d'un acte"""
    act_number: int
    biome: Biome
    nodes: List[MapNode]
    current_node: int = 0
    boss_node: Optional[int] = None

    def get_available_paths(self) -> List[int]:
        """Retourne les chemins disponibles depuis le nœud actuel"""
        if self.current_node >= len(self.nodes):
            return []

        current = self.nodes[self.current_node]
        available = []

        for connection in current.connections:
            if connection < len(self.nodes) and not self.nodes[connection].visited:
                available.append(connection)

        return available

    def reveal_connected_nodes(self):
        """Révèle les nœuds connectés au nœud actuel"""
        current = self.nodes[self.current_node]
        for connection in current.connections:
            if connection < len(self.nodes):
                self.nodes[connection].revealed = True


class MapGenerator:
    """Générateur de cartes procédurales"""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def generate_act(self, act_number: int, biome: Biome) -> ActMap:
        """Génère une carte pour un acte"""
        act_map = ActMap(act_number=act_number, biome=biome, nodes=[])

        # Structure de base: 5 niveaux de profondeur
        # Niveau 0: départ (1 nœud)
        # Niveaux 1-3: chemins (3-4 nœuds chacun)
        # Niveau 4: boss (1 nœud)

        node_id = 0
        levels = []

        # Nœud de départ
        start_node = MapNode(
            id=node_id,
            node_type=NodeType.COMBAT,
            biome=biome,
            x=400,
            y=50,
            revealed=True
        )
        act_map.nodes.append(start_node)
        levels.append([start_node])
        node_id += 1

        # Générer les niveaux intermédiaires
        for level in range(1, 4):
            level_nodes = []
            node_count = self.rng.randint(3, 4)

            for i in range(node_count):
                # Déterminer le type de nœud
                node_type = self._choose_node_type(level, i)

                # Position
                x = 200 + (i * 200)
                y = 50 + (level * 150)

                node = MapNode(
                    id=node_id,
                    node_type=node_type,
                    biome=biome,
                    x=x,
                    y=y
                )

                # Ajouter les ennemis si combat
                if node_type in [NodeType.COMBAT, NodeType.ELITE]:
                    node.enemy_pool = self._generate_enemy_pool(biome, act_number,
                                                                node_type == NodeType.ELITE)

                level_nodes.append(node)
                act_map.nodes.append(node)
                node_id += 1

            levels.append(level_nodes)

        # Nœud de boss
        boss_node = MapNode(
            id=node_id,
            node_type=NodeType.BOSS,
            biome=biome,
            x=400,
            y=500,
            enemy_pool=[self._get_boss_id(biome)]
        )
        act_map.nodes.append(boss_node)
        act_map.boss_node = node_id
        levels.append([boss_node])

        # Créer les connexions entre niveaux
        for i in range(len(levels) - 1):
            current_level = levels[i]
            next_level = levels[i + 1]

            for node in current_level:
                # Connecter à 1-2 nœuds du niveau suivant
                connections = self.rng.randint(1, min(2, len(next_level)))
                targets = self.rng.sample(next_level, connections)

                for target in targets:
                    node.connections.append(target.id)

        return act_map

    def _choose_node_type(self, level: int, position: int) -> NodeType:
        """Choisit le type de nœud selon le niveau et la position"""
        if level == 1:
            # Premier niveau: principalement combats
            weights = {
                NodeType.COMBAT: 70,
                NodeType.EVENT: 20,
                NodeType.MERCHANT: 10
            }
        elif level == 2:
            # Milieu: plus varié
            weights = {
                NodeType.COMBAT: 40,
                NodeType.ELITE: 20,
                NodeType.EVENT: 15,
                NodeType.MERCHANT: 10,
                NodeType.ALCHEMY: 10,
                NodeType.SANCTUARY: 5
            }
        else:
            # Fin: plus difficile
            weights = {
                NodeType.COMBAT: 30,
                NodeType.ELITE: 30,
                NodeType.EVENT: 20,
                NodeType.ALCHEMY: 10,
                NodeType.REST: 10
            }

        total = sum(weights.values())
        roll = self.rng.random() * total

        current = 0
        for node_type, weight in weights.items():
            current += weight
            if roll < current:
                return node_type

        return NodeType.COMBAT

    def _generate_enemy_pool(self, biome: Biome, act: int, is_elite: bool) -> List[str]:
        """Génère la pool d'ennemis pour un nœud"""
        # Logique simplifiée - à enrichir avec les vraies données
        pool = []

        if is_elite:
            # Élite: 1-2 ennemis forts
            pool.append(f"{biome.value}_elite_{act}")
        else:
            # Combat normal: 2-3 ennemis
            count = self.rng.randint(2, 3)
            for i in range(count):
                pool.append(f"{biome.value}_common_{self.rng.randint(1, 3)}")

        return pool

    def _get_boss_id(self, biome: Biome) -> str:
        """Retourne l'ID du boss pour un biome"""
        bosses = {
            Biome.FORET: "forest_ancient_stag",
            Biome.DUNES: "dunes_juvenile_fireworm",
            Biome.FALAISES: "cliffs_specter_roc",
            Biome.FLEUVE: "river_mnemonic_catfish",
            Biome.VOLCAN: "volcano_pyroclast_tyrant",
            Biome.RUINES: "ruins_archsphinx"
        }
        return bosses.get(biome, "neutral_nascent_chimera")


class EventSystem:
    """Système d'événements narratifs"""

    def __init__(self, card_db: CardDatabase):
        self.card_db = card_db
        self.events = self._load_events()

    def _load_events(self) -> Dict[str, Dict]:
        """Charge les événements depuis la configuration"""
        return {
            "wounded_specimen": {
                "type": EventType.CAPTURE,
                "title": "Spécimen Blessé",
                "description": "Vous trouvez une créature blessée. La capturer pourrait l'ajouter à votre deck, mais elle arrivera très affaiblie.",
                "choices": [
                    {
                        "text": "Capturer (50% DUR)",
                        "effect": "capture_wounded"
                    },
                    {
                        "text": "Soigner et relâcher (+5 Fragments)",
                        "effect": "gain_fragments",
                        "value": 5
                    }
                ]
            },
            "toxic_spring": {
                "type": EventType.CHOICE,
                "title": "Source Toxique",
                "description": "Une source mystérieuse. L'eau semble empoisonnée mais pourrait renforcer vos créatures.",
                "choices": [
                    {
                        "text": "Faire boire à tous (+1 ATQ, Venin 1)",
                        "effect": "buff_poison_all"
                    },
                    {
                        "text": "Éviter prudemment",
                        "effect": "none"
                    }
                ]
            },
            "merchant_ambush": {
                "type": EventType.CHOICE,
                "title": "Embuscade Marchande",
                "description": "Un marchand vous tend une embuscade. Négocier ou combattre?",
                "choices": [
                    {
                        "text": "Payer 20 Fragments",
                        "effect": "pay_fragments",
                        "value": 20
                    },
                    {
                        "text": "Combattre (Élite surprise)",
                        "effect": "surprise_elite"
                    }
                ]
            },
            "ancient_altar": {
                "type": EventType.SACRIFICE,
                "title": "Autel Ancien",
                "description": "Un autel demande un sacrifice. Offrir une créature pour un pouvoir permanent?",
                "choices": [
                    {
                        "text": "Sacrifier une carte (+1 Énergie max)",
                        "effect": "sacrifice_for_energy"
                    },
                    {
                        "text": "Refuser",
                        "effect": "none"
                    }
                ]
            }
        }

    def process_event(self, event_id: str, choice: int, run_state: RunState) -> Dict:
        """Traite un événement et retourne les résultats"""
        if event_id not in self.events:
            return {}

        event = self.events[event_id]
        chosen = event["choices"][choice]
        effect = chosen["effect"]

        results = {"message": "", "changes": {}}

        if effect == "capture_wounded":
            # Ajouter une carte blessée au deck
            new_card = self._generate_random_card(run_state.current_act)
            new_card.current_dur = max(1, new_card.base_dur // 2)
            run_state.current_deck.append(new_card)
            results["message"] = f"Capturé: {new_card.name} ({new_card.current_dur}/{new_card.base_dur} DUR)"

        elif effect == "gain_fragments":
            value = chosen.get("value", 0)
            run_state.fragments += value
            results["message"] = f"Gagné {value} Fragments"

        elif effect == "buff_poison_all":
            for card in run_state.current_deck:
                card.current_atk += 1
                card.apply_status(StatusEffect.VENIN, 1)
            results["message"] = "Toutes vos créatures: +1 ATQ, Venin 1"

        elif effect == "pay_fragments":
            value = chosen.get("value", 0)
            if run_state.fragments >= value:
                run_state.fragments -= value
                results["message"] = f"Payé {value} Fragments"
            else:
                results["message"] = "Fragments insuffisants!"
                results["force_combat"] = True

        elif effect == "sacrifice_for_energy":
            if run_state.current_deck:
                # Interface pour choisir quelle carte sacrifier
                results["requires_card_selection"] = True
                results["callback"] = "sacrifice_card"

        return results

    def _generate_random_card(self, act: int) -> Card:
        """Génère une carte aléatoire appropriée à l'acte"""
        rarities = [Rarity.COMMON, Rarity.COMMON, Rarity.UNCOMMON]
        if act >= 2:
            rarities.append(Rarity.RARE)
        if act >= 3:
            rarities.append(Rarity.EPIC)

        rarity = random.choice(rarities)
        # Filtrer les cartes par rareté
        # Retourner une carte aléatoire
        return self.card_db.create_card("forest_spine_frog")  # Placeholder


class MerchantSystem:
    """Système de marchand"""

    def __init__(self):
        self.base_prices = {
            Rarity.COMMON: 15,
            Rarity.UNCOMMON: 25,
            Rarity.RARE: 40,
            Rarity.EPIC: 60,
            Rarity.LEGENDARY: 100
        }

        self.consumable_prices = {
            "shield": 10,
            "egg": 30,
            "remove_card": 50
        }

    def generate_shop(self, act: int, biome: Biome, rng: random.Random) -> Dict:
        """Génère l'inventaire d'un marchand"""
        shop = {
            "cards": [],
            "consumables": [],
            "services": []
        }

        # Cartes à vendre (4-6)
        card_count = rng.randint(4, 6)
        for i in range(card_count):
            # Logique de génération selon l'acte
            card_data = self._generate_shop_card(act, biome, rng)
            shop["cards"].append(card_data)

        # Consommables
        shop["consumables"].append({
            "type": "shield",
            "count": rng.randint(1, 3),
            "price": self.consumable_prices["shield"]
        })

        if rng.random() < 0.3:
            shop["consumables"].append({
                "type": "egg",
                "count": 1,
                "price": self.consumable_prices["egg"]
            })

        # Services
        shop["services"].append({
            "type": "remove_card",
            "price": self.consumable_prices["remove_card"]
        })

        return shop

    def _generate_shop_card(self, act: int, biome: Biome, rng: random.Random) -> Dict:
        """Génère une carte pour le marchand"""
        # Déterminer la rareté selon l'acte
        if act == 1:
            rarity_weights = {Rarity.COMMON: 60, Rarity.UNCOMMON: 35, Rarity.RARE: 5}
        elif act == 2:
            rarity_weights = {Rarity.COMMON: 30, Rarity.UNCOMMON: 50, Rarity.RARE: 18, Rarity.EPIC: 2}
        else:
            rarity_weights = {Rarity.UNCOMMON: 30, Rarity.RARE: 50, Rarity.EPIC: 18, Rarity.LEGENDARY: 2}

        # Sélection pondérée
        total = sum(rarity_weights.values())
        roll = rng.random() * total
        current = 0

        selected_rarity = Rarity.COMMON
        for rarity, weight in rarity_weights.items():
            current += weight
            if roll < current:
                selected_rarity = rarity
                break

        price = self.base_prices[selected_rarity]

        # Ajuster le prix selon l'acte
        price = int(price * (1 + 0.1 * (act - 1)))

        return {
            "card_id": f"{biome.value}_sample",  # À remplacer par vraie génération
            "rarity": selected_rarity,
            "price": price
        }


class AlchemySystem:
    """Système d'alchimie/fusion de cartes"""

    def __init__(self, card_db: CardDatabase):
        self.card_db = card_db
        self.fusion_rules = self._init_fusion_rules()

    def _init_fusion_rules(self) -> Dict:
        """Initialise les règles de fusion"""
        return {
            "same_biome": {
                "bonus_stats": 1,
                "keep_keywords": True
            },
            "different_biomes": {
                "bonus_stats": 0,
                "hybrid_keywords": True
            }
        }

    def can_fuse(self, card1: Card, card2: Card, genes: int) -> bool:
        """Vérifie si deux cartes peuvent fusionner"""
        if genes < 1:
            return False

        # Pas de fusion de légendaires
        if card1.rarity == Rarity.LEGENDARY or card2.rarity == Rarity.LEGENDARY:
            return False

        return True

    def fuse_cards(self, card1: Card, card2: Card, rng: random.Random) -> Card:
        """Fusionne deux cartes en une nouvelle"""
        # Déterminer le biome résultant
        if card1.biome == card2.biome:
            result_biome = card1.biome
            rules = self.fusion_rules["same_biome"]
        else:
            result_biome = rng.choice([card1.biome, card2.biome])
            rules = self.fusion_rules["different_biomes"]

        # Calculer les stats
        avg_atk = (card1.base_atk + card2.base_atk) // 2
        avg_dur = (card1.base_dur + card2.base_dur) // 2
        avg_spd = (card1.base_spd + card2.base_spd) // 2

        if rules.get("bonus_stats"):
            avg_atk += rules["bonus_stats"]

        # Déterminer le coût
        new_cost = max(1, min(3, (card1.cost + card2.cost) // 2 + rng.randint(0, 1)))

        # Créer la nouvelle carte
        fusion_id = f"fusion_{rng.randint(1000, 9999)}"
        fusion_name = f"Chimère {card1.name.split()[0]}-{card2.name.split()[0]}"

        new_card = Card(
            id=fusion_id,
            name=fusion_name,
            biome=result_biome,
            rarity=Rarity.UNCOMMON,
            cost=new_cost,
            base_atk=avg_atk,
            base_dur=avg_dur,
            base_spd=avg_spd
        )

        # Hériter de certains mots-clés
        if rules.get("keep_keywords"):
            if card1.keywords:
                new_card.keywords.add(rng.choice(list(card1.keywords)))

        return new_card


class MetaProgression:
    """Système de méta-progression entre les runs"""

    def __init__(self, save_path: Path = Path("saves")):
        self.save_path = save_path
        self.save_path.mkdir(exist_ok=True)

        self.profile_path = self.save_path / "profile.json"
        self.profile = self.load_profile()

    def load_profile(self) -> Dict:
        """Charge le profil du joueur"""
        if self.profile_path.exists():
            with open(self.profile_path, 'r') as f:
                return json.load(f)

        return {
            "total_runs": 0,
            "victories": 0,
            "total_score": 0,
            "best_score": 0,
            "trophies": 0,
            "unlocked_cards": [],
            "achievements": [],
            "statistics": {
                "total_damage_dealt": 0,
                "total_damage_taken": 0,
                "cards_played": 0,
                "enemies_defeated": 0
            }
        }

    def save_profile(self):
        """Sauvegarde le profil"""
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)

    def complete_run(self, run_state: RunState, victory: bool):
        """Enregistre la fin d'une run"""
        self.profile["total_runs"] += 1

        if victory:
            self.profile["victories"] += 1

        self.profile["total_score"] += run_state.score
        if run_state.score > self.profile["best_score"]:
            self.profile["best_score"] = run_state.score

        # Calculer les trophées gagnés
        trophies = self.calculate_trophies(run_state, victory)
        self.profile["trophies"] += trophies
        run_state.trophies = trophies

        # Débloquer de nouvelles cartes
        self.unlock_cards(run_state)

        self.save_profile()

    def calculate_trophies(self, run_state: RunState, victory: bool) -> int:
        """Calcule les trophées gagnés"""
        trophies = 0

        # Base pour complétion
        if victory:
            trophies += 100
        else:
            trophies += 10 * run_state.current_act

        # Bonus pour score
        if run_state.score >= 1000:
            trophies += 20
        if run_state.score >= 2000:
            trophies += 30
        if run_state.score >= 3000:
            trophies += 50

        return trophies

    def unlock_cards(self, run_state: RunState):
        """Débloque de nouvelles cartes selon les performances"""
        unlocks = []

        # Débloquer selon les paliers de trophées
        total_trophies = self.profile["trophies"]

        trophy_unlocks = {
            100: ["variant_brood_myrmid", "variant_fire_caracal"],
            250: ["variant_armored_pike", "variant_ash_rhea"],
            500: ["exotic_antlion", "exotic_polar_fox"],
            1000: ["exotic_frost_sphinx", "variant_living_sculpture"],
            2000: ["exotic_dust_cerberus", "exotic_ancient_alder"]
        }

        for threshold, cards in trophy_unlocks.items():
            if total_trophies >= threshold:
                for card_id in cards:
                    if card_id not in self.profile["unlocked_cards"]:
                        self.profile["unlocked_cards"].append(card_id)
                        unlocks.append(card_id)

        # Débloquer selon les achievements
        if victory and run_state.current_act >= 3:
            if "first_victory" not in self.profile["achievements"]:
                self.profile["achievements"].append("first_victory")
                unlocks.extend(["variant_mist_scythe", "variant_styx_mastiff"])

        return unlocks

    def get_available_starter_cards(self) -> List[str]:
        """Retourne les cartes disponibles pour le pool de départ"""
        base_cards = [
            "forest_spine_frog", "forest_azure_spider",
            "dunes_solar_fennec", "neutral_scout_rat"
        ]

        return base_cards + self.profile["unlocked_cards"]