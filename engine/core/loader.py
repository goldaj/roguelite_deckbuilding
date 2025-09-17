import json, random
from typing import List
from engine.models.card import CardData, Trigger

def load_all_cards(path: str) -> List[CardData]:
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    cards = []
    for c in raw['cards']:
        triggers = [Trigger(**t) for t in c.get('triggers', [])]
        cards.append(CardData(
            id=c['id'],
            name=c['name'],
            biome=c['biome'],
            rarity=c['rarity'],
            cost=c['cost'],
            atk=c['atk'],
            dur=c['dur'],
            spd=c['spd'],
            keywords=c.get('keywords', []),
            keyword_values=c.get('keyword_values', {}),
            triggers=triggers,
            notes=c.get('notes', '')
        ))
    return cards

def make_player_deck(all_cards: List[CardData], size: int = 10) -> List[CardData]:
    return [random.choice(all_cards) for _ in range(size)]

def pick_enemy_cards(all_cards: List[CardData], cols: int = 4):
    return [random.choice(all_cards) for _ in range(cols)]
