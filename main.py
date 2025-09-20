
# main.py
"""Bestiaire - Roguelite Deckbuilding"""

import pygame
import pygame.freetype
import sys
import json
from pathlib import Path
from typing import Optional

from core.entities import CardDatabase, RunState, CombatState
from ui.interface import CombatScene

class BestiaireGame:
    """Classe principale du jeu"""

    def __init__(self):
        pygame.init()
        pygame.freetype.init()

        # Configuration de l'écran
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bestiaire: Écorces & Échos")

        # Police
        self.font = pygame.freetype.Font(None, 16)

        # Horloge
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        # Base de données
        self.card_db = CardDatabase()

        # État du jeu
        self.current_scene = "menu"
        self.run_state: Optional[RunState] = None

        # Scènes
        self.combat_scene = CombatScene(self.screen, self.font)

    def new_run(self):
        """Démarre une nouvelle run"""
        starter_deck = self.card_db.get_starter_deck()
        self.run_state = RunState(current_deck=starter_deck)

        # Démarrer avec un combat de test
        self.start_combat()

    def start_combat(self):
        """Lance un combat"""
        if not self.run_state:
            return

        # Créer l'état de combat
        combat_state = CombatState()
        combat_state.deck = self.run_state.current_deck.copy()

        # Ajouter quelques ennemis de test
        enemy1 = self.card_db.create_card("forest_spine_frog")
        enemy2 = self.card_db.create_card("dunes_solar_fennec")
        combat_state.enemy_field[0] = enemy1
        combat_state.enemy_field[3] = enemy2

        # Initialiser la scène de combat
        self.combat_scene.init_combat(combat_state)
        self.current_scene = "combat"

    def handle_events(self):
        """Gère les événements"""
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_scene == "combat":
                        self.current_scene = "menu"
                    else:
                        self.running = False
                elif event.key == pygame.K_n and self.current_scene == "menu":
                    self.new_run()

        # Passer les événements à la scène active
        if self.current_scene == "combat":
            self.combat_scene.update(self.dt, events)

    def update(self):
        """Met à jour le jeu"""
        pass

    def draw(self):
        """Dessine le jeu"""
        if self.current_scene == "menu":
            self.draw_menu()
        elif self.current_scene == "combat":
            self.combat_scene.draw()

        pygame.display.flip()

    def draw_menu(self):
        """Dessine le menu principal"""
        self.screen.fill((20, 20, 30))

        # Titre
        title_rect = self.font.get_rect("BESTIAIRE", size=48)
        self.font.render_to(self.screen,
                          (SCREEN_WIDTH//2 - title_rect.width//2, 150),
                          "BESTIAIRE", (200, 200, 255), size=48)

        subtitle_rect = self.font.get_rect("Écorces & Échos", size=24)
        self.font.render_to(self.screen,
                          (SCREEN_WIDTH//2 - subtitle_rect.width//2, 210),
                          "Écorces & Échos", (150, 150, 200), size=24)

        # Instructions
        self.font.render_to(self.screen,
                          (SCREEN_WIDTH//2 - 100, 350),
                          "[N] Nouvelle Run", (255, 255, 255), size=20)
        self.font.render_to(self.screen,
                          (SCREEN_WIDTH//2 - 100, 390),
                          "[ESC] Quitter", (255, 255, 255), size=20)

    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

# Point d'entrée
if __name__ == "__main__":
    game = BestiaireGame()
    game.run()