
import pygame, random, os
from pygame import Rect

from eecores.core.entities import *
from eecores.run.run_state import RunState, load_cards
from eecores.run.mapgen import MapNode
from .scenes import *
from ..assets_mgr import Assets
from .deckview import DeckOverlay

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def act_pattern_nodes(rng, act_index:int):
    """Return list of nodes for one act following: R,C,R,C,R,C,R,C,R then BOSS.
    R = random among EVENT/MARCHAND/ALCHIMIE/SANCTUAIRE"""
    random_nodes_pool = ["EVENT","MARCHAND","ALCHIMIE","SANCTUAIRE"]
    seq = []
    for i in range(4):
        seq.append(MapNode(rng.choice(random_nodes_pool), f"R{i+1}"))
        seq.append(MapNode("COMBAT", f"C{i+1}"))
    seq.append(MapNode(rng.choice(random_nodes_pool), "R5"))
    seq.append(MapNode("BOSS", f"Boss Acte {act_index}"))
    return seq

class App:
    def __init__(self, seed=None):
        pygame.init()
        pygame.display.set_caption("Écorces & Échos — Deckbuilder Roguelite")
        self.w, self.h = 1080, 700
        self.flags_windowed = pygame.RESIZABLE
        self.flags_fullscreen = pygame.FULLSCREEN
        self.fullscreen = False
        self.screen = pygame.display.set_mode((self.w, self.h), self.flags_windowed)
        self.clock = pygame.time.Clock()
        self.running = True
        self.rng = random.Random(seed if seed is not None else random.randrange(1_000_000))

        # Fonts
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_medium = pygame.font.SysFont("arial", 22, bold=True)
        self.font_big = pygame.font.SysFont("arial", 36, bold=True)
        self.font_huge = pygame.font.SysFont("arial", 54, bold=True)

        self.assets = Assets(ASSETS_DIR)

        self._toast = None
        self.state = None
        self.max_acts = 3
        self.nodes = []
        self.node_ptr = 0

        # Load cards
        self.cards = load_cards(os.path.join(DATA_DIR, "cards.json"))
        self.deck_overlay = None

        # Create initial scene after attributes are ready
        self.scene = MainMenu(self)

    def toast(self, text):
        self._toast = Toast(text, duration=1.8)

    def start_new_run(self):
        deck = draft_initial_deck(self.rng, self.cards)
        self.state = RunState(rng=self.rng, cards=self.cards, deck_blueprints=deck)
        self.deck_overlay = DeckOverlay(self, self.state)
        self.state.act = 1
        self.nodes = act_pattern_nodes(self.rng, 1)
        self.node_ptr = 0
        self.goto_next_node_intro()

    def goto_next_node_intro(self):
        # Apply erosion / hatch before each node
        self.state.apply_erosion()
        for name in self.state.hatch_eggs():
            self.toast(f"Éclosion: {name}")
        node = self.nodes[self.node_ptr]
        self.scene = NodeIntroScene(self, node)

    def enter_current_node_real(self):
        node = self.nodes[self.node_ptr]
        self.scene = scene_for_node(self, self.state, node, self.state.act)

    def after_node(self):
        self.node_ptr += 1
        # if finished act, go next act automatically
        if self.node_ptr >= len(self.nodes):
            if self.state.act < self.max_acts:
                self.state.act += 1
                self.nodes = act_pattern_nodes(self.rng, self.state.act)
                self.node_ptr = 0
                self.goto_next_node_intro()
            else:
                self.end_run(True)
        else:
            self.goto_next_node_intro()

    def end_run(self, victory:bool):
        self.scene = EndScene(self, victory, self.state.fragments if self.state else 0)

    def run(self):
        while self.running:
            dt = self.clock.tick(60)/1000.0
            for ev in pygame.event.get():
                if ev.type==pygame.VIDEORESIZE:
                    self.w, self.h = ev.w, ev.h
                    if not self.fullscreen:
                        self.screen = pygame.display.set_mode((self.w, self.h), self.flags_windowed)
                if ev.type==pygame.QUIT:
                    self.running=False
                elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                    self.running=False
                elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0,0), self.flags_fullscreen)
                        info = pygame.display.Info()
                        self.w, self.h = info.current_w, info.current_h
                    else:
                        self.screen = pygame.display.set_mode((self.w, self.h), self.flags_windowed)
                else:
                    self.scene.handle(ev)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            if self._toast:
                self._toast.update(dt)
                self._toast.draw(self.screen, self.font_small)
                if self._toast.finished(): self._toast=None
            pygame.display.flip()

def draft_initial_deck(rng, bps):
    commons = [bps[cid] for cid in [
        "forest_spine_frog","forest_azure_spider","dunes_ember_scorpion","river_mud_turtle",
        "cliffs_echo_bat","ruins_crypt_rat","neutral_sparrow","neutral_rat","neutral_crab",
        "neutral_dog"
    ]]
    uncommons = [bps[cid] for cid in ["forest_mantis","dunes_coulevre_mirage"]]
    deck = commons + uncommons
    rng.shuffle(deck)
    return deck
