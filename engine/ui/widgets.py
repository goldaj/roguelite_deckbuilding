import pygame
from engine.ui.colors import *
from engine.ui.layout import SLOT_W, SLOT_H

def draw_button(surf, rect, text, active=True):
    x,y,w,h = rect
    bg = (240,240,240) if active else (190,190,190)
    pygame.draw.rect(surf, bg, rect, border_radius=12)
    pygame.draw.rect(surf, (60,60,70), rect, width=2, border_radius=12)
    font = pygame.font.SysFont('arial', 22, bold=True)
    s = font.render(text, True, (25,25,30))
    surf.blit(s, (x + (w-s.get_width())//2, y + (h-s.get_height())//2))

def draw_slot(surf, rect, is_hover=False):
    color = SLOT_EMPTY if not is_hover else BLUE
    pygame.draw.rect(surf, color, rect, border_radius=12)
    pygame.draw.rect(surf, CARD_OUTLINE, rect, width=2, border_radius=12)

def draw_card(surf, rect, name, atk, dur, spd, is_drag=False):
    x,y,w,h = rect
    pygame.draw.rect(surf, CARD, rect, border_radius=14)
    pygame.draw.rect(surf, CARD_OUTLINE, rect, width=2, border_radius=14)
    font = pygame.font.SysFont('arial', 16, bold=True)
    font_small = pygame.font.SysFont('arial', 14)
    name_s = font.render(name, True, (30,30,35))
    surf.blit(name_s, (x+10, y+8))
    stats = f"ATK {atk}  DUR {dur}  SPD {spd}"
    stats_s = font_small.render(stats, True, (40,40,50))
    surf.blit(stats_s, (x+10, y+h-24))
    if is_drag:
        pygame.draw.rect(surf, (0,0,0,40), (x-2,y-2,w+4,h+4), width=2, border_radius=16)

def draw_pill(surf, x, y, text, color):
    font = pygame.font.SysFont('arial', 18, bold=True)
    s = font.render(text, True, WHITE)
    pad = 10
    rect = (x, y, s.get_width()+2*pad, s.get_height()+8)
    pygame.draw.rect(surf, color, rect, border_radius=12)
    surf.blit(s, (x+pad, y+4))
