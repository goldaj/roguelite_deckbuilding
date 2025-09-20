# BESTIAIRE: Écorces & Échos

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Build](https://img.shields.io/github/workflow/status/studio-ecorces/bestiaire/CI)

## 🎮 Le Roguelite Deckbuilding où Chaque Cicatrice Raconte une Histoire

**Bestiaire** est un roguelite deckbuilding innovant où l'attrition permanente transforme chaque décision en dilemme crucial. Vos créatures portent les marques indélébiles de chaque combat - dégâts, poisons, malédictions - tout persiste jusqu'à la fin de votre run.

### ✨ Caractéristiques Principales

- **🩸 Attrition Permanente** : Pas de soin, pas de repos. Chaque blessure reste.
- **🎯 Runs Courtes & Intenses** : 15-30 minutes de tension pure
- **🦎 100+ Créatures Uniques** : 6 biomes, chacun avec son écosystème
- **⚔️ Combat Stratégique** : Positionnement, timing, sacrifices calculés
- **🔄 Méta-progression Élégante** : Débloquez de nouvelles créatures sans power creep
- **🎨 Direction Artistique Sobre** : Style encre et estampe minimaliste

---

## 🚀 Installation

### Méthode 1: Exécutable (Recommandé)

Téléchargez la dernière version pour votre OS:
- [Windows](https://github.com/studio-ecorces/bestiaire/releases/latest/download/bestiaire-windows.zip)
- [macOS](https://github.com/studio-ecorces/bestiaire/releases/latest/download/bestiaire-macos.zip)
- [Linux](https://github.com/studio-ecorces/bestiaire/releases/latest/download/bestiaire-linux.tar.gz)

### Méthode 2: Depuis les Sources

```bash
# Cloner le repository
git clone https://github.com/studio-ecorces/bestiaire.git
cd bestiaire

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le jeu
python main.py
```

### Méthode 3: Installation via pip

```bash
pip install bestiaire-roguelite
bestiaire
```

---

## 🎯 Guide de Jeu

### Concepts Fondamentaux

#### L'Attrition Permanente
Chaque créature qui subit des dégâts les garde pour toute la run. Une créature à 5/10 DUR restera à 5 DUR maximum jusqu'à la fin de votre aventure.

#### Les Altérations
- **🟢 Venin** : Dégâts au début de chaque combat
- **🔥 Brûlure** : Dégâts à la fin de chaque combat
- **🩸 Saignement** : Dégâts quand la créature attaque
- **💀 Malédiction** : -1 Vitesse au début du combat
- **⚫ Fracture** : -1 ATQ permanent
- **🌊 Érosion** : -1 DUR à chaque nœud traversé

#### Structure d'une Run
1. **3 Actes** avec biomes aléatoires
2. **4-5 Nœuds** par acte + Boss
3. **Boss Final** après le 3ème acte
4. **Durée** : 15-30 minutes

### Stratégies de Base

#### Économie de Ressources
- Les **Boucliers** sont votre seule protection - utilisez-les avec parcimonie
- Les **Œufs** compensent les pertes sans soigner
- Les **Gènes** permettent de fusionner des cartes faibles

#### Archétypes de Decks
- **🔥 Brûlure/Percée** : Agressif, dégâts post-combat
- **🟢 Poison/Érosion** : Contrôle, victoire par attrition
- **🩸 Saignement** : Risk/reward, glass cannon
- **🛡️ Garde/Carapace** : Défensif, préservation

---

## 🛠️ Documentation Technique

### Architecture

```
bestiaire/
├── core/
│   ├── entities.py      # Cartes, états, structures de données
│   ├── combat.py        # Moteur de combat
│   ├── progression.py   # Cartes, événements, méta-progression
│   └── effects.py       # Système d'effets et mots-clés
├── ui/
│   ├── interface.py     # Interface pygame
│   ├── scenes.py        # Scènes du jeu
│   └── animations.py    # Système d'animation
├── data/
│   ├── cards.json       # Base de données des 100 cartes
│   ├── events.json      # Événements narratifs
│   └── biomes.json      # Configuration des biomes
├── assets/
│   ├── images/          # Sprites et illustrations
│   ├── sounds/          # Effets sonores
│   └── fonts/           # Polices
└── tests/               # Tests automatisés
```

### Système de Combat

Le combat se déroule en tours simultanés avec résolution par vitesse :

```python
# Exemple de résolution de tour
def process_turn():
    units = sort_by_speed(all_units)
    for unit in units:
        target = find_target(unit)
        resolve_attack(unit, target)
        apply_effects(unit, target)
```

### Système d'Altérations Permanentes

```python
class Card:
    def apply_status(self, effect: StatusEffect, value: int):
        """Applique une altération permanente"""
        self.permanent_statuses[effect] += value
        
        # Effets immédiats
        if effect == StatusEffect.FRACTURE:
            self.current_atk = max(1, self.current_atk - value)
```

### Format de Carte (JSON)

```json
{
  "id": "forest_toxic_toad",
  "name": "Crapaud Toxique",
  "biome": "forest",
  "rarity": "R",
  "cost": 2,
  "atk": 1,
  "dur": 5,
  "spd": 1,
  "keywords": [],
  "on_hit": [{"effect": "VENIN", "value": 1}],
  "description": "Zone de danger"
}
```

---

## 💼 Document Commercial

### Proposition de Valeur

**Bestiaire** réinvente le roguelite deckbuilding en introduisant une mécanique d'attrition permanente qui transforme chaque partie en une histoire de survie unique.

### Marché Cible

- **Cœur de cible** : Joueurs de Slay the Spire, Inscryption, Wildfrost
- **Secondaire** : Amateurs de roguelikes tactiques (Into the Breach, FTL)
- **Âge** : 16-35 ans
- **Plateformes** : PC (Steam), Mobile (phase 2), Switch (phase 3)

### Différenciateurs Compétitifs

1. **Attrition Permanente** : Unique sur le marché
2. **Runs Courtes** : Parfait pour le mobile/casual
3. **Profondeur Stratégique** : Rejouabilité infinie
4. **Direction Artistique** : Style distinctif encre/estampe

### Modèle Économique

- **Prix de lancement** : 14,99€ (PC)
- **DLC gratuits** : Nouveaux biomes tous les 3 mois
- **Pas de microtransactions** : Jeu premium complet
- **Version mobile** : 7,99€ (prévu Q2 2025)

### Roadmap

#### v1.0 (Lancement)
- 100 cartes
- 6 biomes
- Système de méta-progression

#### v1.1 (Mois 1)
- Mode Défi Quotidien
- Classements en ligne
- 20 nouvelles cartes

#### v1.2 (Mois 3)
- Nouveau biome : Marais Toxique
- Boss alternatifs
- Mode Ascension (difficulté++)

#### v2.0 (Mois 6)
- Multijoueur asynchrone
- Éditeur de deck
- Workshop Steam

### Métriques de Succès

- **Objectif ventes Year 1** : 50,000 copies
- **Note cible Steam** : >85% positif
- **Rétention J30** : >40%
- **Session moyenne** : 25 minutes

---

## 🧪 Tests

### Lancer les Tests

```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=bestiaire tests/

# Tests de performance
python -m pytest tests/test_performance.py -v

# Tests d'intégration
python -m pytest tests/integration/ -v
```

### Tests Automatiques (CI/CD)

Le projet utilise GitHub Actions pour:
- Tests sur Python 3.9, 3.10, 3.11, 3.12
- Build automatique Windows/macOS/Linux
- Analyse de couverture avec Codecov
- Déploiement automatique sur release

---

## 🏗️ Build & Distribution

### Créer un Exécutable

```bash
# Build pour toutes les plateformes
python build.py all

# Build spécifique
python build.py windows
python build.py macos
python build.py linux
```

### Packaging PyPI

```bash
# Créer le package
python setup.py sdist bdist_wheel

# Upload sur PyPI
twine upload dist/*
```

### Docker

```bash
# Build l'image
docker build -t bestiaire .

# Lancer le conteneur
docker run -it bestiaire
```

---

## 📊 Métriques & Analytics

### Events Trackés

- `game_start` : Nouvelle run
- `combat_end` : Résultat de combat
- `card_played` : Carte jouée
- `node_visited` : Nœud visité
- `run_end` : Fin de run (victoire/défaite)
- `card_unlocked` : Nouvelle carte débloquée

### KPIs Principaux

- **ARPU** : Average Revenue Per User
- **DAU/MAU** : Daily/Monthly Active Users
- **Retention** : D1, D7, D30
- **Session Length** : Durée moyenne
- **Win Rate** : Taux de victoire par acte

---

## 🤝 Contribution

Nous accueillons les contributions ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

### Guidelines

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Code Style

- Black formatter (ligne 100 caractères)
- Type hints obligatoires
- Docstrings Google style
- Tests pour toute nouvelle fonctionnalité

---

## 📄 License

MIT License - voir [LICENSE](LICENSE)

---

## 🙏 Crédits

### Équipe Core

- **Game Design** : [Votre nom]
- **Programmation** : [Votre nom]
- **Art** : IA + retouches manuelles
- **Audio** : [Compositeur]

### Technologies

- **Python** 3.9+
- **Pygame** 2.5+
- **Pydantic** pour la validation
- **Hypothesis** pour les tests
- **PyInstaller** pour les builds

### Inspirations

- Slay the Spire
- Inscryption
- Darkest Dungeon
- Monster Train

---

## 📞 Contact

- **Email** : contact@bestiaire-game.com
- **Discord** : [discord.gg/bestiaire](https://discord.gg/bestiaire)
- **Twitter** : [@BestiaireGame](https://twitter.com/BestiaireGame)
- **Site Web** : [bestiaire-game.com](https://bestiaire-game.com)

---

## 🎯 Prochaines Étapes pour la Commercialisation

1. **Page Steam** : Créer et optimiser avec trailer, screenshots
2. **Campagne Marketing** : 
   - Streamers/YouTubers ciblés
   - Reddit (r/roguelikes, r/indiegames)
   - Game jams et festivals
3. **Beta Fermée** : 100 testeurs, feedback itératif
4. **Lancement Early Access** : 3 mois avant v1.0
5. **Partenariats** : Humble Bundle, Epic Games Store

---

*Bestiaire: Où chaque cicatrice raconte une histoire, et chaque défaite forge une légende.*