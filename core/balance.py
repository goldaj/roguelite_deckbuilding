# core/balance.py
"""Système d'équilibrage et simulateur de combat"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import random
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

from entities import Card, Biome, Rarity, StatusEffect, Keyword
from combat import CombatResolver, CombatState


@dataclass
class SimulationResult:
    """Résultat d'une simulation"""
    winner: str  # "player" ou "enemy"
    turns: int
    player_damage_dealt: int
    enemy_damage_dealt: int
    player_cards_lost: int
    enemy_cards_lost: int
    player_final_presence: int
    enemy_final_presence: int
    combat_log: List[str] = field(default_factory=list)


@dataclass
class CardStatistics:
    """Statistiques d'une carte sur plusieurs simulations"""
    card_id: str
    win_rate: float
    avg_damage_dealt: float
    avg_damage_taken: float
    avg_survival_rate: float
    avg_turns_alive: float
    usage_count: int
    synergy_scores: Dict[str, float] = field(default_factory=dict)

    def power_score(self) -> float:
        """Calcule un score de puissance global"""
        return (
                self.win_rate * 100 +
                self.avg_damage_dealt * 10 +
                self.avg_survival_rate * 50 -
                self.avg_damage_taken * 5
        )


class CombatSimulator:
    """Simulateur de combat pour l'équilibrage"""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.results: List[SimulationResult] = []
        self.card_stats: Dict[str, CardStatistics] = {}

    def simulate_combat(
            self,
            player_deck: List[Card],
            enemy_deck: List[Card],
            max_turns: int = 20
    ) -> SimulationResult:
        """Simule un combat complet"""

        # Créer l'état de combat
        state = CombatState()
        state.deck = player_deck.copy()
        resolver = CombatResolver(state, rng_seed=self.rng.randint(0, 999999))

        # Placer les ennemis
        for i, enemy in enumerate(enemy_deck[:6]):
            state.enemy_field[i] = enemy

        # Démarrer le combat
        resolver.start_combat()

        # Tracking
        initial_player_presence = sum(c.current_dur for c in player_deck)
        initial_enemy_presence = sum(c.current_dur for c in enemy_deck)
        player_damage_dealt = 0
        enemy_damage_dealt = 0

        # Simuler les tours
        turn_count = 0
        while turn_count < max_turns and state.is_combat_over() is None:
            turn_count += 1

            # IA simple pour jouer des cartes
            self._ai_play_cards(resolver, state)

            # Résoudre le tour
            resolver.process_turn()

            # Calculer les dégâts
            current_player_presence = state.get_presence(True)
            current_enemy_presence = state.get_presence(False)

            player_damage_dealt = initial_enemy_presence - current_enemy_presence
            enemy_damage_dealt = initial_player_presence - current_player_presence

        # Déterminer le gagnant
        victory = state.is_combat_over()
        if victory is None:
            # Timeout - celui avec le plus de présence gagne
            victory = state.get_presence(True) > state.get_presence(False)

        # Compter les pertes
        player_cards_lost = sum(1 for c in player_deck if c.current_dur <= 0)
        enemy_cards_lost = sum(1 for c in enemy_deck if c.current_dur <= 0)

        return SimulationResult(
            winner="player" if victory else "enemy",
            turns=turn_count,
            player_damage_dealt=player_damage_dealt,
            enemy_damage_dealt=enemy_damage_dealt,
            player_cards_lost=player_cards_lost,
            enemy_cards_lost=enemy_cards_lost,
            player_final_presence=state.get_presence(True),
            enemy_final_presence=state.get_presence(False),
            combat_log=resolver.action_log
        )

    def _ai_play_cards(self, resolver: CombatResolver, state: CombatState):
        """IA simple pour jouer des cartes"""
        # Jouer des cartes tant qu'on a de l'énergie
        while state.energy > 0 and state.hand:
            # Trier par coût croissant
            playable = [c for c in state.hand if c.cost <= state.energy]
            if not playable:
                break

            # Jouer la carte la plus chère qu'on peut se permettre
            card = max(playable, key=lambda c: c.cost)

            # Trouver une position libre
            for pos in range(6):
                if state.player_field[pos] is None:
                    if resolver.play_card(card, pos):
                        break
            else:
                break  # Pas de position libre

    def run_batch_simulation(
            self,
            num_simulations: int,
            player_deck_generator,
            enemy_deck_generator,
            act: int = 1
    ) -> Dict:
        """Lance plusieurs simulations pour l'analyse statistique"""

        results = []
        card_performance = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'times_played': 0,
            'times_survived': 0
        })

        for i in range(num_simulations):
            # Générer les decks
            player_deck = player_deck_generator(act)
            enemy_deck = enemy_deck_generator(act)

            # Simuler
            result = self.simulate_combat(player_deck, enemy_deck)
            results.append(result)

            # Analyser les performances des cartes
            for card in player_deck:
                stats = card_performance[card.id]
                stats['times_played'] += 1

                if result.winner == "player":
                    stats['wins'] += 1
                else:
                    stats['losses'] += 1

                if card.current_dur > 0:
                    stats['times_survived'] += 1

                # Estimer les dégâts (simplification)
                stats['damage_dealt'] += card.base_atk * result.turns
                stats['damage_taken'] += (card.base_dur - card.current_dur)

        # Calculer les statistiques finales
        win_rate = sum(1 for r in results if r.winner == "player") / num_simulations
        avg_turns = sum(r.turns for r in results) / num_simulations

        # Statistiques par carte
        for card_id, stats in card_performance.items():
            if stats['times_played'] > 0:
                self.card_stats[card_id] = CardStatistics(
                    card_id=card_id,
                    win_rate=stats['wins'] / stats['times_played'],
                    avg_damage_dealt=stats['damage_dealt'] / stats['times_played'],
                    avg_damage_taken=stats['damage_taken'] / stats['times_played'],
                    avg_survival_rate=stats['times_survived'] / stats['times_played'],
                    avg_turns_alive=avg_turns * stats['times_survived'] / stats['times_played'],
                    usage_count=stats['times_played']
                )

        return {
            'overall_win_rate': win_rate,
            'avg_turns': avg_turns,
            'avg_player_damage': sum(r.player_damage_dealt for r in results) / num_simulations,
            'avg_enemy_damage': sum(r.enemy_damage_dealt for r in results) / num_simulations,
            'results': results
        }

    def analyze_card_balance(self) -> pd.DataFrame:
        """Analyse l'équilibrage des cartes"""
        data = []

        for card_id, stats in self.card_stats.items():
            data.append({
                'card_id': card_id,
                'win_rate': stats.win_rate,
                'power_score': stats.power_score(),
                'avg_damage_dealt': stats.avg_damage_dealt,
                'avg_damage_taken': stats.avg_damage_taken,
                'survival_rate': stats.avg_survival_rate,
                'usage_count': stats.usage_count
            })

        df = pd.DataFrame(data)
        df = df.sort_values('power_score', ascending=False)

        return df

    def identify_problematic_cards(self, threshold: float = 0.65) -> Dict:
        """Identifie les cartes problématiques (trop fortes/faibles)"""

        overpowered = []
        underpowered = []

        for card_id, stats in self.card_stats.items():
            if stats.win_rate > threshold:
                overpowered.append({
                    'card_id': card_id,
                    'win_rate': stats.win_rate,
                    'power_score': stats.power_score(),
                    'reason': 'Win rate trop élevé'
                })
            elif stats.win_rate < (1 - threshold):
                underpowered.append({
                    'card_id': card_id,
                    'win_rate': stats.win_rate,
                    'power_score': stats.power_score(),
                    'reason': 'Win rate trop faible'
                })

        return {
            'overpowered': sorted(overpowered, key=lambda x: x['win_rate'], reverse=True),
            'underpowered': sorted(underpowered, key=lambda x: x['win_rate'])
        }

    def calculate_synergies(self) -> Dict[Tuple[str, str], float]:
        """Calcule les synergies entre paires de cartes"""
        synergies = {}

        # Analyser les résultats pour trouver les paires gagnantes
        for result in self.results:
            if result.winner == "player":
                # Identifier les cartes jouées ensemble
                # Calculer leur contribution à la victoire
                pass

        return synergies

    def generate_report(self, output_path: str = "balance_report.html"):
        """Génère un rapport HTML complet d'équilibrage"""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bestiaire - Rapport d'Équilibrage</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .stats {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .overpowered {{ background: #ffcccc; }}
                .underpowered {{ background: #ccccff; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Rapport d'Équilibrage - Bestiaire</h1>

            <h2>Statistiques Globales</h2>
            <div class="stats">
                <p>Nombre de simulations: {len(self.results)}</p>
                <p>Taux de victoire moyen: {self._calculate_avg_win_rate():.2%}</p>
                <p>Durée moyenne des combats: {self._calculate_avg_turns():.1f} tours</p>
            </div>

            <h2>Cartes Problématiques</h2>
            {self._generate_problematic_cards_html()}

            <h2>Top 10 Cartes par Score de Puissance</h2>
            {self._generate_top_cards_html()}

            <h2>Distribution des Raretés</h2>
            {self._generate_rarity_distribution_html()}
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Rapport généré: {output_path}")

    def _calculate_avg_win_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.winner == "player") / len(self.results)

    def _calculate_avg_turns(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.turns for r in self.results) / len(self.results)

    def _generate_problematic_cards_html(self) -> str:
        problems = self.identify_problematic_cards()

        html = "<div class='overpowered'><h3>Cartes Trop Puissantes</h3><ul>"
        for card in problems['overpowered'][:5]:
            html += f"<li>{card['card_id']}: {card['win_rate']:.2%} win rate</li>"
        html += "</ul></div>"

        html += "<div class='underpowered'><h3>Cartes Trop Faibles</h3><ul>"
        for card in problems['underpowered'][:5]:
            html += f"<li>{card['card_id']}: {card['win_rate']:.2%} win rate</li>"
        html += "</ul></div>"

        return html

    def _generate_top_cards_html(self) -> str:
        df = self.analyze_card_balance()

        html = "<table><tr><th>Carte</th><th>Score</th><th>Win Rate</th><th>Survie</th></tr>"
        for _, row in df.head(10).iterrows():
            html += f"""
            <tr>
                <td>{row['card_id']}</td>
                <td>{row['power_score']:.1f}</td>
                <td>{row['win_rate']:.2%}</td>
                <td>{row['survival_rate']:.2%}</td>
            </tr>
            """
        html += "</table>"

        return html

    def _generate_rarity_distribution_html(self) -> str:
        # Analyser la distribution par rareté
        rarity_stats = defaultdict(lambda: {'count': 0, 'win_rate': 0})

        # Agréger les données
        # ...

        html = "<table><tr><th>Rareté</th><th>Nombre</th><th>Win Rate Moyen</th></tr>"
        for rarity in [Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]:
            stats = rarity_stats.get(rarity.value, {'count': 0, 'win_rate': 0})
            html += f"""
            <tr>
                <td>{rarity.value}</td>
                <td>{stats['count']}</td>
                <td>{stats['win_rate']:.2%}</td>
            </tr>
            """
        html += "</table>"

        return html


class BalanceFormulas:
    """Formules d'équilibrage du jeu"""

    @staticmethod
    def calculate_card_budget(rarity: Rarity) -> int:
        """Calcule le budget de stats pour une rareté"""
        budgets = {
            Rarity.COMMON: 5,
            Rarity.UNCOMMON: 7,
            Rarity.RARE: 9,
            Rarity.EPIC: 11,
            Rarity.LEGENDARY: 13
        }
        return budgets.get(rarity, 5)

    @staticmethod
    def keyword_cost(keyword: Keyword) -> float:
        """Coût en budget d'un mot-clé"""
        costs = {
            Keyword.TIRAILLEUR: 0.5,
            Keyword.GARDE: 0.5,
            Keyword.VOL: 0.5,
            Keyword.PERCEE: 1.0,
            Keyword.BOND: 1.0,
            Keyword.CARAPACE: 1.0,
            Keyword.ETHEREE: 1.0
        }
        return costs.get(keyword, 0.5)

    @staticmethod
    def status_effect_value(effect: StatusEffect) -> float:
        """Valeur d'un effet de statut"""
        values = {
            StatusEffect.VENIN: 0.75,
            StatusEffect.BRULURE: 0.75,
            StatusEffect.SAIGNEMENT: 0.5,  # Auto-dégâts
            StatusEffect.FRACTURE: 1.0,
            StatusEffect.MALEDICTION: 0.5,
            StatusEffect.EROSION: 1.0
        }
        return values.get(effect, 0.5)

    @staticmethod
    def calculate_card_score(card: Card) -> float:
        """Calcule le score théorique d'une carte"""
        score = 0.0

        # Stats de base
        score += card.base_atk * 1.0
        score += card.base_dur * 0.8
        score += (card.base_spd - 1) * 0.5

        # Mots-clés
        for keyword in card.keywords:
            score += BalanceFormulas.keyword_cost(keyword)

        # Coût en énergie (négatif)
        score -= card.cost * 0.5

        return score

    @staticmethod
    def validate_card(card: Card) -> Dict[str, Any]:
        """Valide qu'une carte respecte les règles d'équilibrage"""
        budget = BalanceFormulas.calculate_card_budget(card.rarity)
        actual_cost = BalanceFormulas.calculate_card_score(card)

        return {
            'valid': abs(actual_cost - budget) <= 1.0,
            'budget': budget,
            'actual': actual_cost,
            'difference': actual_cost - budget,
            'recommendation': BalanceFormulas._get_recommendation(actual_cost - budget)
        }

    @staticmethod
    def _get_recommendation(difference: float) -> str:
        """Recommandation pour équilibrer une carte"""
        if difference > 1.0:
            return "Carte trop puissante: réduire les stats ou augmenter le coût"
        elif difference < -1.0:
            return "Carte trop faible: augmenter les stats ou réduire le coût"
        else:
            return "Carte équilibrée"

    @staticmethod
    def calculate_enemy_scaling(act: int, is_elite: bool = False) -> Dict:
        """Calcule les stats ennemies selon l'acte"""
        base_hp = 3
        base_atk = 1

        # Scaling par acte
        hp_multiplier = 1.0 + (act - 1) * 0.3
        atk_multiplier = 1.0 + (act - 1) * 0.2

        # Bonus élite
        if is_elite:
            hp_multiplier *= 1.5
            atk_multiplier *= 1.3

        return {
            'hp_range': (
                int(base_hp * hp_multiplier * 0.8),
                int(base_hp * hp_multiplier * 1.2)
            ),
            'atk_range': (
                int(base_atk * atk_multiplier * 0.9),
                int(base_atk * atk_multiplier * 1.1)
            ),
            'speed': random.randint(1, 3)
        }


# Script de test d'équilibrage
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Ajouter le chemin parent
    sys.path.append(str(Path(__file__).parent.parent))

    from entities import CardDatabase

    print("🎯 Lancement du simulateur d'équilibrage...")

    # Initialiser
    card_db = CardDatabase()
    simulator = CombatSimulator(seed=42)


    # Générateurs de deck
    def generate_player_deck(act: int) -> List[Card]:
        """Génère un deck joueur typique"""
        deck = []
        for _ in range(12):
            card = card_db.create_card("forest_spine_frog")
            deck.append(card)
        return deck


    def generate_enemy_deck(act: int) -> List[Card]:
        """Génère des ennemis selon l'acte"""
        deck = []
        for _ in range(2 + act):
            card = card_db.create_card("dunes_solar_fennec")
            # Scaling
            scaling = BalanceFormulas.calculate_enemy_scaling(act)
            card.base_dur = random.randint(*scaling['hp_range'])
            card.base_atk = random.randint(*scaling['atk_range'])
            card.current_dur = card.base_dur
            card.current_atk = card.base_atk
            deck.append(card)
        return deck


    # Simuler
    print("⚔️ Simulation de 100 combats...")
    results = simulator.run_batch_simulation(
        100,
        generate_player_deck,
        generate_enemy_deck,
        act=1
    )

    print(f"\n📊 Résultats:")
    print(f"  Win rate: {results['overall_win_rate']:.2%}")
    print(f"  Durée moyenne: {results['avg_turns']:.1f} tours")
    print(f"  Dégâts moyens infligés: {results['avg_player_damage']:.1f}")
    print(f"  Dégâts moyens reçus: {results['avg_enemy_damage']:.1f}")

    # Analyser l'équilibrage
    print("\n🔍 Analyse d'équilibrage...")
    df = simulator.analyze_card_balance()
    print("\nTop 5 cartes:")
    print(df.head())

    # Identifier les problèmes
    problems = simulator.identify_problematic_cards()
    if problems['overpowered']:
        print("\n⚠️ Cartes trop puissantes:")
        for card in problems['overpowered'][:3]:
            print(f"  - {card['card_id']}: {card['win_rate']:.2%}")

    if problems['underpowered']:
        print("\n⚠️ Cartes trop faibles:")
        for card in problems['underpowered'][:3]:
            print(f"  - {card['card_id']}: {card['win_rate']:.2%}")

    # Générer le rapport
    simulator.generate_report("balance_report.html")
    print("\n✅ Rapport HTML généré: balance_report.html")