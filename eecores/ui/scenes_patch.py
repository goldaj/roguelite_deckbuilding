import pygame
from pygame import Rect
from .deckview import DeckOverlay
from .components import Button, WHITE

class DeckIntroScene:
    """
    Petite scène qui montre la page 'Deck & État persistant' en ouverture,
    avec un bouton 'Continuer' pour passer à l'étape suivante.
    Appelez app.push_scene(DeckIntroScene(app, app.state, on_done=...)).
    """
    def __init__(self, app, state, on_done):
        self.app = app
        self.state = state
        self.on_done = on_done
        self.deck = DeckOverlay(app, state)
        self.deck.open_page(on_continue=self._proceed)

    def _proceed(self):
        if callable(self.on_done):
            self.on_done()

    def handle(self, ev):
        self.deck.handle(ev)

    def update(self, dt):
        pass

    def draw(self, surf):
        self.deck.draw(surf)