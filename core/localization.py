# core/localization.py
"""Système de localisation multi-langues"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class Language(Enum):
    """Langues supportées"""
    EN = "en"  # English
    FR = "fr"  # Français
    ES = "es"  # Español
    DE = "de"  # Deutsch
    IT = "it"  # Italiano
    PT = "pt"  # Português
    RU = "ru"  # Русский
    JA = "ja"  # 日本語
    KO = "ko"  # 한국어
    ZH = "zh"  # 中文


class LocalizationManager:
    """Gestionnaire de localisation"""

    def __init__(self, data_path: Path = Path("data/localization")):
        self.data_path = data_path
        self.current_language = Language.EN
        self.fallback_language = Language.EN

        # Cache des traductions
        self.translations: Dict[Language, Dict[str, Any]] = {}

        # Charger toutes les langues disponibles
        self.load_all_languages()

    def load_all_languages(self):
        """Charge tous les fichiers de langue"""
        for language in Language:
            lang_file = self.data_path / f"{language.value}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[language] = json.load(f)
                print(f"✅ Langue chargée: {language.value}")
            else:
                print(f"⚠️ Fichier de langue manquant: {lang_file}")

    def set_language(self, language: Language):
        """Change la langue active"""
        if language in self.translations:
            self.current_language = language
            return True
        return False

    def get(self, key: str, **kwargs) -> str:
        """Récupère une traduction avec support des variables"""
        # Essayer la langue courante
        text = self._get_from_dict(self.translations.get(self.current_language, {}), key)

        # Fallback sur la langue par défaut
        if text is None and self.current_language != self.fallback_language:
            text = self._get_from_dict(self.translations.get(self.fallback_language, {}), key)

        # Si toujours pas trouvé, retourner la clé
        if text is None:
            return f"[{key}]"

        # Remplacer les variables
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Ignorer les variables manquantes

        return text

    def _get_from_dict(self, data: Dict, key: str) -> Optional[str]:
        """Récupère une valeur depuis un dictionnaire avec support des clés imbriquées"""
        keys = key.split('.')
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return str(current) if current is not None else None

    def get_card_name(self, card_id: str) -> str:
        """Récupère le nom d'une carte"""
        return self.get(f"cards.{card_id}.name")

    def get_card_description(self, card_id: str) -> str:
        """Récupère la description d'une carte"""
        return self.get(f"cards.{card_id}.description")

    def get_biome_name(self, biome: str) -> str:
        """Récupère le nom d'un biome"""
        return self.get(f"biomes.{biome}.name")

    def get_status_name(self, status: str) -> str:
        """Récupère le nom d'un statut"""
        return self.get(f"status.{status}.name")

    def get_status_description(self, status: str) -> str:
        """Récupère la description d'un statut"""
        return self.get(f"status.{status}.description")

    def format_damage(self, damage: int) -> str:
        """Formate un texte de dégâts"""
        return self.get("combat.damage", damage=damage)

    def format_heal(self, amount: int) -> str:
        """Formate un texte de soin"""
        return self.get("combat.heal", amount=amount)

    def get_available_languages(self) -> List[Language]:
        """Retourne la liste des langues disponibles"""
        return list(self.translations.keys())


# Exemple de fichier de traduction (data/localization/en.json)
ENGLISH_TRANSLATIONS = {
    "menu": {
        "new_game": "New Game",
        "continue": "Continue",
        "settings": "Settings",
        "quit": "Quit",
        "credits": "Credits"
    },
    "game": {
        "turn": "Turn {turn}",
        "energy": "Energy: {current}/{max}",
        "presence": "Presence",
        "deck": "Deck",
        "hand": "Hand",
        "discard": "Discard"
    },
    "combat": {
        "victory": "Victory!",
        "defeat": "Defeat...",
        "damage": "{damage} damage",
        "heal": "+{amount} HP",
        "shield": "+{amount} Shield",
        "your_turn": "Your Turn",
        "enemy_turn": "Enemy Turn"
    },
    "cards": {
        "forest_spine_frog": {
            "name": "Spiny Frog",
            "description": "Punishes summons"
        },
        "forest_azure_spider": {
            "name": "Azure Spider",
            "description": "Slow attrition"
        },
        "forest_ivy_boar": {
            "name": "Ivy Boar",
            "description": "Cheap frontline"
        }
        # ... toutes les cartes
    },
    "status": {
        "venin": {
            "name": "Venom",
            "description": "Take {value} damage at combat start"
        },
        "brulure": {
            "name": "Burn",
            "description": "Take {value} damage at combat end"
        },
        "saignement": {
            "name": "Bleed",
            "description": "Take {value} damage when attacking"
        },
        "fracture": {
            "name": "Fracture",
            "description": "-{value} ATK permanently"
        },
        "malediction": {
            "name": "Curse",
            "description": "-1 Speed at combat start"
        },
        "erosion": {
            "name": "Erosion",
            "description": "-1 HP at each node"
        }
    },
    "keywords": {
        "tirailleur": "Sniper: +1 ATK vs new summons",
        "garde": "Guard: Protects backline",
        "vol": "Flying: Ignores ground effects",
        "percee": "Pierce: Bypasses shields",
        "bond": "Pounce: Targets weakest enemy",
        "carapace": "Shell: Reduces attacker's ATK",
        "etheree": "Ethereal: Cannot be targeted by melee"
    },
    "biomes": {
        "forest": {
            "name": "Humid Forest",
            "description": "Venom and growth"
        },
        "dunes": {
            "name": "Crimson Dunes",
            "description": "Fire and speed"
        },
        "cliffs": {
            "name": "Misty Cliffs",
            "description": "Flight and ethereal"
        },
        "river": {
            "name": "Dark River",
            "description": "Bleed and armor"
        },
        "volcano": {
            "name": "Black Volcano",
            "description": "Burn and destruction"
        },
        "ruins": {
            "name": "Arcane Ruins",
            "description": "Curses and erosion"
        }
    },
    "events": {
        "wounded_specimen": {
            "title": "Wounded Specimen",
            "description": "You find a wounded creature. Capturing it would add it to your deck, but it will arrive very weakened.",
            "choice_1": "Capture (50% HP)",
            "choice_2": "Heal and release (+5 Fragments)"
        }
    },
    "tutorial": {
        "welcome": "Welcome to Bestiaire!",
        "attrition": "Remember: all damage is permanent for the entire run.",
        "shields": "Shields are your only protection - use them wisely.",
        "energy": "You have {energy} energy per turn to play cards."
    },
    "settings": {
        "language": "Language",
        "volume": "Volume",
        "master": "Master",
        "music": "Music",
        "sfx": "Sound Effects",
        "fullscreen": "Fullscreen",
        "vsync": "VSync",
        "apply": "Apply",
        "cancel": "Cancel"
    },
    "errors": {
        "save_corrupted": "Save file corrupted",
        "load_failed": "Failed to load game",
        "connection_lost": "Connection lost"
    }
}

# Fichier de traduction français (data/localization/fr.json)
FRENCH_TRANSLATIONS = {
    "menu": {
        "new_game": "Nouvelle Partie",
        "continue": "Continuer",
        "settings": "Paramètres",
        "quit": "Quitter",
        "credits": "Crédits"
    },
    "game": {
        "turn": "Tour {turn}",
        "energy": "Énergie : {current}/{max}",
        "presence": "Présence",
        "deck": "Deck",
        "hand": "Main",
        "discard": "Défausse"
    },
    "combat": {
        "victory": "Victoire !",
        "defeat": "Défaite...",
        "damage": "{damage} dégâts",
        "heal": "+{amount} PV",
        "shield": "+{amount} Bouclier",
        "your_turn": "Votre Tour",
        "enemy_turn": "Tour Ennemi"
    },
    "cards": {
        "forest_spine_frog": {
            "name": "Grenouille Épineuse",
            "description": "Punit les invocations"
        },
        "forest_azure_spider": {
            "name": "Mygale d'Azur",
            "description": "Attrition lente"
        },
        "forest_ivy_boar": {
            "name": "Sanglier Lierre",
            "description": "Ligne de front économique"
        }
    },
    "status": {
        "venin": {
            "name": "Venin",
            "description": "Subir {value} dégâts au début du combat"
        },
        "brulure": {
            "name": "Brûlure",
            "description": "Subir {value} dégâts à la fin du combat"
        },
        "saignement": {
            "name": "Saignement",
            "description": "Subir {value} dégâts en attaquant"
        },
        "fracture": {
            "name": "Fracture",
            "description": "-{value} ATQ permanent"
        },
        "malediction": {
            "name": "Malédiction",
            "description": "-1 Vitesse au début du combat"
        },
        "erosion": {
            "name": "Érosion",
            "description": "-1 PV à chaque nœud"
        }
    },
    "keywords": {
        "tirailleur": "Tirailleur : +1 ATQ contre nouvelles invocations",
        "garde": "Garde : Protège la ligne arrière",
        "vol": "Vol : Ignore les effets au sol",
        "percee": "Percée : Traverse les boucliers",
        "bond": "Bond : Cible l'ennemi le plus faible",
        "carapace": "Carapace : Réduit l'ATQ de l'attaquant",
        "etheree": "Éthéré : Ne peut être ciblé au corps-à-corps"
    },
    "biomes": {
        "forest": {
            "name": "Forêt Humide",
            "description": "Poison et croissance"
        },
        "dunes": {
            "name": "Dunes Cramoisies",
            "description": "Feu et vitesse"
        },
        "cliffs": {
            "name": "Falaises Brumeuses",
            "description": "Vol et éthéré"
        },
        "river": {
            "name": "Fleuve Obscur",
            "description": "Saignement et armure"
        },
        "volcano": {
            "name": "Volcan Noir",
            "description": "Brûlure et destruction"
        },
        "ruins": {
            "name": "Ruines Arcanes",
            "description": "Malédictions et érosion"
        }
    }
}
