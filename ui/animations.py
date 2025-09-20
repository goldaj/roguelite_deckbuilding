# ui/animations.py
"""Système d'animations et d'effets visuels"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto


class AnimationType(Enum):
    """Types d'animations"""
    MOVE = auto()
    ATTACK = auto()
    DAMAGE = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()
    DEATH = auto()
    SPAWN = auto()
    CARD_DRAW = auto()
    CARD_PLAY = auto()
    STATUS_APPLY = auto()
    SHIELD_BREAK = auto()


@dataclass
class Particle:
    """Particule individuelle"""
    x: float
    y: float
    vx: float  # Vélocité X
    vy: float  # Vélocité Y
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.0
    fade: bool = True
    glow: bool = False

    def update(self, dt: float):
        """Met à jour la particule"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt

        if self.fade:
            self.size *= (self.life / self.max_life)

    def is_alive(self) -> bool:
        return self.life > 0 and self.size > 0

    def get_alpha(self) -> int:
        """Calcule l'alpha selon la vie restante"""
        if self.fade:
            return int(255 * (self.life / self.max_life))
        return 255


class ParticleSystem:
    """Système de particules"""

    def __init__(self):
        self.particles: List[Particle] = []
        self.emitters: Dict[str, 'ParticleEmitter'] = {}

    def update(self, dt: float):
        """Met à jour toutes les particules"""
        # Mettre à jour les particules existantes
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(dt)

        # Mettre à jour les émetteurs
        for emitter in self.emitters.values():
            if emitter.active:
                emitter.update(dt)
                self.particles.extend(emitter.emit())

    def draw(self, screen: pygame.Surface):
        """Dessine toutes les particules"""
        for particle in self.particles:
            self._draw_particle(screen, particle)

    def _draw_particle(self, screen: pygame.Surface, particle: Particle):
        """Dessine une particule individuelle"""
        if particle.glow:
            # Effet de lueur
            for i in range(3):
                size = particle.size * (3 - i)
                alpha = particle.get_alpha() // (i + 1)
                color = (*particle.color, alpha)

                # Créer une surface temporaire pour l'alpha
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                screen.blit(surf, (particle.x - size, particle.y - size))
        else:
            pygame.draw.circle(screen, particle.color,
                               (int(particle.x), int(particle.y)),
                               int(particle.size))

    def spawn_burst(self, x: float, y: float, particle_type: str, count: int = 20):
        """Crée une explosion de particules"""
        configs = {
            'damage': {
                'color': (255, 50, 50),
                'speed': 100,
                'life': 0.5,
                'size': 3,
                'gravity': 200
            },
            'heal': {
                'color': (50, 255, 50),
                'speed': 50,
                'life': 1.0,
                'size': 4,
                'gravity': -100,
                'glow': True
            },
            'poison': {
                'color': (100, 200, 50),
                'speed': 30,
                'life': 1.5,
                'size': 2,
                'gravity': 50
            },
            'fire': {
                'color': (255, 150, 0),
                'speed': 80,
                'life': 0.8,
                'size': 5,
                'gravity': -50,
                'glow': True
            },
            'shield': {
                'color': (150, 150, 255),
                'speed': 60,
                'life': 1.0,
                'size': 6,
                'gravity': 0,
                'glow': True
            }
        }

        config = configs.get(particle_type, configs['damage'])

        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(config['speed'] * 0.5, config['speed'] * 1.5)

            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=config['life'],
                max_life=config['life'],
                color=config['color'],
                size=random.uniform(config['size'] * 0.5, config['size'] * 1.5),
                gravity=config['gravity'],
                glow=config.get('glow', False)
            )

            self.particles.append(particle)

    def create_emitter(self, name: str, x: float, y: float, config: Dict) -> 'ParticleEmitter':
        """Crée un émetteur de particules"""
        emitter = ParticleEmitter(x, y, config)
        self.emitters[name] = emitter
        return emitter

    def remove_emitter(self, name: str):
        """Supprime un émetteur"""
        if name in self.emitters:
            del self.emitters[name]


@dataclass
class ParticleEmitter:
    """Émetteur de particules continu"""
    x: float
    y: float
    config: Dict
    active: bool = True
    timer: float = 0.0

    def update(self, dt: float):
        """Met à jour l'émetteur"""
        self.timer += dt

    def emit(self) -> List[Particle]:
        """Émet de nouvelles particules"""
        particles = []

        rate = self.config.get('rate', 10)  # Particules par seconde

        while self.timer > 1.0 / rate:
            self.timer -= 1.0 / rate

            particle = Particle(
                x=self.x + random.uniform(-5, 5),
                y=self.y + random.uniform(-5, 5),
                vx=random.uniform(-20, 20),
                vy=random.uniform(-50, -20),
                life=self.config.get('life', 1.0),
                max_life=self.config.get('life', 1.0),
                color=self.config.get('color', (255, 255, 255)),
                size=random.uniform(1, 3),
                gravity=self.config.get('gravity', 50)
            )

            particles.append(particle)

        return particles


class AnimationManager:
    """Gestionnaire d'animations"""

    def __init__(self):
        self.animations: List['Animation'] = []
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()

    def update(self, dt: float):
        """Met à jour toutes les animations"""
        # Mettre à jour les animations
        self.animations = [a for a in self.animations if not a.finished]
        for animation in self.animations:
            animation.update(dt)

        # Mettre à jour les particules
        self.particle_system.update(dt)

        # Mettre à jour le screen shake
        self.screen_shake.update(dt)

    def draw(self, screen: pygame.Surface):
        """Dessine tous les effets visuels"""
        # Appliquer le screen shake
        if self.screen_shake.active:
            offset = self.screen_shake.get_offset()
            screen_copy = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(screen_copy, offset)

        # Dessiner les particules
        self.particle_system.draw(screen)

        # Dessiner les animations
        for animation in self.animations:
            animation.draw(screen)

    def play_animation(self, anim_type: AnimationType, **kwargs):
        """Lance une animation"""
        if anim_type == AnimationType.ATTACK:
            self._play_attack_animation(**kwargs)
        elif anim_type == AnimationType.DAMAGE:
            self._play_damage_animation(**kwargs)
        elif anim_type == AnimationType.CARD_PLAY:
            self._play_card_animation(**kwargs)
        # etc...

    def _play_attack_animation(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Animation d'attaque"""
        # Créer une traînée de particules
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        steps = int(distance / 20)
        for i in range(steps):
            t = i / steps
            x = start_pos[0] + dx * t
            y = start_pos[1] + dy * t

            self.particle_system.spawn_burst(x, y, 'damage', count=3)

        # Screen shake
        self.screen_shake.shake(intensity=5, duration=0.2)

    def _play_damage_animation(self, pos: Tuple[int, int], damage: int):
        """Animation de dégâts"""
        # Nombre de particules selon les dégâts
        particle_count = min(5 + damage * 2, 30)
        self.particle_system.spawn_burst(pos[0], pos[1], 'damage', count=particle_count)

        # Texte de dégâts flottant
        self.animations.append(FloatingText(
            x=pos[0],
            y=pos[1],
            text=str(damage),
            color=(255, 50, 50),
            duration=1.0
        ))

        # Screen shake pour gros dégâts
        if damage >= 5:
            self.screen_shake.shake(intensity=damage, duration=0.3)

    def _play_card_animation(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Animation de carte jouée"""
        # Particules au départ
        self.particle_system.spawn_burst(start_pos[0], start_pos[1], 'shield', count=10)

        # Animation de déplacement
        self.animations.append(CardMoveAnimation(
            start_pos=start_pos,
            end_pos=end_pos,
            duration=0.5
        ))


@dataclass
class Animation:
    """Classe de base pour les animations"""
    duration: float
    elapsed: float = 0.0
    finished: bool = False

    def update(self, dt: float):
        """Met à jour l'animation"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True

    def draw(self, screen: pygame.Surface):
        """Dessine l'animation"""
        pass

    def get_progress(self) -> float:
        """Retourne la progression de 0 à 1"""
        return min(self.elapsed / self.duration, 1.0)


class FloatingText(Animation):
    """Texte flottant (pour dégâts, buffs, etc.)"""

    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int],
                 duration: float = 1.0, font_size: int = 20):
        super().__init__(duration)
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.start_y = y
        self.float_distance = 50

    def draw(self, screen: pygame.Surface):
        """Dessine le texte flottant"""
        if self.finished:
            return

        # Calculer la position
        progress = self.get_progress()
        current_y = self.start_y - (self.float_distance * progress)

        # Calculer l'alpha
        alpha = int(255 * (1.0 - progress))

        # Rendre le texte
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)

        # Centrer et dessiner
        rect = text_surface.get_rect(center=(int(self.x), int(current_y)))
        screen.blit(text_surface, rect)


class CardMoveAnimation(Animation):
    """Animation de déplacement de carte"""

    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                 duration: float = 0.5):
        super().__init__(duration)
        self.start_pos = start_pos
        self.end_pos = end_pos

    def get_current_pos(self) -> Tuple[int, int]:
        """Calcule la position actuelle"""
        progress = self.get_progress()

        # Interpolation avec easing
        t = self._ease_out_cubic(progress)

        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t

        return int(x), int(y)

    def _ease_out_cubic(self, t: float) -> float:
        """Fonction d'easing cubique"""
        return 1 - (1 - t) ** 3


class ScreenShake:
    """Effet de tremblement d'écran"""

    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.elapsed = 0.0
        self.active = False

    def shake(self, intensity: float, duration: float):
        """Déclenche un tremblement"""
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float):
        """Met à jour le tremblement"""
        if not self.active:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False

    def get_offset(self) -> Tuple[int, int]:
        """Retourne le décalage actuel"""
        if not self.active:
            return (0, 0)

        # Réduire l'intensité avec le temps
        current_intensity = self.intensity * (1.0 - self.elapsed / self.duration)

        # Décalage aléatoire
        offset_x = random.randint(-int(current_intensity), int(current_intensity))
        offset_y = random.randint(-int(current_intensity), int(current_intensity))

        return (offset_x, offset_y)


# audio.py
"""Système audio complet"""

import pygame
import random
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum, auto


class SoundType(Enum):
    """Types de sons"""
    # UI
    BUTTON_CLICK = auto()
    BUTTON_HOVER = auto()
    CARD_DRAW = auto()
    CARD_PLAY = auto()
    CARD_SELECT = auto()

    # Combat
    ATTACK_MELEE = auto()
    ATTACK_RANGED = auto()
    DAMAGE_SMALL = auto()
    DAMAGE_MEDIUM = auto()
    DAMAGE_LARGE = auto()
    SHIELD_BLOCK = auto()
    SHIELD_BREAK = auto()

    # Effets
    POISON_APPLY = auto()
    BURN_APPLY = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()

    # Ambiance
    VICTORY = auto()
    DEFEAT = auto()
    LEVEL_UP = auto()
    UNLOCK = auto()


class MusicTrack(Enum):
    """Pistes musicales"""
    MENU = "menu_theme"
    FOREST = "forest_ambient"
    DUNES = "dunes_ambient"
    CLIFFS = "cliffs_ambient"
    RIVER = "river_ambient"
    VOLCANO = "volcano_ambient"
    RUINS = "ruins_ambient"
    COMBAT_NORMAL = "combat_normal"
    COMBAT_ELITE = "combat_elite"
    COMBAT_BOSS = "combat_boss"
    VICTORY = "victory_fanfare"
    DEFEAT = "defeat_dirge"


class AudioManager:
    """Gestionnaire audio complet"""

    def __init__(self, assets_path: Path = Path("assets/sounds")):
        self.assets_path = assets_path
        self.sounds: Dict[SoundType, List[pygame.mixer.Sound]] = {}
        self.music_tracks: Dict[MusicTrack, str] = {}

        # Volumes
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.ambient_volume = 0.5

        # État
        self.current_music: Optional[MusicTrack] = None
        self.music_paused = False
        self.muted = False

        # Canaux pour différents types de sons
        self.channels = {
            'ui': pygame.mixer.Channel(0),
            'combat': pygame.mixer.Channel(1),
            'effects': pygame.mixer.Channel(2),
            'ambient': pygame.mixer.Channel(3),
            'voice': pygame.mixer.Channel(4)  # Pour futurs voiceovers
        }

        # Initialiser pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Charger les sons
        self.load_all_sounds()

    def load_all_sounds(self):
        """Charge tous les fichiers audio"""
        # Mapping des types de sons vers les fichiers
        sound_files = {
            SoundType.BUTTON_CLICK: ["click_01.ogg", "click_02.ogg"],
            SoundType.CARD_DRAW: ["card_draw_01.ogg", "card_draw_02.ogg"],
            SoundType.CARD_PLAY: ["card_play.ogg"],
            SoundType.ATTACK_MELEE: ["slash_01.ogg", "slash_02.ogg", "slash_03.ogg"],
            SoundType.DAMAGE_SMALL: ["hit_small.ogg"],
            SoundType.DAMAGE_MEDIUM: ["hit_medium.ogg"],
            SoundType.DAMAGE_LARGE: ["hit_large.ogg"],
            SoundType.SHIELD_BLOCK: ["shield_block.ogg"],
            SoundType.SHIELD_BREAK: ["shield_break.ogg"],
            SoundType.POISON_APPLY: ["poison.ogg"],
            SoundType.BURN_APPLY: ["fire.ogg"],
            SoundType.HEAL: ["heal.ogg"],
            SoundType.BUFF: ["buff.ogg"],
            SoundType.DEBUFF: ["debuff.ogg"],
            SoundType.VICTORY: ["victory.ogg"],
            SoundType.DEFEAT: ["defeat.ogg"]
        }

        # Charger les sons
        for sound_type, files in sound_files.items():
            self.sounds[sound_type] = []
            for filename in files:
                filepath = self.assets_path / "sfx" / filename
                if filepath.exists():
                    sound = pygame.mixer.Sound(filepath)
                    self.sounds[sound_type].append(sound)
                else:
                    print(f"⚠️ Fichier audio manquant: {filepath}")

        # Charger les pistes musicales
        music_files = {
            MusicTrack.MENU: "music/menu_theme.ogg",
            MusicTrack.FOREST: "music/forest_ambient.ogg",
            MusicTrack.COMBAT_NORMAL: "music/combat_normal.ogg",
            MusicTrack.COMBAT_BOSS: "music/combat_boss.ogg",
            MusicTrack.VICTORY: "music/victory_fanfare.ogg"
        }

        for track, filename in music_files.items():
            filepath = self.assets_path / filename
            if filepath.exists():
                self.music_tracks[track] = str(filepath)
            else:
                print(f"⚠️ Musique manquante: {filepath}")

    def play_sound(self, sound_type: SoundType, volume_override: Optional[float] = None):
        """Joue un effet sonore"""
        if self.muted or sound_type not in self.sounds:
            return

        sounds = self.sounds[sound_type]
        if not sounds:
            return

        # Choisir une variation aléatoire
        sound = random.choice(sounds)

        # Calculer le volume
        volume = volume_override if volume_override else self.sfx_volume
        volume *= self.master_volume
        sound.set_volume(volume)

        # Choisir le canal approprié
        if sound_type in [SoundType.BUTTON_CLICK, SoundType.BUTTON_HOVER,
                          SoundType.CARD_DRAW, SoundType.CARD_PLAY]:
            channel = self.channels['ui']
        elif sound_type in [SoundType.ATTACK_MELEE, SoundType.ATTACK_RANGED,
                            SoundType.DAMAGE_SMALL, SoundType.DAMAGE_MEDIUM]:
            channel = self.channels['combat']
        else:
            channel = self.channels['effects']

        # Jouer
        channel.play(sound)

    def play_music(self, track: MusicTrack, loops: int = -1, fade_ms: int = 1000):
        """Joue une musique"""
        if self.muted or track not in self.music_tracks:
            return

        # Arrêter la musique actuelle avec fondu
        if self.current_music:
            pygame.mixer.music.fadeout(fade_ms)

        # Charger et jouer la nouvelle musique
        filepath = self.music_tracks[track]
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        pygame.mixer.music.play(loops, fade_ms=fade_ms)

        self.current_music = track

    def stop_music(self, fade_ms: int = 1000):
        """Arrête la musique"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None

    def pause_music(self):
        """Met en pause la musique"""
        pygame.mixer.music.pause()
        self.music_paused = True

    def resume_music(self):
        """Reprend la musique"""
        pygame.mixer.music.unpause()
        self.music_paused = False

    def set_master_volume(self, volume: float):
        """Définit le volume principal"""
        self.master_volume = max(0.0, min(1.0, volume))
        self.update_volumes()

    def set_music_volume(self, volume: float):
        """Définit le volume de la musique"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, volume: float):
        """Définit le volume des effets"""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def update_volumes(self):
        """Met à jour tous les volumes"""
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def toggle_mute(self):
        """Active/désactive le son"""
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def play_combat_music(self, is_boss: bool = False, is_elite: bool = False):
        """Joue la musique de combat appropriée"""
        if is_boss:
            self.play_music(MusicTrack.COMBAT_BOSS)
        elif is_elite:
            self.play_music(MusicTrack.COMBAT_ELITE)
        else:
            self.play_music(MusicTrack.COMBAT_NORMAL)

    def play_biome_music(self, biome: str):
        """Joue la musique du biome"""
        biome_tracks = {
            'forest': MusicTrack.FOREST,
            'dunes': MusicTrack.DUNES,
            'cliffs': MusicTrack.CLIFFS,
            'river': MusicTrack.RIVER,
            'volcano': MusicTrack.VOLCANO,
            'ruins': MusicTrack.RUINS
        }

        track = biome_tracks.get(biome, MusicTrack.FOREST)
        self.play_music(track)

    def play_damage_sound(self, damage: int):
        """Joue un son de dégâts selon l'intensité"""
        if damage <= 2:
            self.play_sound(SoundType.DAMAGE_SMALL)
        elif damage <= 5:
            self.play_sound(SoundType.DAMAGE_MEDIUM)
        else:
            self.play_sound(SoundType.DAMAGE_LARGE)