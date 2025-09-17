
import pygame

class TooltipManager:
    def __init__(self, app):
        self.app = app
        self.text = None
        self.pos = (0,0)
    def show(self, text, pos):
        self.text = text
        self.pos = pos
    def clear(self):
        self.text = None
    def draw(self, surf):
        if not self.text:
            return
        font = self.app.font_small
        words = self.text.split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] > 360 and line:
                lines.append(line); line = w
            else:
                line = test
        if line: lines.append(line)
        w = max(font.size(l)[0] for l in lines) + 16
        h = len(lines)*22 + 12
        x,y = self.pos
        if x + w > self.app.w - 10: x = self.app.w - w - 10
        if y + h > self.app.h - 10: y = self.app.h - h - 10
        pane = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(pane, (0,0,0,210), (0,0,w,h), border_radius=10)
        surf.blit(pane, (x,y))
        for i,l in enumerate(lines):
            surf.blit(font.render(l, True, (235,235,245)), (x+8, y+6+i*22))

class ZoomPreview:
    def __init__(self, app):
        self.app = app
        self.card = None
        self.rect = pygame.Rect(app.w-330, 80, 300, 420)
    def set_card(self, card): self.card = card
    def clear(self): self.card = None
    def draw(self, surf):
        if not self.card: return
        r = self.rect
        r.x = self.app.w - r.w - 20
        pygame.draw.rect(surf, (18,18,24,240), r, border_radius=16)
        pygame.draw.rect(surf, (255,255,255,40), r, width=2, border_radius=16)
        y = r.y + 12
        name = self.app.font_big.render(self.card.blueprint.name, True, (240,240,252))
        surf.blit(name, (r.x+12, y)); y += 40
        line = f"ATQ {self.card.atk}   DUR {self.card.current_dur}   V{self.card.spd}"
        surf.blit(self.app.font_medium.render(line, True, (230,230,240)), (r.x+12, y)); y += 30
        desc = []
        bp = self.card.blueprint
        if getattr(bp, 'triggers', None):
            for tr in bp.triggers:
                if getattr(tr, 'event', None) == 'on_deploy' and getattr(tr, 'grant_keyword', None):
                    kw, val = tr.grant_keyword
                    if kw == 'BOUCLIER':
                        desc.append(f"À la pose: +{val} Bouclier à l'allié en face")
                else:
                    desc.append("Capacité: Effet au déploiement")
        if getattr(bp, 'keywords', None):
            desc.append("Mots-clés: " + ', '.join(bp.keywords))
        if not desc:
            desc.append("Aucune capacité spéciale")
        if getattr(self.card, 'statuses', None):
            sdesc = [f"{k}: {v}" for k,v in self.card.statuses.items() if v>0]
            if sdesc: desc.append("Statuts: " + ", ".join(sdesc))
        font = self.app.font_small
        x = r.x+12; maxw = r.w-24
        for text in desc:
            words = text.split(); line=""
            while words:
                w = words.pop(0)
                test = (line+" "+w).strip()
                if font.size(test)[0] > maxw and line:
                    surf.blit(font.render(line, True, (220,220,230)), (x, y)); y += 22; line = w
                else:
                    line = test
            if line: surf.blit(font.render(line, True, (220,220,230)), (x, y)); y += 22
        y += 8
        icons = getattr(self.app.assets, "icons", {}) or {}
        if getattr(self.card, 'statuses', None):
            for key in ('venin','brulure','saignement','malediction','erosion'):
                val = self.card.statuses.get(key, 0) if isinstance(self.card.statuses, dict) else 0
                if val>0:
                    ic = icons.get(key)
                    if ic:
                        ic = pygame.transform.smoothscale(ic, (22,22))
                        surf.blit(ic, (x, y))
                        surf.blit(font.render(str(val), True, (230,230,240)), (x+26, y+2))
                        y += 26
