import pygame
from engine.ui.colors import *
from engine.ui.layout import WINDOW_W, WINDOW_H
from engine.ui.widgets import draw_button

class MainMenuUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption('Roguelite Deckbuilder — Menu')
        self.clock = pygame.time.Clock()
        self.running = True
        self.start_btn = pygame.Rect(WINDOW_W//2 - 140, WINDOW_H//2 - 30, 280, 60)

    def run(self):
        action = None
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    action = "quit"
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.start_btn.collidepoint(e.pos):
                        action = "start"
                        self.running = False

            self.screen.fill((25,30,40))
            # title
            font = pygame.font.SysFont('arial', 40, bold=True)
            s = font.render("Roguelite Deckbuilder", True, WHITE)
            self.screen.blit(s, (WINDOW_W//2 - s.get_width()//2, 130))

            draw_button(self.screen, self.start_btn, "Nouvelle partie")
            pygame.display.flip()
            self.clock.tick(60)
        return action
