import pygame
from typing import Optional, Tuple
from engine.core.state import GameState, BOARD_COLS
from engine.core.combat import resolve_combat
from engine.models.card import Unit, CardData
from engine.ui.colors import *
from engine.ui.layout import WINDOW_W, WINDOW_H, board_rects, hand_area
from engine.ui.widgets import draw_slot, draw_card, draw_pill, draw_button

class GameUI:
    def __init__(self, gs: GameState, stage: int, is_boss: bool):
        pygame.init()
        self.gs = gs
        self.stage = stage
        self.is_boss = is_boss
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        cap = f'Combat {stage}{" — Boss" if is_boss else ""}'
        pygame.display.set_caption(cap)
        self.clock = pygame.time.Clock()
        self.rects = board_rects()
        self.hand_rect = hand_area()
        self.dragging: Optional[Tuple[int, pygame.Rect]] = None  # (hand_index, rect)
        self.end_turn_btn = pygame.Rect(WINDOW_W-160, 30, 130, 40)
        self.continue_btn = pygame.Rect(WINDOW_W//2 - 110, 120, 220, 50)
        self.running = True
        self.outcome: Optional[str] = None  # 'win' or 'loss'

    def run(self):
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(60)
        return self.outcome

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.outcome = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if not self.gs.is_over():
                    # start drag from hand
                    hx, hy, hw, hh = self.hand_rect
                    if hy <= my <= hy+hh:
                        idx, card_rect = self.hand_card_at(mx, my)
                        if idx is not None:
                            self.dragging = (idx, card_rect.move(0,0))
                    if self.end_turn_btn.collidepoint(mx, my):
                        self.end_turn()
                else:
                    # game over overlay: continue button
                    if self.continue_btn.collidepoint(mx, my):
                        w = self.gs.winner()
                        self.outcome = "win" if w == "player" else "loss"
                        self.running = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    mx, my = event.pos
                    slot_idx = self.player_slot_at(mx, my)
                    if slot_idx is not None and self.gs.player.board[slot_idx] is None:
                        card = self.gs.player.hand.pop(self.dragging[0])
                        self.gs.player.board[slot_idx] = Unit(card, card.dur)
                    self.dragging = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.gs.is_over():
                    self.end_turn()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.outcome = "quit"
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                idx, rect = self.dragging
                mx, my = event.pos
                self.dragging = (idx, pygame.Rect(mx-90, my-60, rect.w, rect.h))

    def end_turn(self):
        resolve_combat(self.gs)
        self.gs.turn_index += 1
        if self.gs.player.deck:
            self.gs.draw(self.gs.player, 1)

    def render(self):
        self.screen.fill(BG)
        # board
        hover_idx = None
        mx, my = pygame.mouse.get_pos()
        if self.dragging:
            hover_idx = self.player_slot_at(mx, my)

        for i, rect in enumerate(self.rects['enemy']):
            draw_slot(self.screen, rect)
            unit = self.gs.enemy.board[i]
            if unit:
                draw_card(self.screen, rect, unit.data.name, unit.atk, unit.current_dur, unit.spd)

        for i, rect in enumerate(self.rects['player']):
            is_hover = hover_idx == i and self.gs.player.board[i] is None
            draw_slot(self.screen, rect, is_hover)
            unit = self.gs.player.board[i]
            if unit:
                draw_card(self.screen, rect, unit.data.name, unit.atk, unit.current_dur, unit.spd)

        # hand
        self.draw_hand()

        # HUD
        draw_pill(self.screen, 20, 20, f"Combat {self.stage}{' (Boss)' if self.is_boss else ''}", YELLOW if self.is_boss else BLUE)
        draw_pill(self.screen, 220, 20, f"PV Joueur {self.gs.player.hp}", GREEN if self.gs.player.hp>0 else RED)
        draw_pill(self.screen, 420, 20, f"PV Ennemi {self.gs.enemy.hp}", GREEN if self.gs.enemy.hp>0 else RED)

        # end turn button
        pygame.draw.rect(self.screen, (240,240,240), self.end_turn_btn, border_radius=10)
        pygame.draw.rect(self.screen, (60,60,60), self.end_turn_btn, width=2, border_radius=10)
        font = pygame.font.SysFont('arial', 18, bold=True)
        self.screen.blit(font.render("Fin du tour ↵", True, (20,20,20)), (self.end_turn_btn.x+16, self.end_turn_btn.y+10))

        # dragging preview
        if self.dragging:
            idx, rect = self.dragging
            card = self.gs.player.hand[idx]
            draw_card(self.screen, rect, card.name, card.atk, card.dur, card.spd, is_drag=True)

        # Game over
        if self.gs.is_over():
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            self.screen.blit(overlay, (0,0))
            msg = "Victoire" if self.gs.winner() == "player" else "Défaite"
            font2 = pygame.font.SysFont('arial', 46, bold=True)
            s = font2.render(msg, True, WHITE)
            self.screen.blit(s, (self.screen.get_width()//2 - s.get_width()//2, 60))
            # continue
            draw_button(self.screen, self.continue_btn, "Continuer")

        pygame.display.flip()

    def hand_card_at(self, mx, my):
        hx, hy, hw, hh = self.hand_rect
        if not (hy <= my <= hy+hh):
            return None, None
        gap = 16
        w, h = 150, 110
        start_x = hx + 16
        y = hy + 20
        for i, card in enumerate(self.gs.player.hand):
            rect = pygame.Rect(start_x + i*(w+gap), y, w, h)
            if rect.collidepoint(mx, my):
                return i, rect
        return None, None

    def player_slot_at(self, mx, my):
        for i, rect in enumerate(self.rects['player']):
            x,y,w,h = rect
            r = pygame.Rect(x,y,w,h)
            if r.collidepoint(mx, my):
                return i
        return None

    def draw_hand(self):
        pygame.draw.rect(self.screen, (45,50,65), self.hand_rect, border_radius=16)
        pygame.draw.rect(self.screen, (80,85,100), self.hand_rect, width=2, border_radius=16)
        hx, hy, hw, hh = self.hand_rect
        gap = 16
        w, h = 150, 110
        start_x = hx + 16
        y = hy + 20
        for i, card in enumerate(self.gs.player.hand):
            if self.dragging and self.dragging[0] == i:
                continue
            rect = (start_x + i*(w+gap), y, w, h)
            draw_card(self.screen, rect, card.name, card.atk, card.dur, card.spd)
