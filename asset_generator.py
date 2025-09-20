#!/usr/bin/env python3
"""
Générateur automatique d'assets pour Bestiaire
Crée tous les prompts pour générer les illustrations avec Midjourney/DALL-E
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import requests
import time
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np


# ============================================================================
# GÉNÉRATEUR DE PROMPTS POUR ILLUSTRATIONS
# ============================================================================

@dataclass
class CardPrompt:
    """Prompt pour générer une illustration de carte"""
    card_id: str
    name: str
    biome: str
    creature_type: str
    visual_style: str
    prompt_midjourney: str
    prompt_dalle: str
    negative_prompt: str


class AssetGenerator:
    """Génère tous les assets du jeu"""

    def __init__(self):
        self.output_dir = Path("assets/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Styles visuels par biome
        self.biome_styles = {
            "forest": {
                "palette": "deep greens, moss, emerald, dew drops",
                "atmosphere": "humid, misty, organic",
                "style": "watercolor ink wash"
            },
            "dunes": {
                "palette": "ochre, crimson, burnt orange, sand",
                "atmosphere": "hot, dry, shimmering heat",
                "style": "bold ink strokes"
            },
            "cliffs": {
                "palette": "grays, pale blues, white mist",
                "atmosphere": "foggy, ethereal, windswept",
                "style": "minimalist sumi-e"
            },
            "river": {
                "palette": "deep blues, blacks, murky greens",
                "atmosphere": "dark, mysterious, flowing",
                "style": "fluid ink technique"
            },
            "volcano": {
                "palette": "black, red, orange, ash gray",
                "atmosphere": "smoky, glowing, destructive",
                "style": "dramatic chiaroscuro"
            },
            "ruins": {
                "palette": "purple, gold, ancient stone",
                "atmosphere": "mystical, crumbling, arcane",
                "style": "detailed etching"
            },
            "neutral": {
                "palette": "neutral grays, soft earth tones",
                "atmosphere": "balanced, natural",
                "style": "clean line art"
            }
        }

        # Base prompt template
        self.base_prompt = """
        {creature_description}, creature card game illustration,
        {biome_style}, {color_palette},
        ink and watercolor art style, 
        strong silhouette, centered composition,
        white background, no text, no borders,
        professional TCG art, high contrast,
        style of Mike Mignola meets Studio Ghibli
        """

        self.negative_prompt = """
        text, typography, letters, numbers, watermark, signature,
        frame, border, multiple creatures, human, anime character,
        3D render, photograph, realistic, blurry, low quality,
        oversaturated, busy background
        """

    def generate_all_card_prompts(self) -> List[CardPrompt]:
        """Génère tous les prompts pour les 100 cartes"""

        prompts = []

        # Charger la base de données des cartes
        cards_data = self.load_cards_database()

        for card_id, card_info in cards_data.items():
            prompt = self.create_card_prompt(card_id, card_info)
            prompts.append(prompt)

        # Sauvegarder tous les prompts
        self.save_prompts_to_file(prompts)

        return prompts

    def create_card_prompt(self, card_id: str, card_info: Dict) -> CardPrompt:
        """Crée un prompt pour une carte spécifique"""

        biome = card_info.get("biome", "neutral")
        name = card_info.get("name", "Unknown")

        # Déterminer le type de créature
        creature_type = self.extract_creature_type(name)

        # Récupérer le style du biome
        style = self.biome_styles.get(biome, self.biome_styles["neutral"])

        # Créer la description détaillée
        description = self.create_creature_description(name, creature_type, card_info)

        # Prompt pour Midjourney
        prompt_mj = f"""
        {description}, fantasy creature, {creature_type},
        {style['style']} art style, {style['palette']} color palette,
        {style['atmosphere']} atmosphere,
        centered creature portrait, white background,
        trading card game illustration, 
        ink and wash technique, strong silhouette,
        --ar 3:4 --style raw --v 6
        """

        # Prompt pour DALL-E 3
        prompt_dalle = f"""
        A {creature_type} creature called '{name}' for a card game,
        illustrated in {style['style']} style with {style['palette']} colors.
        The creature should have {description}.
        {style['atmosphere']} atmosphere.
        White background, no text, centered composition.
        Style: ink wash and watercolor, reminiscent of traditional Asian art
        mixed with modern fantasy card game aesthetics.
        """

        return CardPrompt(
            card_id=card_id,
            name=name,
            biome=biome,
            creature_type=creature_type,
            visual_style=style['style'],
            prompt_midjourney=self.clean_prompt(prompt_mj),
            prompt_dalle=self.clean_prompt(prompt_dalle),
            negative_prompt=self.negative_prompt
        )

    def extract_creature_type(self, name: str) -> str:
        """Extrait le type de créature du nom"""

        # Dictionnaire de traduction FR -> EN
        creature_types = {
            "Grenouille": "frog",
            "Mygale": "spider",
            "Sanglier": "boar",
            "Serpent": "snake",
            "Mante": "mantis",
            "Dryade": "dryad",
            "Crapaud": "toad",
            "Fennec": "fennec fox",
            "Scorpion": "scorpion",
            "Couleuvre": "snake",
            "Hyène": "hyena",
            "Dromadaire": "camel",
            "Sphinx": "sphinx",
            "Phénix": "phoenix",
            "Ver": "worm",
            "Goéland": "seagull",
            "Chauve-Souris": "bat",
            "Harrier": "hawk",
            "Roc": "roc bird",
            "Piranha": "piranha",
            "Lamproie": "lamprey",
            "Tortue": "turtle",
            "Silure": "catfish",
            "Brochet": "pike",
            "Crabe": "crab",
            "Nixe": "water nymph",
            "Anguille": "eel",
            "Hydre": "hydra",
            "Gekko": "gecko",
            "Molosse": "mastiff",
            "Iguane": "iguana",
            "Salamandre": "salamander",
            "Chacal": "jackal",
            "Dragon": "dragon",
            "Rat": "rat",
            "Gargouille": "gargoyle",
            "Spectre": "specter",
            "Hibou": "owl",
            "Golem": "golem"
        }

        for fr, en in creature_types.items():
            if fr.lower() in name.lower():
                return en

        return "creature"

    def create_creature_description(self, name: str, creature_type: str, card_info: Dict) -> str:
        """Crée une description visuelle détaillée"""

        descriptions = {
            "forest_spine_frog": "spiky forest frog with thorny skin, moss-covered back, alert eyes, defensive posture",
            "forest_azure_spider": "large azure-blue tarantula with iridescent hairs, dew drops on web, eight gleaming eyes",
            "dunes_solar_fennec": "small desert fox with oversized ears, golden fur, quick and agile stance",
            "volcano_pyroclast_tyrant": "massive lava beast with molten rock skin, crown of fire, magma veins glowing through cracks",
            # ... ajouter toutes les descriptions
        }

        card_id = card_info.get("id", "")
        if card_id in descriptions:
            return descriptions[card_id]

        # Description générique basée sur le type
        return f"fantasy {creature_type} with magical aura"

    def clean_prompt(self, prompt: str) -> str:
        """Nettoie un prompt"""
        lines = [line.strip() for line in prompt.strip().split('\n')]
        return ' '.join(filter(None, lines))

    def load_cards_database(self) -> Dict:
        """Charge la base de données des cartes"""
        # Simuler le chargement depuis cards.json
        return {
            "forest_spine_frog": {"name": "Grenouille Épineuse", "biome": "forest"},
            "forest_azure_spider": {"name": "Mygale d'Azur", "biome": "forest"},
            "dunes_solar_fennec": {"name": "Fennec Solaire", "biome": "dunes"},
            # ... toutes les cartes
        }

    def save_prompts_to_file(self, prompts: List[CardPrompt]):
        """Sauvegarde tous les prompts dans des fichiers"""

        # Fichier maître avec tous les prompts
        output_file = self.output_dir / "all_prompts.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# PROMPTS MIDJOURNEY POUR BESTIAIRE\n")
            f.write("# Copier-coller chaque prompt dans Midjourney\n\n")

            for prompt in prompts:
                f.write(f"## {prompt.name} ({prompt.card_id})\n")
                f.write(f"```\n{prompt.prompt_midjourney}\n```\n\n")

        # Fichier JSON pour automatisation
        json_file = self.output_dir / "prompts.json"
        json_data = [
            {
                "id": p.card_id,
                "name": p.name,
                "midjourney": p.prompt_midjourney,
                "dalle": p.prompt_dalle,
                "negative": p.negative_prompt
            }
            for p in prompts
        ]

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(prompts)} prompts sauvegardés dans {output_file}")


# ============================================================================
# GÉNÉRATEUR D'ASSETS TEMPORAIRES
# ============================================================================

class PlaceholderGenerator:
    """Génère des placeholders en attendant les vraies illustrations"""

    def __init__(self):
        self.card_width = 512
        self.card_height = 704
        self.output_dir = Path("assets/cards/temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_placeholders(self):
        """Génère des placeholders pour toutes les cartes"""

        cards = self.load_cards_database()

        for card_id, card_info in cards.items():
            self.create_placeholder_card(card_id, card_info)

        print(f"✅ {len(cards)} placeholders générés dans {self.output_dir}")

    def create_placeholder_card(self, card_id: str, card_info: Dict):
        """Crée une image placeholder pour une carte"""

        # Créer l'image de base
        img = Image.new('RGB', (self.card_width, self.card_height), 'white')
        draw = ImageDraw.Draw(img)

        # Couleur selon le biome
        biome_colors = {
            "forest": (100, 150, 100),
            "dunes": (200, 150, 100),
            "cliffs": (150, 150, 180),
            "river": (100, 120, 180),
            "volcano": (180, 100, 100),
            "ruins": (150, 100, 180),
            "neutral": (140, 140, 140)
        }

        biome = card_info.get("biome", "neutral")
        color = biome_colors.get(biome, (128, 128, 128))

        # Dessiner le fond coloré
        draw.rectangle([0, 0, self.card_width, self.card_height], fill=color)

        # Ajouter un cadre
        draw.rectangle([10, 10, self.card_width - 10, self.card_height - 10],
                       outline='white', width=5)

        # Ajouter le nom
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()

        name = card_info.get("name", card_id)
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (self.card_width - text_width) // 2
        draw.text((text_x, 50), name, fill='white', font=font)

        # Ajouter une forme géométrique au centre
        center_x = self.card_width // 2
        center_y = self.card_height // 2

        shape_type = hash(card_id) % 3
        if shape_type == 0:  # Cercle
            draw.ellipse([center_x - 100, center_y - 100, center_x + 100, center_y + 100],
                         fill='white', outline='black', width=3)
        elif shape_type == 1:  # Triangle
            points = [
                (center_x, center_y - 100),
                (center_x - 87, center_y + 50),
                (center_x + 87, center_y + 50)
            ]
            draw.polygon(points, fill='white', outline='black', width=3)
        else:  # Carré
            draw.rectangle([center_x - 80, center_y - 80, center_x + 80, center_y + 80],
                           fill='white', outline='black', width=3)

        # Ajouter les stats
        stats = f"ATK:{card_info.get('atk', 0)} DUR:{card_info.get('dur', 0)}"
        draw.text((20, self.card_height - 50), stats, fill='white', font=font)

        # Sauvegarder
        output_path = self.output_dir / f"{card_id}.png"
        img.save(output_path)

    def load_cards_database(self) -> Dict:
        """Charge la base de données simplifiée"""
        # Ici on devrait charger depuis cards.json
        # Pour l'exemple, on retourne quelques cartes
        return {
            f"card_{i}": {
                "name": f"Carte {i}",
                "biome": ["forest", "dunes", "cliffs", "river", "volcano", "ruins"][i % 6],
                "atk": (i % 5) + 1,
                "dur": (i % 7) + 2
            }
            for i in range(100)
        }


# ============================================================================
# POST-TRAITEMENT DES IMAGES
# ============================================================================

class ImageProcessor:
    """Post-traite les images générées par IA"""

    def __init__(self):
        self.card_width = 512
        self.card_height = 704

    def process_card_image(self, input_path: Path, output_path: Path):
        """Traite une image de carte"""

        img = Image.open(input_path)

        # 1. Redimensionner si nécessaire
        if img.size != (self.card_width, self.card_height):
            img = img.resize((self.card_width, self.card_height), Image.LANCZOS)

        # 2. Améliorer le contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        # 3. Ajouter un léger vignettage
        img = self.add_vignette(img)

        # 4. Ajouter un cadre subtil
        img = self.add_border(img)

        # 5. Optimiser pour le jeu
        img = img.convert('RGB')
        img.save(output_path, 'PNG', optimize=True, quality=95)

    def add_vignette(self, img: Image.Image) -> Image.Image:
        """Ajoute un effet de vignettage"""

        # Créer un masque de vignette
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)

        for i in range(min(img.size) // 2):
            alpha = 255 - int(255 * (i / (min(img.size) / 2)) ** 2)
            draw.ellipse([i, i, img.size[0] - i, img.size[1] - i], fill=alpha)

        # Appliquer le masque
        black = Image.new('RGB', img.size, 'black')
        img = Image.composite(img, black, mask)

        return img

    def add_border(self, img: Image.Image) -> Image.Image:
        """Ajoute un cadre à l'image"""

        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                       outline='black', width=2)

        return img

    def batch_process(self, input_dir: Path, output_dir: Path):
        """Traite toutes les images d'un dossier"""

        output_dir.mkdir(parents=True, exist_ok=True)

        for img_path in input_dir.glob("*.png"):
            output_path = output_dir / img_path.name
            self.process_card_image(img_path, output_path)
            print(f"✅ Traité: {img_path.name}")


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    """Génère tous les assets nécessaires"""

    print("""
    ╔════════════════════════════════════════════╗
    ║     BESTIAIRE - GÉNÉRATEUR D'ASSETS       ║
    ╚════════════════════════════════════════════╝
    """)

    print("1. Génération des prompts pour illustrations...")
    generator = AssetGenerator()
    prompts = generator.generate_all_card_prompts()

    print(f"\n2. Création de {len(prompts)} placeholders...")
    placeholder = PlaceholderGenerator()
    placeholder.generate_all_placeholders()

    print("\n3. Instructions pour les illustrations finales:")
    print("   a) Ouvrir assets/generated/all_prompts.txt")
    print("   b) Copier chaque prompt dans Midjourney")
    print("   c) Paramètres recommandés: --ar 3:4 --style raw --v 6")
    print("   d) Sauvegarder les images dans assets/cards/raw/")
    print("   e) Lancer le post-traitement")

    print("\n4. Pour post-traiter les images:")
    print("   python asset_generator.py --process")

    print("\n✅ Génération terminée!")
    print(f"   - Prompts: assets/generated/all_prompts.txt")
    print(f"   - Placeholders: assets/cards/temp/")
    print(f"   - JSON: assets/generated/prompts.json")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--process":
        print("Post-traitement des images...")
        processor = ImageProcessor()
        processor.batch_process(
            Path("assets/cards/raw"),
            Path("assets/cards/final")
        )
    else:
        main()