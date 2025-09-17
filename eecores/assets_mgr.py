
import os, pygame

class Assets:
    def __init__(self, base_dir):
        g = lambda p: os.path.join(base_dir, p)
        self.bg = pygame.image.load(g("bg.png")).convert_alpha()
        self.panel = pygame.image.load(g("panel.png")).convert_alpha()
        self.button = pygame.image.load(g("button.png")).convert_alpha()
        self.card_frame = pygame.image.load(g("card_frame.png")).convert_alpha()
        self.mini_card = pygame.image.load(g("mini_card.png")).convert_alpha()
        # Icons
        self.icons = {}
        for name in ["atk","dur","spd","shield","carapace","venin","brulure","saignement","malediction","erosion"]:
            try:
                self.icons[name] = pygame.image.load(g(f"icon_{name}.png")).convert_alpha()
            except:
                pass
        try:
            self.logo = pygame.image.load(g("logo.png")).convert_alpha()
        except:
            self.logo = None
