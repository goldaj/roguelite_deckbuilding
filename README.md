# Écorces & Échos — Deckbuilder Roguelite (Pygame UI) v1.0

**Beau, jouable, complet** : UI cliquable, animations, assets visuels générés, et **run end-to-end** (3 actes + boss final).  
Architecture **modulaire** pour faire évoluer règles et contenu.

## Installation (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Linux/macOS :
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Tests coeur :
```bash
python -m unittest eecores.tests.test_core -v
```

## Points clés
- **Assets**: fond, cadres, boutons, icônes (ATQ/DUR/VIT + statuts) → `eecores/assets/` (générés).  
- **UI/UX**: drag & drop des cartes, toasts, mini-cards sur le board, progression de carte avec nœuds complétés.  
- **Run complète**: 3 actes, chaque acte = 4 nœuds (dont 1 élite) + boss ; écran **Victoire/Défaite**.  
- **Modulaire**: règles dans `eecores/core`, données `data/cards.json`, scènes UI isolées.



## Nouveautés v1.1
- **Deck Viewer** (bouton **Deck** ou touche **D**) accessible **à tout moment**.
- **Enchaînement automatique des nœuds** selon le pattern: **aléatoire, combat, aléatoire, combat, aléatoire, combat, aléatoire, combat, aléatoire, BOSS** (par acte).
- **Top bar unifiée** avec boutons **Deck** et **Aide**; panneau d’aide contextuel décrivant clairement chaque type de nœud.
- **Écran d’intro de nœud** (bannière 0,8s) qui explique où on arrive, puis entrée automatique.
