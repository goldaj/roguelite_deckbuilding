# BESTIAIRE : Écorces & Échos — Document de conception (v1)

*Roguelite deckbuilding de créatures où chaque dégât et chaque altération est une cicatrice définitive durant toute la partie. Une run courte (15–30 min), nerveuse, lisible, mais stratégique et létale. Meta-progression : nouveaux spécimens débloqués pour enrichir le pool de départ.*

---

## 1) Pitch & Différenciateurs
**Pitch** — Vous dressez un bestiaire vivant. Chaque carte est un spécimen (animal, monstre, esprit). Les combats rongent vos cartes : **dégâts et effets sont permanents jusqu’à la fin de la run**. Vous avancez d’un biome à l’autre, gérez l’attrition, sacrifiez pour survivre. Une défaite remet tout à zéro, mais **de nouvelles cartes** potentiellement puissantes rejoignent le pool de départ des runs suivantes.

**Différenciateurs**
- **Attrition totale** : pas de soin, pas de purge. La survie dépend d’éviter l’impact plutôt que de le réparer.
- **Boucliers consommables** (coquilles, carapaces, parade) pour **dévier** le permanent au lieu de le soigner.
- **Écologie vivante** : chaque biome a ses proies/prédateurs, et des **match-ups** clairs.
- **Run courte, dense** : 10–14 rencontres + 1 boss, 15–30 minutes.
- **Meta-prog élégante** : pas de power creep démesuré, mais **variation du pool initial**.

Tone/Style — **Sobriété élégante**, inspirations estampes / encre / cell‑shading. Soundscape minimaliste, percussions sèches, chœurs discrets. UI claire, animée par micro‑mouvements.

---

## 2) Boucle de jeu
1. **Draft initial** : 10 cartes communes faiblardes + 2 neutres utilitaires.
2. **Carte des biomes** (nœuds) : Combat / Élite / Événement / Marchand / Alchimie (craft) / Sanctuaire des Œufs (incubation) / Boss.
3. **Combat** (1–3 vagues selon nœud) : rythme 4–8 tours. Récompense : fragments, spécimens capturés, consommables (boucliers), ou gènes.
4. **Attrition** : dégâts et altérations persistent. Les cartes détruites sont **définitivement perdues** pour la run.
5. **Progression** : choix de nœud suivant jusqu’au **Boss de biome** ; 3 biomes, puis **Boss final**.
6. **Fin de run** : score, trophées, **déblocages de cartes** (ajoutées au pool initial des runs futures).

Durée cible d’une run : **17–24 minutes** (médiane). Difficile : **28–32 min**.

---

## 3) Règles cœur (combat)
- **Main** : 5 cartes. **Énergie** par tour : 3 (progression possible à 4 dans certains événements). **Coût** des cartes : 0–3.
- **Stats carte** : `ATQ`, `DUR` (Durabilité, l’équivalent d’HP permanent), `Vitesse` (initiative locale 1–3), `Traits`.
- **Jouer une créature** l’invoque sur la **rangée** (avant/arrière). Elle **attaque** automatiquement selon sa Vitesse.
- **Cibles** : par défaut, face à elle ; certains traits « Percée » (frappe arrière), « Bond » (ignore l’avant), « Tirailleur » (punit les invocations).
- **Dégâts = ATQ**. Quand une créature **reçoit des dégâts**, **sa DUR diminue définitivement**. À 0 → **perdue pour la run**.
- **Altérations permanentes** (voir §6) : Venin, Brûlure, Saignement, Fracture, Malédiction… Elles collent à la carte jusqu’à la fin de la run.
- **Bouclier** : une **charge** absorbe **un impact** (dégâts OU une application d’altération). Les boucliers sont consommés au moment du coup, **ne soignent pas**.
- **Élites** : ajoutent modificateurs au terrain (Brouillard : -1 Vitesse à distance ; Lave : 1 Brûlure par tour à la frontlane si non volante).

Objectif d’un combat : réduire la **Présence** ennemie à 0 (somme des DUR des ennemis présents) OU éliminer le **Commandant** (si présent).

---

## 4) Économie & Ressources
- **Fragments** : monnaie run, pour Marchand/Alchimie.
- **Gènes** : ressource de craft (drop sur Élite/Boss). Permet de **fusionner** deux cartes faibles en une **nouvelle carte modeste** (jamais de soin, stats rollées sur une table dédiée).
- **Œufs** : consommable qui **pond** une carte **Neutre Jeune** après 2 nœuds (compense l’attrition sans annuler la philosophie « pas de soin »).
- **Trophées** : méta‑monnaie (hors run) pour **débloquer** des cartes dans le pool initial.

---

## 5) Nœuds de carte (roguelite)
- **Combat** : standard, 1 vague.
- **Élite** : 2 vagues, modificateurs. Récompense supérieure (Gènes, Artefact de terrain unique pour le biome).
- **Événement** : choix « risque/récompense » (capture d’un spécimen blessé, pacte, terrain altéré pour le prochain combat…).
- **Marchand** : acheter cartes/boucliers/œufs ; vendre cartes **blessées** (faible valeur) pour des Fragments.
- **Alchimie** : **fusion** de deux cartes en une nouvelle (table de craft par biome). Jamais de soin.
- **Sanctuaire des Œufs** : accélère les éclosions (incuber immédiatement un Œuf → obtention d’un **Jeune** aléatoire mais fragile).
- **Boss** : mécanique singulière, récompenses majeures (artefact + Gènes + capture spécifique).

---

## 6) Altérations (permanentes sur la run)
**Toutes persistent**, non dissipables :
- **Venin X** — Au **début de chaque combat**, subit X dégâts.
- **Brûlure X** — À la **fin de chaque combat**, subit X dégâts.
- **Saignement X** — À **chaque fois que la créature attaque**, perd X.
- **Fracture** — -1 **ATQ** permanent.
- **Offense émoussée** — **ATQ plafonnée** à 1 tant que la carte a au moins 1 Brûlure.
- **Malédiction** — Au **tour 1** de chaque combat, -1 Vitesse (min 1).
- **Érosion** — À chaque **nœud**, -1 DUR (faible mais inexorable).

**Mots-clés (non altérations)** :
- **Bouclier (n)** : bloque n impacts.
- **Percée** : frappe la cible arrière si l’avant est protégé par Bouclier.
- **Bond** : choisit toujours la cible la plus faible en DUR sur la ligne.
- **Carapace (n)** : convertit **le prochain coup reçu** en -n ATQ temporaire sur l’attaquant (jusqu’à fin du combat), au lieu de dégâts. (La victime garde ses altérations.)
- **Éthéré** : ne peut être ciblé par corps‑à‑corps ; vulnérable aux effets/à distance.
- **Vol** : ignore terrains de ligne (Lave/Brouillard).
- **Tirailleur** : +1 ATQ contre les invocations arrivées **ce tour**.
- **Garde** : si en **frontlane**, **intercepte** la première attaque destinée à l’arrière.

---

## 7) Structure d’une run & difficulté
- **Acts** : 3 biomes aléatoires parmi 6, puis **Boss final**.
- **Rencontres par acte** : 4 (dont 1 Élite) + 1 Boss.
- **Courbe** : Acte 1 (apprentissage), Acte 2 (attrition marquée), Acte 3 (match‑ups punitifs), Boss final (check de build + ressources restantes).
- **Taux de victoire cible** : 35–45% après 10 runs.

---

## 8) Meta‑progression (déblocages)
- **Trophées** au score ≥ palier (S, A, B). Chaque palier débloque **3–6 nouvelles cartes** dans le **pool initial** des runs suivantes.
- **Arbres d’écologie** : accomplir un haut‑fait d’un biome (ex : tuer le Boss Volcan sans Vol) ajoute des **variantes** au pool du biome.
- **Pas de statistiques persistantes** (pas de +HP à vie) : uniquement **diversification**.

---

## 9) Raretés & budgets de stats
- **Commune (C)** — Budget ~ 4–5 points (ATQ + DUR + (Vitesse-1)). Traits simples.
- **Inhabituelle (U)** — Budget ~ 6–7. 1 mot-clé fort ou petite synergie.
- **Rare (R)** — Budget ~ 8–9. Mot-clé fort + petit drawback.
- **Épique (E)** — Budget ~ 10–11. Mécanique unique, contrainte lourde.
- **Légendaire (L)** — Budget ~ 12–13. Signature de biome, souvent **niche**.

`Vitesse` pèse léger : (Vitesse–1) compte dans le budget.

---

## 10) Biomes (écologie & boss)
1. **Forêt Humide** — Poison, Tirailleur, Garde. **Boss** : *Reine Myrmide*, pond des renforts.
2. **Dunes Cramoisies** — Brûlure, Percée. **Boss** : *Ver de Feu Ancestral*, crache lave.
3. **Falaises & Brumes** — Vol, Bond, Éthéré. **Boss** : *Roc‑Spectre*, divise sa présence.
4. **Fleuve Obscur** — Saignement, Carapace. **Boss** : *Silure Mnémonique*, renvoie les altérations.
5. **Volcan Noir** — Brûlure + Terrain Lave. **Boss** : *Tyran Pyroclaste*.
6. **Ruines Arcanes** — Malédiction, Érosion. **Boss** : *Bibliophage*, consomme vos traits.

---

## 11) 100 cartes (concepts complets)
*Format :* **Nom** (Biome, Rareté) — **Coût** | **ATQ/DUR/Vit.** — Traits/Capacité — *Hook / note d’équilibrage*.

### Forêt Humide
1. **Grenouille Épineuse** (C) — 1 | 1/3/2 — Tirailleur — *Punition d’invocations.*
2. **Mygale d’Azur** (C) — 1 | 1/4/1 — Venin 1 (à l’attaque) — *Attrition lente.*
3. **Sanglier Lierre** (C) — 1 | 2/3/1 — Garde — *Front cheap.*
4. **Serpent des Joncs** (U) — 1 | 2/2/3 — Bond — *Pickoff rapide.*
5. **Mante Prédatrice** (U) — 2 | 3/3/2 — Percée — *Contourne boucliers.*
6. **Dryade Veilleuse** (R) — 2 | 2/5/1 — Au déploiement : donne **Bouclier (1)** à l’allié arrière — *Protection long terme.*
7. **Crapaud Toxique** (R) — 2 | 1/5/1 — À chaque coup subi : applique **Venin 1** à l’attaquant — *Zone de danger.*
8. **Avaleur de Graines** (E) — 2 | 3/4/2 — Si tue : pond un **Œuf** (main) — *Récupère du capital sans soigner.*
9. **Liane Spectrale** (E) — 2 | 2/4/2 — Éthéré ; à l’attaque : **Malédiction** — *Tempo et affaiblissement.*
10. **Ancien Cerf‑Racines** (L) — 3 | 4/6/2 — Garde ; les ennemis avec Venin perdent **Vitesse** (min 1) — *Synergie poison/tempo.*

### Dunes Cramoisies
11. **Fennec Solaire** (C) — 1 | 2/2/3 — Vitesse 3 — *Initiative haute.*
12. **Scorpion des Braises** (C) — 1 | 1/3/2 — À l’attaque : **Brûlure 1** — *Attrition feu.*
13. **Coléoptère Béliers** (C) — 1 | 2/3/1 — Carapace (1) — *Mitige une claque.*
14. **Couleuvre Mirage** (U) — 1 | 2/2/3 — Bond ; si cible protégée : +1 ATQ — *Chasseur de boucliers.*
15. **Hyène Rieuse** (U) — 2 | 3/3/2 — Si l’ennemi est **Brûlé** : +1 ATQ — *Combo feu.*
16. **Traque‑Sable** (R) — 2 | 3/4/2 — Percée ; ignore **Garde** — *Briseur de lignes.*
17. **Dromadaire d’Obsidienne** (R) — 2 | 2/6/1 — À la fin de combat : **Brûlure 1** (auto) — *Puissant mais s’use.*
18. **Sphinx Érodant** (E) — 3 | 3/5/2 — À la fin de chaque **nœud** : inflige **Érosion** à la cible frappée ce combat — *Neige.*
19. **Phénix de Sel** (E) — 2 | 4/2/3 — Si détruit : donne **Brûlure 2** à l’assaillant — *Échange désespéré.*
20. **Ver de Feu Juvenile** (L) — 3 | 5/4/2 — Terrain Lave : +1 ATQ ; à l’attaque : **Brûlure 1** — *Signature biome.*

### Falaises & Brumes
21. **Goéland Filou** (C) — 1 | 1/3/3 — Vol ; Tirailleur — *Punition d’invocs.*
22. **Chauve‑Souris Écho** (C) — 1 | 2/2/3 — Éthéré — *Intouchable CAC.*
23. **Ronge‑Nuee** (C) — 1 | 2/3/1 — Si attaque arrière : +1 ATQ — *Incite Percée/Bond.*
24. **Harrier Gris** (U) — 2 | 3/3/3 — Vol ; Bond — *Sniper mobile.*
25. **Roc Menaçant** (U) — 2 | 3/4/1 — Si Garde adverse déclenche : +1 ATQ permanent (max +2) — *Anti‑tanks.*
26. **Aiguilleur de Brume** (R) — 2 | 2/4/2 — Au déploiement : **Bouclier (1)** à toute la ligne — *Macro‑défense.*
27. **Spectre de Cime** (R) — 2 | 3/3/2 — Éthéré ; à l’attaque : **Malédiction** — *Tempo affaiblissant.*
28. **Fauche‑Vent** (E) — 2 | 4/3/3 — Percée ; si tue arrière : gagne **Bouclier (1)** — *Snowball maîtrisé.*
29. **Grand‑Duc Ancillaire** (E) — 2 | 2/5/2 — Tant qu’il a Bouclier : **intercepte** aussi la seconde attaque — *Super Garde conditionnel.*
30. **Roc‑Spectre** (L) — 3 | 4/6/2 — À l’arrivée : **se scinde** en deux 2/3/2 Éthérés (perd 1 DUR à chaque nœud) — *Puzzle d’attrition.*

### Fleuve Obscur
31. **Piranha Strié** (C) — 1 | 2/2/3 — Saignement 1 (sur soi à l’attaque) — *Glass‑cannon dégressif.*
32. **Lamproie** (C) — 1 | 1/4/1 — À l’attaque : **Saignement 1** (ennemi) — *Transfert d’usure.*
33. **Tortue de Vase** (C) — 1 | 1/5/1 — Carapace (1) — *Mur vivant.*
34. **Silure Noir** (U) — 2 | 3/3/1 — Si la cible saigne : +1 ATQ — *Synergie saignement.*
35. **Brochet Fulminant** (U) — 2 | 4/2/3 — Si Bouclier adverse : +1 ATQ — *Anti‑bouclier.*
36. **Crabe Longbras** (R) — 2 | 2/6/1 — Garde ; quand il intercepte : **-1 ATQ** de l’assaillant (temporaire combat) — *Anti‑burst.*
37. **Nixe Murmurante** (R) — 2 | 2/3/2 — Éthéré ; au début de combat : **Malédiction** sur l’ennemi le plus rapide — *Frein d’initiative.*
38. **Anguille Nécrose** (E) — 2 | 3/4/2 — À chaque attaque subie : **Fracture** l’assaillant — *Anti‑carry.*
39. **Hydre Pâle** (E) — 3 | 4/4/2 — Quand elle détruit : invoque **Tête Pâle** 1/1/2 (max 2) — *Élargit la présence.*
40. **Silure Mnémonique** (L) — 3 | 3/7/1 — Au **tour 1** : renvoie **une** altération subie à l’ennemi qui l’a appliquée — *Contre limité.*

### Volcan Noir
41. **Gekko Fumarole** (C) — 1 | 2/2/3 — Terrain Lave : **Bouclier (1)** — *Adaptatif.*
42. **Molosse Cendreux** (C) — 1 | 2/3/2 — À l’attaque : **Brûlure 1** — *Standard feu.*
43. **Iguane Obsidien** (C) — 1 | 1/4/1 — Carapace (1) — *Mur feu.*
44. **Crapaud Fuligineux** (U) — 1 | 3/2/2 — Si l’ennemi est Brûlé : **Percée** — *Combo feu percée.*
45. **Salamandre Sombre** (U) — 2 | 2/4/2 — Tant qu’elle a Bouclier : +1 ATQ — *Timing.*
46. **Chacal Vitrifié** (R) — 2 | 3/4/2 — À la fin de combat : **Brûlure 1** (auto) — *Puissant à usure.*
47. **Roche‑Vive** (R) — 2 | 2/6/1 — Au déploiement : **Bascule terrain** en Lave pour ce combat — *Altère le plan.*
48. **Tyran Pyroclaste** (E) — 3 | 5/5/1 — Chaque tour : crée **Fissure** (ennemi avant reçoit Brûlure 1) — *Win condition feu.*
49. **Lave‑Serre** (E) — 2 | 4/3/3 — Si tue : **Érosion** sur la ligne ennemie — *Punition scaling.*
50. **Dragon Cendré** (L) — 3 | 4/6/2 — Vol ; fin de combat : **Brûlure 1** à un ennemi aléatoire restant — *Propagation lente.*

### Ruines Arcanes
51. **Rat des Cryptes** (C) — 1 | 2/2/2 — Vitesse 2 ; Tirailleur — *Flex.*
52. **Gargouille Fissurée** (C) — 1 | 1/4/1 — À l’attaque : **Malédiction** — *Frein.*
53. **Spectre Archiviste** (C) — 1 | 1/3/2 — Éthéré ; si cible déjà maudite : +1 ATQ — *Synergie.*
54. **Hibou Runique** (U) — 2 | 2/3/3 — Vol ; au déploiement : **Bouclier (1)** à un allié — *Tempo.*
55. **Golem Érodé** (U) — 2 | 3/4/1 — À l’attaque : **Érosion** — *Usure hors combat.*
56. **Vermine des Glyphes** (R) — 2 | 3/3/2 — Si l’ennemi porte déjà 2+ altérations : +1 ATQ — *Build enabling.*
57. **Bibliophage** (R) — 2 | 2/5/1 — Au tour 1 : **désactive** un mot‑clé ennemi (aléatoire) ce combat — *Tech.*
58. **Scribe Délié** (E) — 2 | 4/3/2 — Éthéré ; quand il tue : applique **Malédiction** en chaîne à la ligne — *Spread.*
59. **Ankou Mineur** (E) — 3 | 3/5/2 — Les invocations ennemies arrivent avec **-1 DUR** — *Anti-swarm.*
60. **Archi‑Sphinx** (L) — 3 | 4/6/2 — Tant qu’il est en jeu : les **Boucliers** coûtent +1 à l’ennemi (Marchand/Événements) — *Pression macro.*

### Neutres (accessible à tous biomes)
61. **Moineau Hargneux** (C) — 0 | 1/1/3 — Vol ; Tirailleur — *Filler agressif.*
62. **Rat Éclaireur** (C) — 0 | 1/2/3 — Vitesse 3 ; meurt facilement — *Tempo micro.*
63. **Chien Errant** (C) — 1 | 2/2/2 — Bond — *Presse la faiblesse.*
64. **Crabe de Rivage** (C) — 1 | 1/3/1 — Carapace (1) — *Mur low‑cost.*
65. **Renarde des Rues** (U) — 1 | 2/3/2 — Si joue en premier ce tour : +1 ATQ — *Initiative.*
66. **Hérisson** (U) — 1 | 1/4/1 — À chaque coup subi : inflige 1 à l’assaillant — *Disuasif.*
67. **Loup Solitaire** (R) — 2 | 3/3/2 — +1 ATQ s’il est **seul** sur sa ligne — *Minimalisme.*
68. **Corbeau de Carogne** (R) — 2 | 2/3/3 — Bond ; +1 ATQ contre cibles < 3 DUR — *Finisher.*
69. **Ursidé Hivernal** (E) — 3 | 4/5/1 — Garde ; si subit >1 dégât en un coup : **Fracture** l’assaillant — *Anti burst.*
70. **Chimère Naissante** (L) — 3 | 5/4/2 — Au déploiement : **-1 DUR** à elle‑même et **Bouclier (1)** à tous les alliés — *Agression sacrificielle.*

### Variantes de biome (pool débloquable)
71. **Myrmide Porte‑couvee** (U, Forêt) — 1 | 1/4/2 — Fin de combat : ajoute **Œuf** (pioche) — *Économie longue.*
72. **Boa Stranguleur** (R, Forêt) — 2 | 3/4/1 — À l’attaque : **Saignement 1** — *Trans‑biome.*
73. **Caracal de Feu** (R, Dunes) — 2 | 4/3/2 — Si Brûlure sur la cible : +1 ATQ — *Spike.*
74. **Buse Sépulcrale** (R, Falaises) — 2 | 3/3/3 — Vol ; à la mort d’un allié : **Malédiction** sur l’assaillant — *Punition.*
75. **Brochet Cuirassé** (R, Fleuve) — 2 | 2/6/2 — Garde ; à l’interception : **Carapace (1)** — *Tank technique.*
76. **Rhéa de Cendre** (U, Volcan) — 1 | 2/2/3 — Vol ; Brûlure 1 à l’attaque — *Aérien feu.*
77. **Statue Animée** (U, Ruines) — 1 | 2/3/1 — Immobile (ne peut attaquer premier tour) ; **Bouclier (1)** — *Stall.*
78. **Fauche‑Brume** (E, Falaises) — 2 | 4/3/3 — Percée ; Éthéré — *Assassin pur.*
79. **Molosse du Styx** (E, Fleuve) — 3 | 5/4/2 — À chaque meurtre : **Malédiction** — *Carry.*
80. **Sculpture Vivante** (L, Ruines) — 3 | 4/7/1 — Tant qu’elle vit : **Érosion** à la fin de chaque combat sur un ennemi aléatoire — *Clock global.*

### Spécimens exotiques (déblocables tard)
81. **Grue Émaciée** (R) — 2 | 3/2/3 — Vol ; si l’ennemi < 2 DUR : **Percée** — *Closer précis.*
82. **Fourmilion** (U) — 1 | 2/3/1 — Piège : si attaqué premier, applique **Malédiction** — *Réactif.*
83. **Lézard Verruqueux** (C) — 1 | 1/4/1 — À la fin de combat : **Venin 1** (auto) — *S’use.*
84. **Araignée Fileuse** (U) — 1 | 1/3/2 — Au déploiement : **Bouclier (1)** à un allié aléatoire — *Support.*
85. **Cerbère Poussière** (E) — 3 | 4/5/2 — À chaque nouvelle **vague** : +1 ATQ (combat) — *Scaling combat.*
86. **Bison des Falaises** (R) — 2 | 3/5/1 — Garde ; Percée si attaqué ce tour — *Contre‑charge.*
87. **Aulne Ancestral** (E) — 2 | 2/7/1 — Tant qu’il vit : ennemis **-1 Vitesse** (min 1) — *Terrain vivant.*
88. **Renard Polaire** (U) — 1 | 2/3/2 — Si la main ≤2 cartes : +1 ATQ — *Low‑hand.*
89. **Scarabée Doré** (R) — 2 | 2/4/2 — Au déploiement : gagne **Bouclier (2)** si vous avez ≤2 Boucliers en réserve — *Économie défensive.*
90. **Sphinx de Givre** (L) — 3 | 4/6/2 — Au tour 1 : **Malédiction** et **Érosion** sur la cible la plus forte — *Pression double.*

### Créatures des profondeurs & ombres
91. **Truite Albinos** (C) — 1 | 2/2/2 — Vitesse 2 ; si terrain Fleuve : **Bouclier (1)** — *Adaptation.*
92. **Murène Nerveuse** (U) — 1 | 3/2/3 — Bond ; si l’ennemi a Bouclier : **Brûlure 1** — *Anti‑bouclier agressif.*
93. **Goule Chitineuse** (R) — 2 | 3/4/2 — Si tue : applique **Saignement 1** sur la prochaine cible attaquée — *Carry saignement.*
94. **Abeille Royale** (R) — 2 | 2/3/3 — Tirailleur ; alliés **+1 Vitesse** ce tour-ci — *Hâte limitée.*
95. **Papillon Nocturne** (U) — 1 | 2/2/3 — Éthéré ; si ennemi **Maudit** : +1 ATQ — *Combo ruines.*
96. **Carcajou** (R) — 2 | 4/3/2 — Si blesse un ennemi < 3 DUR : **Fracture** — *Brise‑pattes.*
97. **Alouette de Cendre** (C) — 1 | 1/3/3 — Vol ; si terrain Lave : +1 ATQ — *Synergie terrain.*
98. **Yéti Fuligineux** (E) — 3 | 4/6/1 — Au début de chaque combat : **Brûlure 1** à l’ennemi en face — *Pression frontale.*
99. **Néréide d’Onyx** (E) — 2 | 3/4/2 — Éthéré ; fin de combat : **Saignement 1** à l’ennemi ayant le plus de DUR — *Tick ciblé.*
100. **Loup des Ruines** (L) — 3 | 5/5/2 — Tant qu’il vit : vos attaques appliquent **Malédiction** si la cible a déjà une altération — *Synergie globale.*

---

## 12) Archetypes & match‑ups
- **Feu Percée (Dunes/Volcan)** bat **Tortue/Garde** mais perd contre **Carapace/Fracture**.
- **Poison & Érosion (Forêt/Ruines)** bat **Vol/Éthéré** dans la durée, mais perd contre **Burst court**.
- **Saignement (Fleuve)** outscale les **boucliers** (car plusieurs impacts) mais se **suicide** si mal piloté.
- **Éthéré/Vitesse (Falaises)** bat **Lourd/Garde**, perd contre **Tirailleur** et **Hâte ennemie**.

**Forecast de combat type** (équilibrage cible) :
- TTK moyen d’une créature 3/4 sans altérations exposée à 3 ATQ/ tour ≈ 2 combats.
- Paquets « poison » visent la **compression** : 1 Venin par cible → 3–4 dégâts garantis sur la run.
- Paquets « feu » visent **l’étranglement** post‑combat (Brûlure) → avantage temporel si on gagne vite.

---

## 13) Systèmes d’équilibrage & simulateur
**Budget** : chaque carte a un coût de budget (ATQ + DUR + (Vit−1) + poids traits). Les traits coûtent :
- Bouclier (1) = +1 ; Éthéré = +1 ; Vol = +0.5 ; Garde = +0.5 ; Percée = +1 ; Bond = +1 ; Carapace (1) = +1 ; Tirailleur = +0.5.
- Triggers d’altération à l’attaque = +0.5 à +1 selon force (Brûlure/Venin/Saignement = +0.75 de base).

**Cibles** :
- Deck initial 12 cartes (10 C, 2 U) → DPS effectif ≈ 5–7 par tour ; Présence ≈ 35–42 DUR.
- Élite Acte 1 : Présence 28–32 ; Acte 2 : 40–46 ; Acte 3 : 52–60.

**Simulateur (pseudo)** :
```
seed RNG
for each battle:
  init lines, initiative by speed
  for turn in 1..8:
    for side in order(speed desc, tie random):
      pick target by rules (front/back, bond, percée)
      apply damage -> if shield>0: shield-- else target.DUR-=ATQ
      apply on-hit effects
      check deaths
  end combat triggers (brûlure, saignement auto, etc.)
  persist states into deck
```

---

## 14) IA ennemie
- **Priorité** : focus la **carte la plus intacte** (max DUR) pour maximiser attrition ; exceptions : si **Garde**, si **Éthéré**, si **Bond**.
- **Heuristiques** : préserver les effets (poison/fire apply early), choisir lanes avec moins de boucliers.
- **Boss** : scripts simples (tours clés avec **double action** ou terrain modifié).

---

## 15) UX / UI
- **Board** 2×3 par camp (avant/arrière). Drag‑and‑drop des cartes.
- **Pictos** clairs : altérations en jetons, **compteurs** numériques persistants.
- **Journal** discret (colonne) : « La Mygale d’Azur applique Venin 1 → Grenouille Épineuse ».
- **Carte** nodale type « ceinture » (choix à 2–3 embranchements).
- **Temps** : animations rapides (<600 ms), skip possible.

---

## 16) Implémentation technique (Python)
**Stack** : `Python 3.11+`, `pygame-ce` (ou `pyglet`), `pydantic` pour les datas, `dataclasses`, `numpy` pour le simulateur, `pytest`.

**Architecture**
- `core/` : moteur de combat (`entities.py`, `effects.py`, `keywords.py`, `resolver.py`).
- `data/` : JSON des cartes, nœuds, tables de craft.
- `run/` : gestion de run, map, loot, seed.
- `ui/` : scènes pygame, composants (main, board, shop, map).
- `assets/` : cartes (images PNG/SVG), SFX.

**Modèle de données (pydantic)**
```json
{
  "id": "forest_spine_frog",
  "name": "Grenouille Épineuse",
  "biome": "FORET",
  "rarity": "C",
  "cost": 1,
  "atk": 1,
  "dur": 3,
  "spd": 2,
  "keywords": ["TIRAILLEUR"],
  "on_attack": [{"apply": "VENIN", "value": 0}],
  "on_deploy": [],
  "notes": "Punition d'invocations"
}
```

**RNG** : `random.Random(seed)` centralisé ; tous les tirages via un **service** (reproductibilité, replays).

**Persistance** : états des cartes sérialisés (DUR restants, altérations cumulées). **Jamais de heal ni purge.**

**Tests** :
- Unitaire : mots‑clés, altés permanentes.
- Property‑based : simulateur (Hypothesis) pour détecter soft‑locks.
- Scénarios : 1000 combats auto → vérifier TTK moyens et taux de victoire.

**Performance** : 60 FPS cible ; batch update des effets ; assets vectoriels optionnels.

---

## 17) Contenu & pipeline d’illustrations (Art Bible)
**Direction** : **encre noire + aplats colorés**, silhouette lisible, fond minimal. Format carte : 512×704 px, safe‑zone texte basse.

**Prompt générique (IA)** :
> *A stylized creature illustration, ink line art with cel‑shaded flats, strong silhouette, minimal background, centered composition, dynamic pose, trading card art, high contrast, 2D, crisp edges, professional concept art.*

**Variantes par biome** :
- Forêt : palette verts/mousses, motifs de lianes.
- Dunes : ocres/rouges, chaleur vibrante.
- Falaises : gris/bleus froids, brume.
- Fleuve : bleus profonds, reflets.
- Volcan : noirs/rouges, cendres.
- Ruines : violets/dorés, glyphes.

**Par carte** : ajouter le nom FR + 2–3 attributs visuels clés (ex. *Mygale d’Azur : large tarantula, azure hairs, dew drops*). Voir **Annexe B** pour 100 prompts détaillés.

**Export** : PNG 512×704, nommage `id.png`. **Pas de texte dans l’image** (UI l’ajoute).

---

## 18) Calendrier & coûts (indicatif)
- **Semaine 1–2** : prototype combat + 30 cartes + map basique + simulateur.
- **Semaine 3–4** : 100 cartes, 6 biomes, 6 boss, événements, marchand, alchimie.
- **Semaine 5** : polish UX, art passe 1 (auto‑généré), SFX.
- **Semaine 6** : équilibrages via simulateur, QA, release alpha.

Équipe minimale : 1 dev Python, 1 GD (ici), 1 tech‑artist (pipeline IA), QA part‑time.

---

## 19) Monétisation & positionnement
- **Premium indé** (10–15€) ; rejouabilité forte.
- **DLC gratuits** : nouveaux biomes/variantes. **Pas de gacha/p2w.**

---

## 20) Risques & atténuations
- **Snowball négatif** (attrition trop dure) → plus de **Boucliers** en loot, Œufs plus fréquents en Acte 3.
- **Complexité des altés** → UI pédagogique avec **tooltips persistants**.
- **Répétitivité** → tables d’événements contextuelles au biome.

---

## 21) Localisation & accessibilité
- Termes courts et cohérents (Venin, Brûlure…).
- Options : **vitesse d’anim** (x1/x2), **dyslexie‑friendly font**, **contraste élevé**.

---

## 22) Annexes

### Annexe A — Ex. JSON complet d’une carte
```json
{
  "id": "dunes_scorpio_ember",
  "name": "Scorpion des Braises",
  "biome": "DUNES",
  "rarity": "C",
  "cost": 1,
  "atk": 1,
  "dur": 3,
  "spd": 2,
  "keywords": [],
  "on_attack": [{"apply": "BRULURE", "value": 1}],
  "on_hit": [],
  "on_deploy": [],
  "on_kill": [],
  "persistent_effects": [],
  "notes": "Attrition feu standard"
}
```

### Annexe B — Prompts d’illustrations (100)
*(format : Nom FR — prompt EN court à concaténer au prompt générique ; palettes par biome ; no text)*

**Prompt générique à utiliser pour toutes les cartes :**
> *Creature trading card illustration, ink line art with cel-shaded flats, strong silhouette, minimal background, centered composition, dynamic pose, professional 2D concept art, crisp edges, no text, no typography.*

1. Grenouille Épineuse — *forest palette greens; spiky forest frog, mossy skin, dew drops, alert eyes*
2. Mygale d’Azur — *forest palette greens; large tarantula, azure hairs, moisture on hairs, leaf litter*
3. Sanglier Lierre — *forest palette greens; boar wrapped in ivy, heavy tusks, earth splashes*
4. Serpent des Joncs — *forest palette greens; slender grass snake in reeds, glossy scales, coiled*
5. Mante Prédatrice — *forest palette greens; mantis mid‑strike, serrated limbs, sharp silhouette*
6. Dryade Veilleuse — *forest palette greens; wood nymph guardian, bark texture, gentle glow eyes*
7. Crapaud Toxique — *forest palette greens; warty toad, visible toxic glands, shimmering ooze*
8. Avaleur de Graines — *forest palette greens; small rodent pouching seeds, puffed cheek, nimble paws*
9. Liane Spectrale — *forest palette greens; ghostly vine spirit, semi‑transparent tendrils*
10. Ancien Cerf‑Racines — *forest palette greens; stag with root antlers, moss draping, regal stance*
11. Fennec Solaire — *dunes palette ochres/reds; desert fennec, big ears, heat shimmer*
12. Scorpion des Braises — *dunes palette; ember‑glowing scorpion, heated pincers, sparks*
13. Coléoptère Béliers — *dunes palette; heavy rhinoceros beetle, ramming stance, dust trail*
14. Couleuvre Mirage — *dunes palette; mirage‑like sand snake, wavering heat, shimmering scales*
15. Hyène Rieuse — *dunes palette; laughing hyena, bared teeth, desert wind*
16. Traque‑Sable — *dunes palette; sleek desert predator, low sprint, piercing gaze*
17. Dromadaire d’Obsidienne — *dunes palette; black obsidian‑hued camel, sturdy, heat haze*
18. Sphinx Érodant — *dunes palette; weathered sphinx statue with life, sand‑worn glyphs*
19. Phénix de Sel — *dunes palette; crystalline salt phoenix, fragmented wings, rising*
20. Ver de Feu Juvénile — *dunes/volcan palette; young fire worm, molten cracks, burrowing*
21. Goéland Filou — *cliffs/brume palette grays/blues; sly seagull mid‑dive, coastal spray*
22. Chauve‑Souris Écho — *cliffs/brume palette; ethereal bat, translucent membranes, echo waves*
23. Ronge‑Nuée — *cliffs/brume palette; swarmy cliff rodents, collective shape, motion blur*
24. Harrier Gris — *cliffs/brume palette; grey harrier hawk, swift wings, stoop pose*
25. Roc Menaçant — *cliffs/brume palette; massive rock bird, looming presence, heavy shadow*
26. Aiguilleur de Brume — *cliffs/brume palette; mist‑weaving bird, guiding currents, wing trails*
27. Spectre de Cime — *cliffs/brume palette; mountain peak ghost, thin aura, hollow eyes*
28. Fauche‑Vent — *cliffs/brume palette; wind‑scythe raptor, sweeping arc, feathers slicing air*
29. Grand‑Duc Ancillaire — *cliffs/brume palette; grand owl sentinel, protective stance*
30. Roc‑Spectre — *cliffs/brume palette; spectral roc splitting form, twin silhouettes*
31. Piranha Strié — *river palette deep blues; striped piranha, sharp teeth, water splash*
32. Lamproie — *river palette; lamprey with circular maw, latch posture*
33. Tortue de Vase — *river palette; mud turtle, thick shell, low profile*
34. Silure Noir — *river palette; whiskered catfish, lurking in dark water*
35. Brochet Fulminant — *river palette; pike lunging, electricity hint, streamlined*
36. Crabe Longbras — *river palette; long‑armed crab, wide stance, armored*
37. Nixe Murmurante — *river palette; whispering water spirit, ripples around*
38. Anguille Nécrose — *river palette; decayed eel, necrotic patches, eerie glow*
39. Hydre Pâle — *river palette; pale hydra with multiple heads, subtle menace*
40. Silure Mnémonique — *river palette; ancient catfish with runic scars, reflective eyes*
41. Gekko Fumarole — *volcano palette blacks/reds; fumarole gecko, steam plumes, ash specks*
42. Molosse Cendreux — *volcano palette; ashen hound, ember eyes, cinder trail*
43. Iguane Obsidien — *volcano palette; obsidian‑skinned iguana, jagged scales*
44. Crapaud Fuligineux — *volcano palette; sooty toad, ember warts, faint smoke*
45. Salamandre Sombre — *volcano palette; dark salamander, glowing underbelly, guarded pose*
46. Chacal Vitrifié — *volcano palette; glassy‑fur jackal, vitrified sheen, desert night*
47. Roche‑Vive — *volcano palette; living rock boulder, cracking heat veins*
48. Tyran Pyroclaste — *volcano palette; pyroclastic tyrant beast, magma veins, crown of fire*
49. Lave‑Serre — *volcano palette; lava‑talon raptor, molten claws, fast swoop*
50. Dragon Cendré — *volcano palette; ashen dragon, smoke wings, ember rain*
51. Rat des Cryptes — *ruins palette violets/golds; crypt rat, runic debris, wary stance*
52. Gargouille Fissurée — *ruins palette; cracked gargoyle awakening, dust fall*
53. Spectre Archiviste — *ruins palette; librarian ghost, tattered robe, floating runes*
54. Hibou Runique — *ruins palette; rune‑etched owl, glimmering sigils on feathers*
55. Golem Érodé — *ruins palette; eroded golem, sand‑worn edges, slow step*
56. Vermine des Glyphes — *ruins palette; glyph‑infested vermin, markings glow*
57. Bibliophage — *ruins palette; book‑devouring creature, pages swirling*
58. Scribe Délié — *ruins palette; unbound scribe spirit, quill of light, paper stream*
59. Ankou Mineur — *ruins palette; minor reaper, small scythe, lantern glow*
60. Archi‑Sphinx — *ruins palette; majestic sphinx, ornate headdress, riddle aura*
61. Moineau Hargneux — *neutral palette; scrappy sparrow, mid‑peck, tiny but fierce*
62. Rat Éclaireur — *neutral palette; scout rat, inquisitive whiskers, quick paws*
63. Chien Errant — *neutral palette; stray dog, lean, alert ears*
64. Crabe de Rivage — *neutral palette; shoreline crab, wet shell, simple backdrop*
65. Renarde des Rues — *neutral palette; street fox, sly grin, urban hint*
66. Hérisson — *neutral palette; hedgehog puffed spines, defensive ball pose*
67. Loup Solitaire — *neutral palette; lone wolf, moon hint, tense stance*
68. Corbeau de Carogne — *neutral palette; carrion crow, keen eyes, scavenger vibes*
69. Ursidé Hivernal — *neutral palette; winter bear, frosty breath, bulky*
70. Chimère Naissante — *neutral palette; nascent chimera, mixed animal features, unstable glow*
71. Myrmide Porte‑couvée — *forest palette; ant warrior carrying larval pouch*
72. Boa Stranguleur — *forest palette; constrictor snake, muscular coils*
73. Caracal de Feu — *dunes/volcano palette; fire‑tinged caracal, ear tufts, sprint*
74. Buse Sépulcrale — *cliffs/ruins palette; sepulchral hawk, graveyard mist*
75. Brochet Cuirassé — *river palette; armored pike, plated scales*
76. Rhéa de Cendre — *volcano palette; ash‑dusted rhea bird, long legs, sprint*
77. Statue Animée — *ruins palette; animated statue, glowing core, heavy weight*
78. Fauche‑Brume — *cliffs palette; mist‑reaper, ethereal scythe, swift*
79. Molosse du Styx — *river/ruins palette; underworld hound, twin heads hinted, shadow ripples*
80. Sculpture Vivante — *ruins palette; living sculpture, golden fractures, imposing*
81. Grue Émaciée — *neutral/cold palette; emaciated crane, long legs, elegant sorrow*
82. Fourmilion — *dunes palette; antlion pit, hidden jaws, sand swirl*
83. Lézard Verruqueux — *neutral palette; warty lizard, rough skin, grounded*
84. Araignée Fileuse — *forest palette; web‑spinner spider, silk threads gleaming*
85. Cerbère Poussière — *ruins/dunes palette; dusty cerberus, triple shadow heads*
86. Bison des Falaises — *cliffs palette; cliff bison, massive horns, rock chips*
87. Aulne Ancestral — *forest palette; ancient alder tree‑creature, heavy canopy*
88. Renard Polaire — *neutral/cold palette; arctic fox, snow flecks, nimble*
89. Scarabée Doré — *neutral/ruins palette; golden scarab, metallic sheen*
90. Sphinx de Givre — *ruins/cold palette; frost sphinx, icy patterns, calm menace*
91. Truite Albinos — *river/cold palette; albino trout, pale scales, water ripple*
92. Murène Nerveuse — *river palette; nervous moray eel, sharp teeth, darting*
93. Goule Chitineuse — *ruins palette; chitinous ghoul, insect carapace hints*
94. Abeille Royale — *forest/neutral palette; royal bee, crown‑like fuzz, mid‑flight*
95. Papillon Nocturne — *ruins/cliffs palette; nocturnal moth, powdery wings, dim glow*
96. Carcajou — *neutral/cold palette; wolverine, low growl, muscular*
97. Alouette de Cendre — *volcano/cliffs palette; ash lark, soot‑tipped wings*
98. Yéti Fuligineux — *volcano/cold palette; sooty yeti, ember sparks in fur*
99. Néréide d’Onyx — *river/ruins palette; onyx‑toned nereid, dark waters, luminous eyes*
100. Loup des Ruines — *ruins palette; ruin‑bound wolf, glyph scars, poised*

### Annexe C — Pseudocode combat (détaillé) — Pseudocode combat (détaillé)
```
class Creature:
  atk, dur, spd
  shields
  statuses = {venin:0, brulure:0, saign:0, fracture:0, malediction:0, erosion:0}

class Resolver:
  def start_combat(self):
    for c in all_creatures: c.spd = max(1, c.spd - (1 if c.has('MALEDICTION') else 0))
  def attack(self, attacker, target):
    if target.shields>0: target.shields-=1
    else: target.dur -= attacker.atk
    self.apply_onhit(attacker, target)
  def end_combat(self):
    for c in all_creatures:
      c.dur -= c.statuses['brulure']
      # venin tickera au début du prochain combat
```

---

## 23) Conclusion
**Écorces & Échos** propose une identité forte : **la peur du coup de trop**. L’attrition n’est pas une punition gratuite, c’est un choix : frapper vite, esquiver, ou accepter la cicatrice pour gagner une position. Runs courtes, décisions lourdes, méta propre.

Prêt pour un **prototype Python** : datas normalisées, simulateur d’équilibrage, 100 cartes jouables, pipeline d’art prêt à l’automatisation.

