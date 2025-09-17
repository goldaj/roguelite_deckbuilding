import pygame
from engine.ui.colors import *
from engine.ui.layout import WINDOW_W, WINDOW_H
from engine.ui.widgets import draw_button

class VictoryUI:
    def __init__(self, is_boss=False):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption('Victoire')
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu_btn = pygame.Rect(WINDOW_W//2 - 160, WINDOW_H//2 + 40, 320, 60)
        self.is_boss = is_boss

    def run(self):
        action = None
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    action = "quit"
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.menu_btn.collidepoint(e.pos):
                        action = "menu"
                        self.running = False
            self.screen.fill((20,25,35))
            font = pygame.font.SysFont('arial', 44, bold=True)
            title = "Victoire du Boss !" if self.is_boss else "Victoire !"
            s = font.render(title, True, (230,230,255))
            self.screen.blit(s, (WINDOW_W//2 - s.get_width()//2, 160))

            draw_button(self.screen, self.menu_btn, "Retour au menu")
            pygame.display.flip()
            self.clock.tick(60)
        return action
