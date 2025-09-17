
import pygame
from pygame import Rect

WHITE = (245,245,255)

def clamp(x, a, b): return max(a, min(b, x))

class Button:
    def __init__(self, rect, label, on_click, skin=None):
        self.rect = Rect(rect)
        self.label = label
        self.on_click = on_click
        self.skin = skin or {}
        self.hover = False
    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos) and self.on_click:
                self.on_click()
    def draw(self, surf, font):
        if self.skin.get("button"):
            surf.blit(pygame.transform.smoothscale(self.skin["button"], self.rect.size), self.rect.topleft)
        else:
            pygame.draw.rect(surf, (54,62,92), self.rect, border_radius=12)
        col = (255,255,255) if not self.hover else (240,220,255)
        surf.blit(font.render(self.label, True, col), (self.rect.x+16, self.rect.y+12))

class Toast:
    def __init__(self, text, duration=1.7):
        self.text = text; self.ttl = duration; self.y = 40
    def update(self, dt): self.ttl -= dt; self.y = 40 + int((1.7 - self.ttl) * 6)
    def finished(self): return self.ttl <= 0
    def draw(self, surf, font, y=40):
        pane = pygame.Surface((min(740, max(220, font.size(self.text)[0] + 24)), 36), pygame.SRCALPHA)
        pygame.draw.rect(pane, (0,0,0,200), pane.get_rect(), border_radius=10)
        surf.blit(pane, (20, y))
        surf.blit(font.render(self.text, True, WHITE), (28, y+8))

class TopBar:
    def __init__(self, app, state):
        self.app = app; self.state = state; self.help = ""
    def set_help(self, text): self.help = text or ""
    def handle(self, ev): pass
    def draw(self, surf, font):
        r = Rect(0, 0, self.app.w, 56)
        pygame.draw.rect(surf, (20,20,30), r)
        pygame.draw.rect(surf, (255,255,255,40), r, width=1)
        if self.help:
            txt = font.render(self.help, True, (220,220,230))
            surf.blit(txt, (16, 16))

class CardWidget:
    def __init__(self, creature, pos, skin=None, icons=None):
        self.creature = creature
        self.x, self.y = pos
        self.w, self.h = 180, 252
        self.dragging = False
        self.drag_offset = (0,0)
        self.skin = skin or {}
        self.icons = icons or {}
        self.is_animating = False
        self.play_anim = 0.0
        self.target_pos = (self.x, self.y)
    def rect(self):
        return Rect(int(self.x), int(self.y), int(self.w), int(self.h))
    def set_size(self, w, h):
        self.w, self.h = int(w), int(h)
    def start_drag(self, mouse_pos):
        self.dragging = True
        self.drag_offset = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
    def stop_drag(self):
        self.dragging = False
    def update(self, dt):
        if self.play_anim > 0.0:
            self.play_anim = max(0.0, self.play_anim - dt*2.0)
    def draw(self, surf, font_title, font_text):
        r = self.rect()
        # frame
        frame = self.skin.get("card_frame")
        if frame:
            surf.blit(pygame.transform.smoothscale(frame, r.size), r.topleft)
        else:
            pygame.draw.rect(surf, (45,45,60), r, border_radius=14)
            pygame.draw.rect(surf, (255,255,255,40), r, width=2, border_radius=14)
        # name
        surf.blit(font_title.render(self.creature.blueprint.name, True, WHITE), (r.x+10, r.y+8))
        # cost
        cost = str(getattr(self.creature.blueprint, "cost", 1))
        pygame.draw.circle(surf, (40,80,120), (r.right-22, r.y+22), 14)
        surf.blit(font_text.render(cost, True, (240,240,255)), (r.right-28, r.y+14))
        # stats areas (draw icons if available)
        def stat(ix, text, x, y):
            ic = self.icons.get(ix)
            if ic:
                ic = pygame.transform.smoothscale(ic, (20,20)); surf.blit(ic, (x, y))
                surf.blit(font_text.render(text, True, WHITE), (x+24, y+2))
            else:
                surf.blit(font_text.render(f"{ix}:{text}", True, WHITE), (x, y))
        # layout ratios for consistency with tooltips
        bx, by, bw, bh = r
        stat("atk", str(self.creature.atk), bx+int(0.07*bw), by+bh-int(0.36*bh))
        stat("dur", str(self.creature.current_dur), bx+int(0.07*bw), by+bh-int(0.18*bh))
        stat("spd", f"V{self.creature.spd}", bx+int(0.55*bw), by+bh-int(0.36*bh))
        # ability hint
        has_ability = bool(getattr(self.creature.blueprint, "triggers", []) or getattr(self.creature.blueprint, "keywords", []))
        if has_ability:
            ic = self.icons.get("ability")
            if ic:
                ic = pygame.transform.smoothscale(ic, (20,20))
                surf.blit(ic, (bx+int(0.55*bw), by+bh-int(0.18*bh)))
        # statuses compact
        statuses = getattr(self.creature, "statuses", {}) or {}
        sx = bx + int(0.82*bw); sy = by + int(0.10*bh)
        for key in ("venin","brulure","saignement","malediction","erosion"):
            val = statuses.get(key, 0)
            if val>0:
                ic = self.icons.get(key)
                if ic:
                    ii = pygame.transform.smoothscale(ic, (16,16)); surf.blit(ii, (sx, sy))
                    surf.blit(font_text.render(str(val), True, WHITE), (sx+18, sy-1))
                    sy += 18
