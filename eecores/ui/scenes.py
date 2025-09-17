
import pygame, random
from pygame import Rect

from eecores.core.entities import *
from eecores.core.combat import *
from eecores.run.run_state import *
from eecores.run.mapgen import MapNode
from eecores.run.nodes import node_event, shop_offer, build_enemy_team
from .components import Button, CardWidget, Toast, clamp, TopBar
from .deckview import DeckOverlay
from .handview import HandOverlay
from .tooltip import TooltipManager, ZoomPreview

WHITE = (250, 250, 255)

def ease_out_quad(t): return 1 - (1 - t) * (1 - t)
def lerp(a,b,t): return a + (b-a)*t

NODE_HELP = {
    "COMBAT": (
        "Combat: Tour 1 → pioche animée de 5 cartes. Puis 1 carte au début de chaque tour. "
        "Drag & drop pour poser. Initiative par Vitesse. Bouclier annule, Carapace réduit l'ATQ adverse."
    ),
    "ELITE": "Élite: Combat plus coriace, butin amélioré.",
    "EVENT": "Événement: Gain/perte/rencontres.",
    "MARCHAND": "Marchand: Achat de cartes & Boucliers.",
    "ALCHIMIE": "Alchimie: Fusion de communes.",
    "SANCTUAIRE": "Sanctuaire: Incubation d'œuf.",
    "FREEPICK": "Cadeau: Choisissez 1 carte gratuite à ajouter à votre deck.",
    "DECKINTRO": "Deck initial: consultez l'intégralité de votre deck avant de partir."
}

class SceneBase:
    def __init__(self, app):
        self.app = app
        state = getattr(app, 'state', None)
        self.topbar = TopBar(app, state) if state else None
    def with_help(self, node_type: str):
        if self.topbar: self.topbar.set_help(NODE_HELP.get(node_type, "")); return self
    def handle(self, ev):
        if self.topbar: self.topbar.handle(ev)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov: deckov.handle(ev)
    def update(self, dt): pass
    def draw(self, surf): pass

class MainMenu(SceneBase):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = [
            Button((540, 300, 260, 60), "Nouvelle Run", self.new_run, skin={"button": app.assets.button}),
            Button((540, 380, 260, 60), "Quitter", self.quit, skin={"button": app.assets.button}),
        ]
    def new_run(self):
        # Démarre une run standard, puis impose deck=10 et introduction/FreePick custom.
        self.app.start_new_run()
        st = self.app.state
        # Forcer 10 cartes au départ (commons/rares neutres si dispo)
        pool = [bp for bp in st.cards.values() if bp.rarity in ("C","U","R")]
        if len(pool) >= 10:
            st.deck_blueprints = st.rng.sample(pool, 10)
        elif len(st.deck_blueprints) < 10:
            # fallback: duplique au besoin
            while len(st.deck_blueprints) < 10 and pool:
                st.deck_blueprints.append(st.rng.choice(pool))
        # Montrer le deck complet d'abord
        if not getattr(self.app, 'deck_overlay', None):
            self.app.deck_overlay = DeckOverlay(self.app)
        self.app.deck_overlay.visible = True
        self.app.scene = DeckIntroScene(self.app).with_help("DECKINTRO")
    def quit(self): self.app.running = False
    def handle(self, ev):
        super().handle(ev)
        for b in self.buttons: b.handle(ev)
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        title = self.app.font_huge.render("Écorces & Échos", True, WHITE); surf.blit(title, (80, 80))
        if self.app.assets.logo: surf.blit(self.app.assets.logo, (60, 140))
        for b in self.buttons: b.draw(surf, self.app.font_medium)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class DeckIntroScene(SceneBase):
    def __init__(self, app):
        super().__init__(app)
        self.btn = Button((820, 620, 220, 52), "Continuer", self.next, skin={"button": app.assets.button})
        self.with_help("DECKINTRO")
    def next(self):
        # Premier nœud: évènement de sélection gratuite
        self.app.scene = FreePickScene(self.app, self.app.state).with_help("FREEPICK")
    def handle(self, ev):
        super().handle(ev); self.btn.handle(ev)
        # deck overlay toujours visible ici
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.next()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        t = self.app.font_big.render("Votre deck initial (10 cartes)", True, WHITE); surf.blit(t, (60, 90))
        s = self.app.font_small.render("Analysez vos cartes. Appuyez sur Continuer pour recevoir 1 carte gratuite.", True, WHITE)
        surf.blit(s, (60, 140))
        self.btn.draw(surf, self.app.font_small)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov:
            deckov.visible = True
            deckov.draw(surf)

class FreePickScene(SceneBase):
    def __init__(self, app, state: RunState):
        super().__init__(app); self.state = state
        # Réutilise l'offre du shop mais picks gratuits ; limite: 1 seule carte
        self.offers = shop_offer(state)[:5]
        self.taken = False
        self.buttons = []
        y = 240
        for i, bp in enumerate(self.offers):
            def mk(bp=bp):
                def take():
                    if self.taken: return
                    self.state.deck_blueprints.append(bp)
                    self.taken = True
                    self.app.toast(f"Ajout gratuit: {bp.name}")
                return take
            self.buttons.append(Button((520, y, 340, 52), f"Prendre {bp.name} (gratuit)", mk(), skin={"button": self.app.assets.button})); y += 66
        self.cont = Button((520, 620, 340, 52), "Terminer (passe au premier nœud)", self.finish, skin={"button": self.app.assets.button})
        self.with_help("FREEPICK")
    def finish(self):
        # Enchaîne sur le flux normal: on laisse l'App entrer sur le 1er nœud réel immédiatement
        try:
            self.app.enter_current_node_real()
        except Exception:
            self.app.after_node()
    def handle(self, ev):
        super().handle(ev)
        for b in self.buttons: b.handle(ev)
        self.cont.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        t = self.app.font_big.render("Cadeau: choisissez 1 carte", True, WHITE); surf.blit(t, (60, 90))
        for b in self.buttons: b.draw(surf, self.app.font_small)
        self.cont.draw(surf, self.app.font_small)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class NodeIntroScene(SceneBase):
    def __init__(self, app, node: MapNode):
        super().__init__(app); self.node = node; self.timer = 0.0; self.with_help(node.node_type)
    def update(self, dt):
        self.timer += dt
        if self.timer >= 0.8: self.app.enter_current_node_real()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        t = self.app.font_big.render(f"Prochain nœud: {self.node.node_type}", True, WHITE); surf.blit(t, (60, 60))
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class CombatScene(SceneBase):
    def __init__(self, app, state: RunState, difficulty: int = 1):
        super().__init__(app)
        self.state = state
        self.engine = CombatEngine(state.rng, Board(), [], build_enemy_team(state.rng, state.cards, difficulty))
        self.engine.setup()
        self.energy = 3
        self.turn = 1

        self.widgets = []
        self.end_btn = Button((860, 620, 180, 52), "Fin du tour", self.end_turn, skin={"button": app.assets.button})
        self.toasts = []
        self.dragging = None
        self.hand_overlay = HandOverlay(app)
        self.tooltips = TooltipManager(app)
        self.zoom = ZoomPreview(app)
        self.with_help("COMBAT")

        self.draw_stack_pos = (40, self.app.h - 160)
        self.draw_animations = []
        self.initial_draw_phase = True
        self.initial_draw_remaining = 5
        self.initial_draw_timer = 0.0
        self.deck_empty = False

    def compute_board_pos(self):
        W, H = self.app.w, self.app.h
        grid_w = min(600, int(W * 0.7))
        cx = W // 2 - grid_w // 2
        top_enemy = 100
        top_player = top_enemy + 180
        x_points = [cx + int(grid_w * (i + 0.5) / 3) for i in range(3)]
        enemyA = [(x - 20, top_enemy) for x in x_points]
        enemyB = [(x - 20, top_enemy + 80) for x in x_points]
        playerA = [(x - 20, top_player) for x in x_points]
        playerB = [(x - 20, top_player + 80) for x in x_points]
        return {"PLAYER": {"A": playerA, "B": playerB}, "ENEMY": {"A": enemyA, "B": enemyB}}

    # Layout main (évite la pile à gauche)
    def current_layout_for_index(self, index_after_add:int):
        W, H = self.app.w, self.app.h
        n = max(1, index_after_add)
        reserved_left = self.draw_stack_pos[0] + 74
        avail_w = max(120, W - reserved_left - 16)
        max_w = (avail_w) // n - 12
        max_w = max(110, min(160, max_w))
        aspect = 210 / 150
        w = max_w; h = int(w * aspect)
        y = max(100, H - h - 20)
        x = reserved_left + (n-1) * (w + 12)
        return x, y, w, h

    def layout_hand(self):
        W, H = self.app.w, self.app.h
        n = len(self.widgets)
        if n == 0: return
        reserved_left = self.draw_stack_pos[0] + 74
        avail_w = max(120, W - reserved_left - 16)
        max_w = (avail_w) // n - 12
        max_w = max(110, min(160, max_w))
        aspect = 210 / 150
        w = max_w; h = int(w * aspect)
        y = max(100, H - h - 20); x = reserved_left
        for wdg in self.widgets:
            wdg.target_pos = (x, y)
            if not getattr(wdg, "is_animating", False) and not wdg.dragging:
                try: wdg.set_size(w, h)
                except AttributeError: wdg.w, wdg.h = int(w), int(h)
                wdg.x, wdg.y = x, y
            x += w + 12

    def spawn_draw(self, creature):
        x, y, w, h = self.current_layout_for_index(len(self.widgets) + 1)
        sx, sy = self.draw_stack_pos
        sx += 8 * (len(self.draw_animations) % 3)
        sy += 4 * (len(self.draw_animations) % 3)
        wdg = CardWidget(creature, (sx, sy), skin={"card_frame": self.app.assets.card_frame}, icons=self.app.assets.icons)
        try: wdg.set_size(max(80, int(w*0.7)), max(120, int(h*0.7)))
        except AttributeError: wdg.w, wdg.h = max(80, int(w*0.7)), max(120, int(h*0.7))
        wdg.is_animating = True; wdg.anim_t = 0.0
        wdg.start_pos = (sx, sy); wdg.target_pos = (x, y)
        self.widgets.append(wdg)
        self.draw_animations.append({"wdg": wdg, "sx": sx, "sy": sy, "ex": x, "ey": y, "sw": wdg.w, "sh": wdg.h, "ew": w, "eh": h, "t": 0.0})

    def draw_one_from_state(self):
        if self.deck_empty: return
        new = self.state.draw_hand(1)
        if new: self.spawn_draw(new[0])
        else:
            self.deck_empty = True; self.toasts.append(Toast("Pioche vide"))

    def end_turn(self):
        self.engine.run_one_turn()
        self.turn += 1; self.energy = 3
        if self.engine.presence("PLAYER") == 0 or self.engine.presence("ENEMY") == 0 or self.turn > self.engine.max_turns:
            for owner in ("PLAYER", "ENEMY"):
                for _, c in self.engine.board.iter_side(owner): self.engine.apply_end_of_combat(c)
            self.engine.cleanup_corpses()
            victory = self.engine.presence("ENEMY") == 0 and self.engine.presence("PLAYER") > 0
            survivors = [c.copy_persistent() for _, c in self.engine.board.iter_side("PLAYER")]
            loot_frag = 12 if victory else 4; loot_gene = 1 if victory and self.state.rng.random() < 0.25 else 0
            loot_shield = 1 if victory and self.state.rng.random() < 0.30 else 0; loot_egg = 1 if victory and self.state.rng.random() < 0.20 else 0
            self.state.persist_post_combat(survivors); self.state.fragments += loot_frag; self.state.genes += loot_gene
            if loot_shield:
                name = self.state.grant_shield_to_random(1); 
                if name: self.toasts.append(Toast(f"Bouclier +1 sur {name}"))
            if loot_egg: self.state.eggs.append(2); self.toasts.append(Toast("ŒUF obtenu"))
            if len(self.state.deck_blueprints) == 0: self.app.end_run(False)
            else: self.app.after_node()
            return
        self.draw_one_from_state()

    def slot_by_pos(self, pos):
        BOARD_POS = self.compute_board_pos()
        for lane in ("A", "B"):
            for i, pt in enumerate(BOARD_POS["PLAYER"][lane]):
                r = Rect(pt[0] - 50, pt[1] - 40, 100, 80)
                if r.collidepoint(pos): return ("PLAYER", lane, i, r)
        return None

    def try_play(self, w, mouse):
        if getattr(w, "is_animating", False): return
        if self.energy < w.creature.blueprint.cost: self.toasts.append(Toast("Pas assez d'énergie")); return
        slot = self.slot_by_pos(mouse)
        if not slot: self.toasts.append(Toast("Déposez sur une case valide")); return
        owner, lane, col, _ = slot
        if not self.engine.board.place(owner, w.creature, lane, col): self.toasts.append(Toast("Case occupée")); return
        for tr in w.creature.blueprint.triggers:
            if tr.event == "on_deploy" and tr.grant_keyword and tr.target == "ALLY_LINE":
                other = "B" if lane == "A" else "A"; slots = self.engine.board.player_slots; ally = slots.get((other, col))
                if ally and tr.grant_keyword[0] == KW_BOUCLIER: ally.shields += tr.grant_keyword[1]; self.toasts.append(Toast(f"{ally.blueprint.name} +Bouclier"))
        w.play_anim = 1.0; self.energy -= w.creature.blueprint.cost; self.widgets.remove(w); self.layout_hand()

    def handle(self, ev):
        super().handle(ev)
        self.end_btn.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_h: self.hand_overlay.toggle()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
        if self.initial_draw_phase: return
        if ev.type == pygame.MOUSEMOTION:
            self.tooltips.clear(); self.zoom.clear()
            pos = ev.pos; BOARD_POS = self.compute_board_pos()
            # board hover → zoom + tooltips précises
            for owner, slots in (("ENEMY", self.engine.board.enemy_slots), ("PLAYER", self.engine.board.player_slots)):
                for (lane, i), c in slots.items():
                    if not c: continue
                    posc = BOARD_POS[owner][lane][i]; r = Rect(posc[0] - 70, posc[1] - 50, 140, 110)
                    if r.collidepoint(pos):
                        self.zoom.set_card(c)
                        font = self.app.font_small
                        def srect(lbl, ox, oy): return pygame.Rect(r.x+ox, r.y+oy, 18+4+font.size(lbl)[0], 20)
                        if srect(str(c.atk), 6, 46).collidepoint(pos): self.tooltips.show(f"ATTAQUE: dégâts infligés ({c.atk}).", (pos[0]+14, pos[1]+14)); break
                        if srect(str(c.current_dur), 6, 68).collidepoint(pos): self.tooltips.show(f"DURABILITÉ: points de vie restants ({c.current_dur}).", (pos[0]+14, pos[1]+14)); break
                        if srect(f"V{c.spd}", 74, 46).collidepoint(pos): self.tooltips.show(f"VITESSE: initiative/ordre d'action (V{c.spd}).", (pos[0]+14, pos[1]+14)); break
                        if pygame.Rect(r.x+74, r.y+68, 20, 20).collidepoint(pos) and (getattr(c.blueprint,"triggers",[]) or getattr(c.blueprint,"keywords",[])):
                            self.tooltips.show("CAPACITÉ: effets au déploiement ou mots-clés.", (pos[0]+14, pos[1]+14)); break
                        sx = r.x + 100; sy = r.y + 46
                        for key in ("venin","brulure","saignement","malediction","erosion"):
                            val = getattr(c, "statuses", {}).get(key, 0)
                            if val>0:
                                area = pygame.Rect(sx, sy, 34, 18)
                                if area.collidepoint(pos): self.tooltips.show(f"STATUT {key.capitalize()}: {val}", (pos[0]+14, pos[1]+14)); break
                                sy += 18
            # hand hover — zones en proportion du rect → plus précis
            for w in self.widgets:
                rx,ry,rw,rh = w.rect()
                if Rect(rx,ry,rw,rh).collidepoint(pos):
                    ob = ry+rh
                    atk_rect = Rect(rx+int(0.07*rw), ob-int(0.36*rh), int(0.28*rw), int(0.18*rh))
                    dur_rect = Rect(rx+int(0.07*rw), ob-int(0.18*rh), int(0.28*rw), int(0.18*rh))
                    spd_rect = Rect(rx+int(0.55*rw), ob-int(0.36*rh), int(0.35*rw), int(0.18*rh))
                    abil_rect= Rect(rx+int(0.55*rw), ob-int(0.18*rh), int(0.35*rw), int(0.18*rh))
                    if atk_rect.collidepoint(pos): self.tooltips.show(f"ATTAQUE: dégâts infligés ({w.creature.atk}).", (pos[0]+14, pos[1]+14)); break
                    if dur_rect.collidepoint(pos): self.tooltips.show(f"DURABILITÉ: points de vie ({w.creature.current_dur}).", (pos[0]+14, pos[1]+14)); break
                    if spd_rect.collidepoint(pos): self.tooltips.show(f"VITESSE: initiative (V{w.creature.spd}).", (pos[0]+14, pos[1]+14)); break
                    bp = w.creature.blueprint
                    if abil_rect.collidepoint(pos) and (getattr(bp,"triggers",[]) or getattr(bp,"keywords",[])):
                        self.tooltips.show("CAPACITÉ: effets au déploiement ou mots-clés.", (pos[0]+14, pos[1]+14)); break
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for w in reversed(self.widgets):
                if getattr(w, "is_animating", False): continue
                if w.rect().collidepoint(ev.pos):
                    self.dragging = w; w.start_drag(ev.pos); break
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if self.dragging:
                w = self.dragging; w.stop_drag(); self.try_play(w, ev.pos); self.dragging = None
        elif ev.type == pygame.MOUSEMOTION and self.dragging:
            w = self.dragging; w.x = ev.pos[0] - w.drag_offset[0]; w.y = ev.pos[1] - w.drag_offset[1]

    def update(self, dt):
        if self.initial_draw_phase:
            self.initial_draw_timer += dt
            if self.initial_draw_remaining > 0 and self.initial_draw_timer >= 0.25:
                self.initial_draw_timer = 0.0
                new = self.state.draw_hand(1)
                if new: self.spawn_draw(new[0]); self.initial_draw_remaining -= 1
                else: self.deck_empty = True; self.initial_draw_remaining = 0
            if self.initial_draw_remaining <= 0 and not self.draw_animations:
                self.initial_draw_phase = False
        finished = []
        for anim in self.draw_animations:
            anim["t"] += dt * 3.0
            t = min(1.0, anim["t"])
            wdg = anim["wdg"]
            wdg.x = lerp(anim["sx"], anim["ex"], ease_out_quad(t))
            wdg.y = lerp(anim["sy"], anim["ey"], ease_out_quad(t))
            try: wdg.set_size(lerp(anim["sw"], anim["ew"], t), lerp(anim["sh"], anim["eh"], t))
            except AttributeError: wdg.w, wdg.h = int(lerp(anim["sw"], anim["ew"], t)), int(lerp(anim["sh"], anim["eh"], t))
            if t >= 1.0: wdg.is_animating = False; finished.append(anim)
        for a in finished: self.draw_animations.remove(a)
        self.layout_hand()
        for w in self.widgets: w.update(dt)
        for t in list(self.toasts):
            t.update(dt); 
            if t.finished(): self.toasts.remove(t)

    def draw_deck_stack(self, surf):
        x, y = self.draw_stack_pos
        base_col = (26, 26, 34) if self.deck_empty else (40, 40, 56)
        for i in range(3):
            r = Rect(x + i*6, y + i*4, 60, 86)
            pygame.draw.rect(surf, base_col, r, border_radius=8)
            pygame.draw.rect(surf, (255,255,255,40), r, width=2, border_radius=8)
        text = "Pioche vide" if self.deck_empty else "Pioche"
        label = self.app.font_small.render(text, True, WHITE)
        surf.blit(label, (x, y-20))

    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        BOARD_POS = self.compute_board_pos()
        for owner in ("ENEMY", "PLAYER"):
            for lane in ("A", "B"):
                for i, pt in enumerate(BOARD_POS[owner][lane]):
                    r = Rect(pt[0] - 50, pt[1] - 40, 100, 80)
                    col = (60, 60, 80) if owner == "PLAYER" else (70, 50, 60)
                    pygame.draw.rect(surf, col, r, border_radius=12)
                    pygame.draw.rect(surf, (255, 255, 255, 40), r, width=2, border_radius=12)
        # units
        font = self.app.font_small
        for owner, slots in (("ENEMY", self.engine.board.enemy_slots), ("PLAYER", self.engine.board.player_slots)):
            for (lane, i), c in slots.items():
                if not c: continue
                pos = BOARD_POS[owner][lane][i]
                r = Rect(pos[0] - 70, pos[1] - 50, 140, 110)
                surf.blit(pygame.transform.smoothscale(self.app.assets.mini_card, (r.w, r.h)), r.topleft)
                name = font.render(c.blueprint.name.split()[0], True, (230, 230, 240)); surf.blit(name, (r.x + 6, r.y + 6))
                def stat(ix, lbl, ox, oy):
                    ic = self.app.assets.icons.get(ix)
                    if ic: ic = pygame.transform.smoothscale(ic, (18, 18)); surf.blit(ic, (r.x + ox, r.y + oy))
                    t = font.render(lbl, True, (220, 220, 230)); surf.blit(t, (r.x + ox + 22, r.y + oy+1))
                stat("atk", str(c.atk), 6, 46)
                stat("dur", str(c.current_dur), 6, 68)
                stat("spd", f"V{c.spd}", 74, 46)
                has_ability = bool(getattr(c.blueprint, "triggers", []) or getattr(c.blueprint, "keywords", []))
                if has_ability:
                    ic = self.app.assets.icons.get("ability")
                    if ic: ic = pygame.transform.smoothscale(ic, (18,18)); surf.blit(ic, (r.x + 74, r.y + 68))
                statuses = getattr(c, "statuses", {}) or {}
                sx = r.x + 100; sy = r.y + 46
                for key in ("venin","brulure","saignement","malediction","erosion"):
                    val = statuses.get(key, 0)
                    if val>0:
                        ic = self.app.assets.icons.get(key)
                        if ic:
                            ii = pygame.transform.smoothscale(ic, (16,16)); surf.blit(ii, (sx, sy))
                            surf.blit(font.render(str(val), True, (225,225,235)), (sx+18, sy-1))
                            sy += 18
        for w in self.widgets: w.draw(surf, self.app.font_small, self.app.font_small)
        hud = self.app.font_small.render(f"Tour {self.turn} | Énergie {self.energy} | Ennemis:{self.engine.presence('ENEMY')}", True, WHITE); surf.blit(hud, (20, 70))
        self.end_btn.draw(surf, self.app.font_small)
        self.draw_deck_stack(surf)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        for t in self.toasts: t.draw(surf, self.app.font_small, y=100)
        self.hand_overlay.draw(surf, self.widgets)
        self.zoom.draw(surf); self.tooltips.draw(surf)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class ShopScene(SceneBase):
    def __init__(self, app, state: RunState):
        super().__init__(app); self.state = state
        self.offers = shop_offer(state)
        self.buttons = []
        y = 240
        for i, bp in enumerate(self.offers):
            def mk(bp=bp):
                def buy():
                    price = 15 if bp.rarity in ("C", "U") else 25
                    if self.state.fragments >= price:
                        self.state.fragments -= price; self.state.deck_blueprints.append(bp); self.app.toast(f"Achat: {bp.name}")
                    else: self.app.toast("Pas assez de fragments")
                return buy
            self.buttons.append(Button((520, y, 280, 52), f"Acheter {bp.name}", mk(), skin={"button": self.app.assets.button})); y += 70
        self.shield = Button((520, y, 280, 52), "Bouclier (+1) — 10", self.buy_shield, skin={"button": self.app.assets.button})
        self.leave = Button((520, 600, 280, 52), "Continuer", self.leave_shop, skin={"button": self.app.assets.button})
        self.with_help("MARCHAND")
    def buy_shield(self):
        if self.state.fragments >= 10:
            self.state.fragments -= 10; name = self.state.grant_shield_to_random(1)
            if name: self.app.toast(f"+1 Bouclier à {name}")
        else: self.app.toast("Pas assez de fragments")
    def leave_shop(self): self.app.after_node()
    def handle(self, ev):
        super().handle(ev)
        for b in self.buttons + [self.shield, self.leave]: b.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0)); t = self.app.font_big.render("Marchand", True, WHITE); surf.blit(t, (60, 90))
        for b in self.buttons + [self.shield, self.leave]: b.draw(surf, self.app.font_small)
        hud = self.app.font_small.render(f"Fragments: {self.state.fragments}", True, WHITE); surf.blit(hud, (60, 140))
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class EventScene(SceneBase):
    def __init__(self, app, state: RunState):
        super().__init__(app); self.state = state
        self.text = node_event(state)
        self.btn = Button((820, 620, 220, 52), "Continuer", self.next, skin={"button": app.assets.button})
        self.with_help("EVENT")
    def next(self): self.app.after_node()
    def handle(self, ev):
        super().handle(ev); self.btn.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0)); t = self.app.font_big.render("Événement", True, WHITE); surf.blit(t, (60, 90))
        p = self.app.font_small.render(self.text, True, WHITE); surf.blit(p, (60, 160))
        self.btn.draw(surf, self.app.font_small)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class AlchemyScene(SceneBase):
    def __init__(self, app, state: RunState):
        super().__init__(app); self.state = state
        self.btn = Button((820, 620, 220, 52), "Fusionner", self.fuse, skin={"button": self.app.assets.button})
        self.leave = Button((560, 620, 220, 52), "Continuer", self.exit_, skin={"button": self.app.assets.button})
        self.with_help("ALCHIMIE")
    def fuse(self):
        commons = [bp for bp in self.state.deck_blueprints if bp.rarity == "C"]
        if len(commons) >= 2:
            a, b = self.state.rng.sample(commons, 2)
            try: self.state.deck_blueprints.remove(a); self.state.deck_blueprints.remove(b)
            except ValueError: pass
            atk = max(1, (a.atk + b.atk) // 2 + self.state.rng.choice([0, 1])); dur = max(2, (a.dur + b.dur) // 2); spd = max(1, min(3, (a.spd + b.spd) // 2))
            new_bp = CardBlueprint(id=f"fusion_{a.id}_{b.id}_{self.state.rng.randrange(10000)}", name=f"Fusion de {a.name.split()[0]} & {b.name.split()[0]}", biome="NEUTRE", rarity="U", cost=1, atk=atk, dur=dur, spd=spd, keywords=[], keyword_values={}, triggers=[], notes="Fusion alchimique")
            self.state.deck_blueprints.append(new_bp); self.app.toast(f"Nouvelle carte: {new_bp.name}")
        else: self.app.toast("Pas assez de communes")
    def exit_(self): self.app.after_node()
    def handle(self, ev):
        super().handle(ev); self.btn.handle(ev); self.leave.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0)); t = self.app.font_big.render("Alchimie", True, WHITE); surf.blit(t, (60, 90))
        self.btn.draw(surf, self.app.font_small); self.leave.draw(surf, self.app.font_small)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class SanctuaryScene(SceneBase):
    def __init__(self, app, state: RunState):
        super().__init__(app); self.state = state
        self.incub = Button((520, 320, 280, 52), "Incuber un œuf (10)", self.inc, skin={"button": self.app.assets.button})
        self.leave = Button((520, 600, 280, 52), "Continuer", self.exit_, skin={"button": self.app.assets.button})
        self.with_help("SANCTUAIRE")
    def inc(self):
        if self.state.fragments >= 10:
            self.state.fragments -= 10; self.state.deck_blueprints.append(self.state.cards["neutral_jeune"]); self.app.toast("Un Jeune Naissant rejoint votre deck.")
        else: self.app.toast("Pas assez de fragments")
    def exit_(self): self.app.after_node()
    def handle(self, ev):
        super().handle(ev); self.incub.handle(ev); self.leave.handle(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and getattr(self.app, 'deck_overlay', None): self.app.deck_overlay.toggle()
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0)); t = self.app.font_big.render("Sanctuaire", True, WHITE); surf.blit(t, (60, 90))
        self.incub.draw(surf, self.app.font_small); self.leave.draw(surf, self.app.font_small)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

class EndScene(SceneBase):
    def __init__(self, app, victory: bool, fragments: int):
        super().__init__(app); self.victory = victory; self.fragments = fragments
        self.btn = Button((440, 520, 240, 60), "Retour menu", self.back, skin={"button": self.app.assets.button})
    def back(self): self.app.scene = MainMenu(self.app)
    def handle(self, ev): super().handle(ev); self.btn.handle(ev)
    def draw(self, surf):
        surf.blit(self.app.assets.bg, (0, 0))
        t = self.app.font_huge.render("VICTOIRE !" if self.victory else "DÉFAITE", True, WHITE); surf.blit(t, (320, 240))
        s = self.app.font_big.render(f"Score (Fragments): {self.fragments}", True, WHITE); surf.blit(s, (360, 320))
        self.btn.draw(surf, self.app.font_medium)
        if self.topbar: self.topbar.draw(surf, self.app.font_small)
        deckov = getattr(self.app, 'deck_overlay', None)
        if deckov and deckov.visible: deckov.draw(surf)

def scene_for_node(app, state, node: MapNode, act: int):
    diff = act + (1 if node.node_type == "ELITE" else 0)
    if node.node_type == "FREEPICK": return FreePickScene(app, state)
    if node.node_type in ("COMBAT", "ELITE"): return CombatScene(app, state, difficulty=diff)
    if node.node_type == "EVENT": return EventScene(app, state)
    if node.node_type == "MARCHAND": return ShopScene(app, state)
    if node.node_type == "ALCHIMIE": return AlchemyScene(app, state)
    if node.node_type == "SANCTUAIRE": return SanctuaryScene(app, state)
    if node.node_type == "BOSS": return CombatScene(app, state, difficulty=act + 1)
    return EventScene(app, state)
