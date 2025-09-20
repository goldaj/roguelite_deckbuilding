# ui/interface.py
"""Interface graphique du jeu avec pygame"""

import pygame
import pygame.freetype
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
import math
import json

from core.entities import Card, CombatState, RunState, Biome, StatusEffect
from core.combat import CombatResolver

# Configuration graphique
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CARD_WIDTH = 90
CARD_HEIGHT = 126
FPS = 60

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
MID_GRAY = (80, 80, 80)
LIGHT_GRAY = (160, 160, 160)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
BLUE = (100, 100, 200)
GOLD = (255, 215, 0)

# Couleurs par biome
BIOME_COLORS = {
    Biome.FORET: (100, 150, 100),
    Biome.DUNES: (200, 150, 100),
    Biome.FALAISES: (150, 150, 180),
    Biome.FLEUVE: (100, 120, 180),
    Biome.VOLCAN: (180, 100, 100),
    Biome.RUINES: (150, 100, 180),
    Biome.NEUTRE: (140, 140, 140)
}

# Couleurs des status
STATUS_COLORS = {
    StatusEffect.VENIN: (100, 200, 100),
    StatusEffect.BRULURE: (255, 100, 50),
    StatusEffect.SAIGNEMENT: (200, 50, 50),
    StatusEffect.FRACTURE: (150, 150, 150),
    StatusEffect.MALEDICTION: (150, 50, 200),
    StatusEffect.EROSION: (100, 100, 50)
}

@dataclass
class CardSprite:
    """Sprite visuel d'une carte"""
    card: Card
    x: float
    y: float
    target_x: float
    target_y: float
    scale: float = 1.0
    rotation: float = 0.0
    hovering: bool = False
    selected: bool = False

    def update(self, dt: float):
        """Animation fluide vers la position cible"""
        self.x += (self.target_x - self.x) * 0.2
        self.y += (self.target_y - self.y) * 0.2

    def draw(self, screen: pygame.Surface, font: pygame.freetype.Font):
        """Dessine la carte"""
        width = int(CARD_WIDTH * self.scale)
        height = int(CARD_HEIGHT * self.scale)

        # Rectangle de base
        rect = pygame.Rect(int(self.x - width/2), int(self.y - height/2), width, height)

        # Couleur selon biome
        color = BIOME_COLORS.get(self.card.biome, MID_GRAY)
        if self.hovering:
            color = tuple(min(255, c + 30) for c in color)

        # Fond de carte
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE if self.selected else BLACK, rect, 2)

        # Nom de la carte
        name_rect = font.get_rect(self.card.name[:12], size=10)
        font.render_to(screen,
                      (rect.x + rect.width//2 - name_rect.width//2,
                       rect.y + 5),
                      self.card.name[:12], WHITE, size=10)

        # Stats
        # ATQ
        atk_color = RED if self.card.current_atk < self.card.base_atk else WHITE
        font.render_to(screen, (rect.x + 5, rect.bottom - 20),
                      f"{self.card.get_effective_atk()}", atk_color, size=14)

        # DUR
        dur_color = RED if self.card.current_dur < self.card.base_dur else WHITE
        font.render_to(screen, (rect.right - 20, rect.bottom - 20),
                      f"{self.card.current_dur}", dur_color, size=14)

        # Coût
        pygame.draw.circle(screen, BLUE, (rect.x + 15, rect.y + 15), 12)
        font.render_to(screen, (rect.x + 11, rect.y + 8),
                      str(self.card.cost), WHITE, size=14)

        # Boucliers
        if self.card.shields > 0:
            pygame.draw.circle(screen, (200, 200, 200),
                             (rect.right - 15, rect.y + 15), 10)
            font.render_to(screen, (rect.right - 19, rect.y + 9),
                          str(self.card.shields), BLACK, size=12)

        # Icônes de statuts (mini icônes en bas)
        status_x = rect.x + 5
        for status, value in self.card.permanent_statuses.items():
            if value > 0:
                color = STATUS_COLORS.get(status, WHITE)
                pygame.draw.circle(screen, color, (status_x, rect.bottom - 35), 5)
                font.render_to(screen, (status_x - 3, rect.bottom - 42),
                              str(value), WHITE, size=8)
                status_x += 12

class CombatScene:
    """Scène de combat"""

    def __init__(self, screen: pygame.Surface, font: pygame.freetype.Font):
        self.screen = screen
        self.font = font
        self.state: Optional[CombatState] = None
        self.resolver: Optional[CombatResolver] = None

        self.card_sprites: Dict[Card, CardSprite] = {}
        self.hand_sprites: List[CardSprite] = []
        self.field_sprites: List[Optional[CardSprite]] = [None] * 12

        self.selected_card: Optional[CardSprite] = None
        self.hovering_position: int = -1

        self.animation_queue: List[Dict] = []
        self.animation_timer: float = 0

    def init_combat(self, state: CombatState):
        """Initialise un nouveau combat"""
        self.state = state
        self.resolver = CombatResolver(state)
        self.resolver.start_combat()

        # Créer les sprites pour la main
        self._update_hand_sprites()

    def _update_hand_sprites(self):
        """Met à jour les sprites de la main"""
        self.hand_sprites.clear()

        hand_y = SCREEN_HEIGHT - CARD_HEIGHT//2 - 20
        spacing = min(120, (SCREEN_WIDTH - 200) // max(1, len(self.state.hand)))
        start_x = SCREEN_WIDTH // 2 - (len(self.state.hand) * spacing) // 2

        for i, card in enumerate(self.state.hand):
            sprite = CardSprite(
                card=card,
                x=start_x + i * spacing,
                y=hand_y,
                target_x=start_x + i * spacing,
                target_y=hand_y
            )
            self.hand_sprites.append(sprite)
            self.card_sprites[card] = sprite

    def update(self, dt: float, events: List[pygame.event.Event]):
        """Met à jour la scène"""
        mouse_pos = pygame.mouse.get_pos()

        # Gestion des événements
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._end_turn()

        # Hover sur les cartes
        for sprite in self.hand_sprites:
            rect = pygame.Rect(
                int(sprite.x - CARD_WIDTH//2),
                int(sprite.y - CARD_HEIGHT//2),
                CARD_WIDTH, CARD_HEIGHT
            )
            sprite.hovering = rect.collidepoint(mouse_pos)

            if sprite.hovering:
                sprite.target_y = SCREEN_HEIGHT - CARD_HEIGHT//2 - 40
                sprite.scale = 1.1
            else:
                sprite.target_y = SCREEN_HEIGHT - CARD_HEIGHT//2 - 20
                sprite.scale = 1.0

        # Animation des sprites
        for sprite in self.card_sprites.values():
            sprite.update(dt)

        # Traiter la queue d'animations
        if self.animation_queue:
            self.animation_timer += dt
            if self.animation_timer > 0.5:
                self.animation_queue.pop(0)
                self.animation_timer = 0

    def _handle_click(self, mouse_pos: Tuple[int, int]):
        """Gère les clics souris"""
        # Sélection d'une carte en main
        for sprite in self.hand_sprites:
            rect = pygame.Rect(
                int(sprite.x - CARD_WIDTH//2),
                int(sprite.y - CARD_HEIGHT//2),
                CARD_WIDTH, CARD_HEIGHT
            )
            if rect.collidepoint(mouse_pos):
                self.selected_card = sprite
                sprite.selected = True
                # Déselectionner les autres
                for other in self.hand_sprites:
                    if other != sprite:
                        other.selected = False
                return

        # Placement d'une carte sélectionnée
        if self.selected_card:
            position = self._get_board_position(mouse_pos)
            if position >= 0 and position < 6:
                if self.resolver.play_card(self.selected_card.card, position):
                    # Déplacer la carte sur le terrain
                    self.field_sprites[position] = self.selected_card
                    self.hand_sprites.remove(self.selected_card)

                    # Mettre à jour la position cible
                    board_x, board_y = self._get_board_coords(position)
                    self.selected_card.target_x = board_x
                    self.selected_card.target_y = board_y

                    self.selected_card = None
                    self._update_hand_sprites()

    def _get_board_position(self, mouse_pos: Tuple[int, int]) -> int:
        """Détermine la position sur le board selon la souris"""
        board_start_x = 350
        board_start_y = 300

        for row in range(2):
            for col in range(3):
                x = board_start_x + col * 100
                y = board_start_y + row * 100
                rect = pygame.Rect(x - 40, y - 40, 80, 80)
                if rect.collidepoint(mouse_pos):
                    return row * 3 + col
        return -1

    def _get_board_coords(self, position: int) -> Tuple[int, int]:
        """Retourne les coordonnées écran d'une position de board"""
        row = position // 3
        col = position % 3
        x = 350 + col * 100
        y = 300 + row * 100
        return x, y

    def _end_turn(self):
        """Termine le tour du joueur"""
        if self.resolver:
            self.resolver.process_turn()
            # Vérifier si le combat est terminé
            if self.state.is_combat_over() is not None:
                rewards = self.resolver.end_combat()
                # Retourner à la carte ou traiter les récompenses

    def draw(self):
        """Dessine la scène de combat"""
        self.screen.fill(DARK_GRAY)

        # Dessiner le plateau
        self._draw_board()

        # Dessiner les cartes sur le terrain
        for i, sprite in enumerate(self.field_sprites):
            if sprite:
                sprite.draw(self.screen, self.font)

        # Dessiner la main
        for sprite in self.hand_sprites:
            sprite.draw(self.screen, self.font)

        # UI d'information
        self._draw_ui()

    def _draw_board(self):
        """Dessine le plateau de jeu"""
        # Zones du joueur (bas)
        for row in range(2):
            for col in range(3):
                x = 350 + col * 100
                y = 300 + row * 100
                color = (60, 80, 60) if row == 0 else (50, 60, 70)
                pygame.draw.rect(self.screen, color,
                               pygame.Rect(x - 40, y - 40, 80, 80), 2)

        # Zones ennemies (haut)
        for row in range(2):
            for col in range(3):
                x = 350 + col * 100
                y = 100 + row * 100
                color = (80, 60, 60) if row == 1 else (70, 50, 60)
                pygame.draw.rect(self.screen, color,
                               pygame.Rect(x - 40, y - 40, 80, 80), 2)

    def _draw_ui(self):
        """Dessine l'interface utilisateur"""
        # Énergie
        energy_text = f"Énergie: {self.state.energy}/3"
        self.font.render_to(self.screen, (20, 20), energy_text, WHITE, size=18)

        # Tour
        turn_text = f"Tour {self.state.turn}"
        self.font.render_to(self.screen, (20, 50), turn_text, WHITE, size=18)

        # Présence
        player_presence = self.state.get_presence(True)
        enemy_presence = self.state.get_presence(False)

        self.font.render_to(self.screen, (20, 300),
                          f"Votre présence: {player_presence}", GREEN, size=16)
        self.font.render_to(self.screen, (20, 150),
                          f"Présence ennemie: {enemy_presence}", RED, size=16)

        # Instructions
        self.font.render_to(self.screen, (SCREEN_WIDTH - 200, 20),
                          "ESPACE: Fin de tour", LIGHT_GRAY, size=14)
