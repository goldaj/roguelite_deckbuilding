
import pygame
from pygame import Rect
from .components import Button, WHITE

class DeckOverlay:
    """
    Overlay d'inspection du deck et des ressources persistantes.
    Signature compatible avec l'existant: DeckOverlay(app, state).
    Le paramètre 'state' est accepté mais non requis.
    """
    def __init__(self, app, state=None):
        self.app = app
        self.visible = False
        self._panel_w = 480
        self._panel_margin = 20
        self._close_btn = Button((0,0,34,34), "✕", self.close)
        # cache simple pour le contenu
        self._entries = []

    def open(self): self.visible = True
    def close(self): self.visible = False
    def toggle(self): self.visible = not self.visible

    def handle(self, ev):
        if not self.visible: return
        # Fermer en cliquant en dehors du panneau
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            px, py, pw, ph = self._panel_rect()
            if not Rect(px, py, pw, ph).collidepoint(ev.pos):
                self.close(); return
        # Bouton ✕
        self._close_btn.handle(ev)

    def _panel_rect(self):
        w = min(self._panel_w, max(420, int(self.app.w*0.45)))
        h = min(self.app.h - 2*self._panel_margin, 680)
        x = self.app.w - w - self._panel_margin
        y = self._panel_margin
        return x, y, w, h

    def draw(self, surf):
        if not self.visible: return
        # Backdrop
        shade = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        shade.fill((0,0,0,140)); surf.blit(shade, (0,0))

        # Panel
        px, py, pw, ph = self._panel_rect()
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (22,22,30,235), (0,0,pw,ph), border_radius=16)
        pygame.draw.rect(panel, (255,255,255,40), (0,0,pw,ph), width=2, border_radius=16)

        # Header + bouton
        title = self.app.font_big.render("Deck & État persistant", True, WHITE)
        panel.blit(title, (16, 12))
        cbx, cby, cbw, cbh = pw - 16 - 34, 12, 34, 34
        self._close_btn.rect = Rect(px + cbx, py + cby, cbw, cbh)  # absolu pour la détection
        btn_visual = Rect(cbx, cby, cbw, cbh)
        pygame.draw.rect(panel, (44,48,68), btn_visual, border_radius=8)
        txt = self.app.font_small.render("✕", True, (240,240,250))
        panel.blit(txt, (cbx + (cbw - txt.get_width())//2, cby + (cbh - txt.get_height())//2))

        # Contenu
        y = 60
        state = getattr(self.app, 'state', None)
        if state:
            panel.blit(self.app.font_small.render(f"Fragments: {state.fragments} | Gènes: {state.genes}", True, (230,230,240)), (16, y)); y += 24
            panel.blit(self.app.font_small.render(f"Cartes dans le deck: {len(state.deck_blueprints)}", True, (230,230,240)), (16, y)); y += 10
            area = Rect(12, y+8, pw-24, ph - (y+20))
            pygame.draw.rect(panel, (30,30,44), area, border_radius=10)
            inner_y = area.y + 8
            bps = list(state.deck_blueprints)
            for i, bp in enumerate(bps):
                line = f"• {bp.name}  (ATQ {bp.atk}  DUR {bp.dur}  V{bp.spd} | coût {getattr(bp,'cost',1)})"
                t = self.app.font_small.render(line, True, (235,235,245))
                if inner_y + t.get_height() > area.bottom - 8:
                    more = self.app.font_small.render(f"... (+{len(bps)-i} autres)", True, (200,200,210))
                    panel.blit(more, (area.x + 10, inner_y)); break
                panel.blit(t, (area.x + 10, inner_y)); inner_y += 22

        # Blit
        surf.blit(panel, (px, py))
