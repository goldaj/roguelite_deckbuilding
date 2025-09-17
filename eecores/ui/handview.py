import pygame
from pygame import Rect

class HandOverlay:
    """
    Gestion du drag & drop des cartes SANS traînées/after-image.
    Principe :
      - On dessine les cartes "statiques" (telles qu'elles sont dans la main) sur le `surf` normal.
      - La carte en cours de drag est dessinée UNIQUEMENT sur une couche dédiée `_drag_layer`
        qui est vidée (remise transparente) à CHAQUE frame.
      - On évite absolument de redessiner la carte dragguée à sa position d'origine
        pendant le drag, pour ne pas avoir de "double dessin" confus.
    Intégration :
      - Appelez HandOverlay.begin_drag(widget, mouse_pos) quand le drag commence.
      - Appelez HandOverlay.end_drag() quand le drag finit.
      - Dans votre scène, au draw():
         1) dessinez votre fond / plateau / UI habituelle
         2) dessinez vos widgets de main *sauf* la carte en cours de drag (géré ici)
         3) appelez self.hand_overlay.draw(surf, widgets_de_la_main)
    """
    def __init__(self, app):
        self.app = app
        self.dragging = None      # widget (carte) en drag
        self.drag_offset = (0, 0) # offset curseur->carte au moment du clic
        # Couche transparente dédiée au drag, REINITIALISEE chaque frame
        self._drag_layer = pygame.Surface((app.w, app.h), pygame.SRCALPHA)

    # --- API drag ------------------------------------------------------------
    def begin_drag(self, widget, mouse_pos):
        """A appeler au MOUSEBUTTONDOWN (si on commence à drag cette carte)."""
        self.dragging = widget
        # calcule l'offset curseur->coin haut-gauche de la carte
        rx, ry = (0, 0)
        if hasattr(widget, "rect"):
            # accepte méthode rect() ou attribut rect
            r = widget.rect() if callable(widget.rect) else widget.rect
            rx, ry = r.topleft
        elif hasattr(widget, "x") and hasattr(widget, "y"):
            rx, ry = widget.x, widget.y
        self.drag_offset = (mouse_pos[0] - rx, mouse_pos[1] - ry)

    def end_drag(self):
        """A appeler au MOUSEBUTTONUP (on lache la carte)."""
        self.dragging = None

    # --- Rendu ---------------------------------------------------------------
    def draw(self, surf, widgets=None):
        """
        Dessine la main + la carte en drag sans traînées.
        - `widgets` : liste des CardWidget de la main (peut être None si vous gérez le rendu de la main ailleurs).
        Important : cette fonction NE dessine jamais la carte en drag sur `surf`. Elle la dessine
        uniquement sur `_drag_layer`, qui est remise à zéro chaque frame.
        """
        # 1) Dessin des widgets "statiques" de la main (optionnel)
        if widgets:
            for w in widgets:
                if w is self.dragging:
                    # ne pas redessiner la carte en drag sur la surface principale,
                    # elle sera dessinée plus bas sur la couche de drag
                    continue
                if hasattr(w, "update"):
                    # laisser vivre les petites anims de widget si besoin
                    w.update(0)
                # Supporte draw(surf) ou draw(surf, ...)
                try:
                    w.draw(surf)
                except TypeError:
                    # silhouettes courantes: draw(surf, font_title, font_text)
                    # on essaye de récupérer des polices standard si dispo sur app
                    font_big = getattr(self.app, "font_big", None)
                    font_small = getattr(self.app, "font_small", None)
                    if font_big is not None and font_small is not None:
                        w.draw(surf, font_big, font_small)

        # 2) Couche DRAG : effacée *chaque frame* -> empêche toute "after-image"
        self._drag_layer.fill((0, 0, 0, 0))

        if self.dragging is not None:
            # position courante de la souris moins l'offset de départ
            mx, my = pygame.mouse.get_pos()
            x = mx - self.drag_offset[0]
            y = my - self.drag_offset[1]

            # Si le widget expose un rect => on le déplace pour ce rendu uniquement
            if hasattr(self.dragging, "rect"):
                if callable(self.dragging.rect):
                    r = self.dragging.rect()
                    r.topleft = (x, y)
                    # beaucoup de CardWidget lisent leur position dans self.x/self.y,
                    # donc on tente également une maj temporaire (non destructive) si dispo
                    if hasattr(self.dragging, "x"):
                        old = (self.dragging.x, self.dragging.y)
                        self.dragging.x, self.dragging.y = x, y
                        self._safe_draw_widget(self.dragging, self._drag_layer)
                        self.dragging.x, self.dragging.y = old
                    else:
                        # fallback : on dessine en espérant que le widget prenne son rect()
                        self._safe_draw_widget(self.dragging, self._drag_layer)
                else:
                    # c'est un attribut Rect direct
                    old_rect = self.dragging.rect.copy()
                    self.dragging.rect.topleft = (x, y)
                    self._safe_draw_widget(self.dragging, self._drag_layer)
                    self.dragging.rect = old_rect
            else:
                # pas de rect: on essaye via x/y si présents
                had_xy = hasattr(self.dragging, "x") and hasattr(self.dragging, "y")
                if had_xy:
                    old = (self.dragging.x, self.dragging.y)
                    self.dragging.x, self.dragging.y = x, y
                self._safe_draw_widget(self.dragging, self._drag_layer)
                if had_xy:
                    self.dragging.x, self.dragging.y = old

        # 3) Compose : on blitte la couche de drag UNE SEULE FOIS par frame
        surf.blit(self._drag_layer, (0, 0))

    # --- util interne --------------------------------------------------------
    def _safe_draw_widget(self, widget, target_surf):
        """Essaie d'appeler la bonne signature de draw, sans planter."""
        try:
            widget.draw(target_surf)
        except TypeError:
            font_big = getattr(self.app, "font_big", None)
            font_small = getattr(self.app, "font_small", None)
            if font_big is not None and font_small is not None:
                widget.draw(target_surf, font_big, font_small)
            else:
                # dernier recours : dessine un placeholder
                r = Rect(0, 0, 160, 220)
                pygame.draw.rect(target_surf, (200, 80, 80), r, border_radius=12)
                pygame.draw.line(target_surf, (255, 255, 255), r.topleft, r.bottomright, 2)
                pygame.draw.line(target_surf, (255, 255, 255), r.topright, r.bottomleft, 2)
