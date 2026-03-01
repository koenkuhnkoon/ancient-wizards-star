# ============================================================
# main.py — The Ancient Wizard's Star
#
# This is the very first file Python runs when the game starts.
# It sets up the screen, runs the character selection, and then
# kicks off the main game loop where all the action happens!
# ============================================================

import asyncio
import pygame

# We import the Player class from the game folder.
# ATTACK_DAMAGE is gone — damage is now calculated inside player.get_attack_damage()!
from game.player import Player

# Sound manager — handles all music and sound effects
from game.sound import SoundManager

# Import the World class, and the lists of where shards and potions start
from game.world   import World, VoltrakArena, SHARD_POSITIONS, HEALTH_POTION_POSITIONS, PORTAL_X, PORTAL_Y

# Import the function that creates all the enemies, plus the two mini-boss classes
from game.enemies import create_enemy_group, Grimrak, Zara, Voltrak

# Import the function that creates all the friendly NPCs (companions + villagers)
from game.npc     import create_npc_group, CompanionFighter

# Import items — factory function plus all item types we use directly
from game.items   import create_items_group, HealthPotion, BigHealthPotion, MagicalShard, PortalKey

# ── Screen & Game Constants ────────────────────────────────

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT =  720
TARGET_FPS    =   60
GAME_TITLE    = "The Ancient Wizard's Star"

# ── Background Color ───────────────────────────────────────
GRASS_GREEN = (76, 175, 80)

# ── HUD (Heads-Up Display) Constants ──────────────────────
# The HUD is the info overlay drawn on top of the game — health bars, stat bars, etc.

HEALTH_BAR_X      =  12
HEALTH_BAR_Y      =  12
HEALTH_BAR_WIDTH  = 120
HEALTH_BAR_HEIGHT =  16

# Endurance bar (used to run and attack — replaces the old "Energy" bar)
ENDURANCE_BAR_X      =  12
ENDURANCE_BAR_Y      =  34
ENDURANCE_BAR_WIDTH  = 120
ENDURANCE_BAR_HEIGHT =  16

# Strength bar — shorter secondary stat bar shown below endurance
STRENGTH_BAR_X      =  12
STRENGTH_BAR_Y      =  56
STRENGTH_BAR_WIDTH  = 120    # Same as HP and endurance bars
STRENGTH_BAR_HEIGHT =  16    # Same as HP and endurance bars

# Magic bar — sits just below the strength bar
MAGIC_BAR_X      =  12
MAGIC_BAR_Y      =  78      # 56 + 16 (height) + 6 (gap) = 78
MAGIC_BAR_WIDTH  = 120      # Same as HP and endurance bars
MAGIC_BAR_HEIGHT =  16      # Same as HP and endurance bars

# Portrait — shifted down to make room for the new stat bars
PORTRAIT_X    =  12
PORTRAIT_Y    = 100         # Was 84, now 100 to clear the strength and magic bars
PORTRAIT_SIZE =  48

HUD_LABEL_GAP_X   =   6
HUD_LABEL_NUDGE_Y =   1

# ── HUD Colors ─────────────────────────────────────────────

HEALTH_BAR_FILL_COLOR    = (231,  76,  60)   # Bright red
HEALTH_BAR_BG_COLOR      = ( 90,  26,  26)   # Dark red
ENDURANCE_BAR_FILL_COLOR = (  0, 229, 255)   # Bright cyan
ENDURANCE_BAR_BG_COLOR   = (  0,  58,  69)   # Dark cyan
STRENGTH_BAR_FILL_COLOR  = (255, 140,   0)   # Orange
STRENGTH_BAR_BG_COLOR    = ( 60,  30,   0)   # Dark orange
MAGIC_BAR_FILL_COLOR     = (160,  32, 240)   # Purple
MAGIC_BAR_BG_COLOR       = ( 40,   0,  60)   # Dark purple
PORTRAIT_BORDER_COLOR    = (245, 200,  66)   # Hero gold
OUTLINE_BLACK            = ( 26,  26,  26)   # Very dark outline
HERO_GOLD                = (245, 200,  66)   # Used for titles and highlights

# Colors used on the character selection screen
SELECT_SCREEN_BG   = ( 20,  20,  40)
SELECT_SCREEN_TEXT = (255, 255, 255)

# The six playable character classes, in the order keys 1–6 select them
CHARACTER_CLASSES = ["Wizard", "Knight", "Assassin", "Miner", "Ninja", "Robot"]

# ── Character Selection Screen Layout ─────────────────────
SELECT_TITLE_Y     =  80
SELECT_SUBTITLE_Y  = 160
SELECT_OPTIONS_Y   = 230
SELECT_OPTION_GAP  =  45
SELECT_HINT_OFFSET =  60

# ── Pause Screen Constants ─────────────────────────────────
PAUSE_OVERLAY_COLOR = (  0,   0,   0, 160)
PAUSE_PANEL_COLOR   = ( 20,  20,  40, 230)
PAUSE_TITLE_COLOR   = (245, 200,  66)
PAUSE_BODY_COLOR    = (255, 255, 255)
PAUSE_SELECT_COLOR  = (245, 200,  66)
PAUSE_PANEL_WIDTH   = 520
PAUSE_PANEL_HEIGHT  = 400
NUM_SETTINGS        = 1

# ── Level-Up Overlay Constants ─────────────────────────────
# The level-up overlay appears when the player earns a level.
# The player presses 1–4 to pick which stat to increase.

LEVELUP_PANEL_W = 560
LEVELUP_PANEL_H = 300
LEVELUP_PANEL_X = SCREEN_WIDTH  // 2 - LEVELUP_PANEL_W // 2
LEVELUP_PANEL_Y = SCREEN_HEIGHT // 2 - LEVELUP_PANEL_H // 2

# Maps key 1, 2, 3, 4 → which stat to boost
LEVELUP_OPTION_KEYS = {
    pygame.K_1: "health",
    pygame.K_2: "endurance",
    pygame.K_3: "strength",
    pygame.K_4: "magic",
}

# ── Boss Spawning Thresholds ───────────────────────────────
# Grimrak spawns when the player has collected 25 shards total.
# Zara spawns when the player has collected 50 shards total.
GRIMRAK_SPAWN_SHARDS = 25
ZARA_SPAWN_SHARDS    = 50

# Where the mini-bosses appear on the map
GRIMRAK_SPAWN_POS = (900, 300)
ZARA_SPAWN_POS    = (950, 400)

# Where the portal key drops when both mini-bosses are beaten
PORTAL_KEY_DROP_POS = (640, 300)

# Where Voltrak spawns when the portal is opened (just left of the gate)
VOLTRAK_SPAWN_POS = (880, 270)

# ── Voltrak Boss Health Bar ─────────────────────────────────
# A wide bar shown at the top-centre of the screen during the final fight.
# It tells the player how close they are to saving Lumoria!
VOLTRAK_BAR_WIDTH      = 500
VOLTRAK_BAR_HEIGHT     = 24
VOLTRAK_BAR_X          = SCREEN_WIDTH  // 2 - VOLTRAK_BAR_WIDTH  // 2
VOLTRAK_BAR_Y          = 18
VOLTRAK_BAR_FILL_COLOR = (0, 220, 255)   # Electric cyan — Voltrak's theme!
VOLTRAK_BAR_BG_COLOR   = (0, 40, 60)    # Dark teal background

# ── Respawn Points ─────────────────────────────────────────
# When the player dies, they come back at the first respawn point.
# (We'll add logic to pick the nearest one later!)
RESPAWN_POINTS = [
    (640, 360),   # Center of the map — the starting spot
    (200, 300),   # Near the first villager
    (850, 450),   # Right side of the map
]

# Total lives before the run ends in game over.
MAX_LIVES = 3


# ============================================================
# PROJECTILE CLASS — flying weapons!
#
# When the Ninja throws a shuriken or the Robot fires a laser,
# a Projectile is created here. It flies across the screen and
# damages whatever enemy it hits first.
# ============================================================

class Projectile:
    """A flying weapon shot by the Ninja (shuriken) or Robot (laser).

    It moves across the screen until it hits an enemy or travels too far.
    dx, dy -- direction of travel (normalised to speed pixels per frame)
    weapon  -- "shuriken" or "laser" — affects size, colour, and damage
    """
    SHURIKEN_SPEED  = 8    # pixels per frame
    LASER_SPEED     = 12   # lasers are faster!
    SHURIKEN_SIZE   = 14   # pixel width and height of the shuriken
    LASER_W, LASER_H = 24, 8   # laser beam rectangle

    SHURIKEN_COLOR = (200, 220, 255)   # silver-blue fallback
    LASER_COLOR    = (0, 230, 255)     # bright cyan fallback

    MAX_TRAVEL = 600   # despawn after travelling this many pixels

    # Sprite frames — loaded once by Projectile.load_sprites() after pygame.init()
    _shuriken_frames: list = []   # 4 spinning frames from fx_projectile_shuriken.png
    _laser_frames: list    = []   # 2 frames from fx_projectile_laser.png

    @classmethod
    def load_sprites(cls):
        """Load projectile sprite sheets from disk.

        Called once in main() after pygame.display.set_mode() so
        convert_alpha() works correctly.
        """
        def _slice(path, fw, fh, n):
            try:
                sheet = pygame.image.load(path).convert_alpha()
                return [sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh)) for i in range(n)]
            except Exception:
                return []   # Fall back to coloured rect if file is missing

        cls._shuriken_frames = _slice(
            "assets/fx_projectile_shuriken.png", cls.SHURIKEN_SIZE, cls.SHURIKEN_SIZE, 4)
        cls._laser_frames = _slice(
            "assets/fx_projectile_laser.png", cls.LASER_W, cls.LASER_H, 2)

    def __init__(self, x, y, dx, dy, weapon, damage):
        self.x       = float(x)
        self.y       = float(y)
        self.dx      = dx   # velocity x (pixels/frame)
        self.dy      = dy   # velocity y (pixels/frame)
        self.weapon  = weapon
        self.damage  = damage
        self.alive   = True
        self.travelled = 0.0   # total distance moved so far

    def update(self):
        """Move the projectile one frame. Return False when it should be removed."""
        if not self.alive:
            return False
        self.x  += self.dx
        self.y  += self.dy
        step = (self.dx ** 2 + self.dy ** 2) ** 0.5
        self.travelled += step
        if self.travelled >= self.MAX_TRAVEL:
            self.alive = False
        return self.alive

    def get_rect(self):
        """The collision rectangle of this projectile."""
        if self.weapon == "shuriken":
            return pygame.Rect(int(self.x), int(self.y),
                               self.SHURIKEN_SIZE, self.SHURIKEN_SIZE)
        else:   # laser
            return pygame.Rect(int(self.x), int(self.y),
                               self.LASER_W, self.LASER_H)

    def draw(self, screen):
        """Draw the projectile using its sprite sheet, or a coloured rectangle as fallback."""
        if not self.alive:
            return
        rect = self.get_rect()
        frames = self._shuriken_frames if self.weapon == "shuriken" else self._laser_frames
        if frames:
            # Cycle through frames as the projectile flies — gives a spinning/pulsing look
            idx = int(self.travelled / 20) % len(frames)
            screen.blit(frames[idx], (rect.x, rect.y))
        else:
            # Fallback: coloured rectangle if sprites couldn't be loaded
            color = self.SHURIKEN_COLOR if self.weapon == "shuriken" else self.LASER_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)


# ============================================================
# ATTACK EFFECT CLASS — brief flash when a melee weapon swings
#
# When the player hits Space with a sword, pickaxe, etc., a
# coloured flash appears showing EXACTLY where the weapon hit.
# It fades out after about 0.2 seconds (12 frames at 60 FPS).
# ============================================================

class AttackEffect:
    """A brief visual flash showing the area of a melee attack.

    Drawn using the fx_attack_*.png sprite sheets for EFFECT_DURATION frames,
    then it disappears automatically.
    Falls back to a coloured rectangle if the art file isn't loaded yet.
    """
    EFFECT_DURATION = 12   # frames (0.2 seconds at 60 FPS) — default for all weapons

    # Some weapons linger longer — or shorter — than the default 12 frames
    WEAPON_DURATIONS = {
        "laser":       44,   # 0.73 s — the beam hangs in the air a good moment
        "enemy_melee":  8,   # 0.13 s — short, sharp red flash when an enemy hits the player
    }

    # Fallback colours per weapon — used if sprites haven't loaded
    COLORS = {
        "staff":       (160,  80, 255, 140),   # purple burst
        "sword":       (255, 230,  80, 140),   # golden slash
        "daggers":     (200, 200, 255, 140),   # silver thrust
        "pickaxe":     (200, 120,  40, 140),   # orange arc
        "laser":       (  0, 230, 255, 220),   # bright cyan beam
        "enemy_melee": (255,  50,  50, 180),   # red flash — shown when ANY enemy hits the player
    }

    # Sprite frames per weapon — filled by load_sprites() after pygame.init()
    _frames: dict = {}

    @classmethod
    def load_sprites(cls):
        """Load all attack effect sprite sheets from disk.

        Each sheet is a horizontal strip of animation frames.
        Called once in main() after pygame.display.set_mode() so
        convert_alpha() works correctly.
        """
        # weapon → (filepath, frame_width, frame_height, num_frames)
        specs = {
            "staff":   ("assets/fx_attack_staff.png",   100, 100, 4),
            "sword":   ("assets/fx_attack_sword.png",    80,  50, 4),
            "daggers": ("assets/fx_attack_daggers.png",  40,  32, 2),
            "pickaxe": ("assets/fx_attack_pickaxe.png", 110,  40, 4),
        }
        for weapon, (path, fw, fh, n) in specs.items():
            try:
                sheet = pygame.image.load(path).convert_alpha()
                cls._frames[weapon] = [
                    sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh))
                    for i in range(n)
                ]
            except Exception:
                cls._frames[weapon] = []   # Will fall back to coloured rect

    def __init__(self, rects, weapon_type):
        """rects -- list of pygame.Rect zones to highlight"""
        self.rects      = rects
        self.weapon     = weapon_type
        duration        = self.WEAPON_DURATIONS.get(weapon_type, self.EFFECT_DURATION)
        self.timer      = duration
        self.max_timer  = duration   # kept for the fade-out ratio calculation
        self.alive      = True

    def update(self):
        """Count down the timer — when it reaches 0, the effect disappears."""
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen):
        """Draw the attack effect using its sprite sheet, or a coloured fallback."""
        if not self.alive:
            return

        frames = self._frames.get(self.weapon, [])
        # Fade out over the effect's lifetime (1.0 at start → 0.0 at end)
        fade = self.timer / self.max_timer

        if frames:
            num_frames = len(frames)
            # Play the animation forward: frame 0 at swing start, last frame just before fade
            idx = min(int((1.0 - fade) * num_frames), num_frames - 1)
            frame = frames[idx].copy()   # Copy so set_alpha doesn't affect the shared sheet
            frame.set_alpha(int(255 * fade))
            for rect in self.rects:
                fw, fh = frame.get_size()
                if rect.width != fw or rect.height != fh:
                    # Facing up/down swaps width/height — rotate the frame to match
                    if rect.height > rect.width:
                        blit_frame = pygame.transform.rotate(frame, 90)
                    else:
                        blit_frame = pygame.transform.scale(frame, (rect.width, rect.height))
                else:
                    blit_frame = frame
                screen.blit(blit_frame, (rect.x, rect.y))
        else:
            # Fallback: semi-transparent coloured rectangle
            alpha = int(180 * fade)
            color_base = self.COLORS.get(self.weapon, (255, 255, 255, 140))
            color = (color_base[0], color_base[1], color_base[2], alpha)
            surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            for rect in self.rects:
                pygame.draw.rect(surf, color, rect, border_radius=6)
            screen.blit(surf, (0, 0))


# ── Helper: Draw Voltrak's Boss Health Bar ─────────────────

def draw_voltrak_boss_bar(screen, voltrak, bar_font):
    """Draw Voltrak's health bar at the top-centre of the screen.

    This big bar tells the player how much health the final boss has left.
    It only shows while Voltrak is alive and fighting.

    voltrak  -- the Voltrak boss object
    bar_font -- the font used for the label underneath the bar
    """
    # Dark teal background — the "empty" part of the health bar
    bg_rect = pygame.Rect(VOLTRAK_BAR_X, VOLTRAK_BAR_Y, VOLTRAK_BAR_WIDTH, VOLTRAK_BAR_HEIGHT)
    pygame.draw.rect(screen, VOLTRAK_BAR_BG_COLOR, bg_rect)

    # Cyan fill — shrinks as Voltrak takes damage
    fraction = voltrak.health / voltrak.max_health
    fill_w   = int(VOLTRAK_BAR_WIDTH * fraction)
    if fill_w > 0:
        pygame.draw.rect(screen, VOLTRAK_BAR_FILL_COLOR,
            pygame.Rect(VOLTRAK_BAR_X, VOLTRAK_BAR_Y, fill_w, VOLTRAK_BAR_HEIGHT))

    # Phase 2 tint: overlay orange when Voltrak is in his angry second phase!
    if voltrak.health <= voltrak.max_health // 2:
        phase_surf = pygame.Surface((fill_w, VOLTRAK_BAR_HEIGHT), pygame.SRCALPHA)
        phase_surf.fill((255, 120, 0, 70))   # Orange-tinted, semi-transparent
        screen.blit(phase_surf, (VOLTRAK_BAR_X, VOLTRAK_BAR_Y))

    # Thin white outline around the bar
    pygame.draw.rect(screen, (220, 220, 220), bg_rect, width=1)

    # Label underneath the bar
    label = bar_font.render("VOLTRAK  THE SHOCKBLADE EEL", True, HERO_GOLD)
    label_x = SCREEN_WIDTH // 2 - label.get_width() // 2
    screen.blit(label, (label_x, VOLTRAK_BAR_Y + VOLTRAK_BAR_HEIGHT + 3))


# ── Helper: Draw the Victory Screen ────────────────────────

def draw_victory_screen(screen, title_font, body_font):
    """Show the victory overlay when Voltrak is defeated.

    A deep purple overlay with golden text celebrating the win.
    The player can press ESC to return to the title screen.

    title_font -- big bold font for the main celebration line
    body_font  -- smaller font for the sub-text and hint
    """
    # Dark gold overlay — celebratory and warm
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((120, 80, 0, 180))
    screen.blit(overlay, (0, 0))

    # Big celebration line
    title = title_font.render("YOU SAVED LUMORIA!", True, HERO_GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 90))

    # Story text
    sub1 = body_font.render("Voltrak the Shockblade Eel has been defeated!", True, (255, 238, 190))
    screen.blit(sub1, (SCREEN_WIDTH // 2 - sub1.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    sub2 = body_font.render("The Ancient Wizard's Star shines safely again!", True, (255, 250, 220))
    screen.blit(sub2, (SCREEN_WIDTH // 2 - sub2.get_width() // 2, SCREEN_HEIGHT // 2 + 14))

    # Hint
    hint = body_font.render("Press Space to return to the menu", True, (180, 180, 180))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    # Touch return button
    return_rect = get_end_screen_return_rect()
    pygame.draw.rect(screen, (80, 110, 60), return_rect, border_radius=10)
    return_text = body_font.render("Return to Menu", True, (255, 255, 255))
    screen.blit(return_text, (return_rect.centerx - return_text.get_width() // 2,
                              return_rect.centery - return_text.get_height() // 2))


# ── Helper: Draw the HUD ───────────────────────────────────

def draw_hud(screen, player, hud_font):
    """Draw the health bar, endurance bar, strength bar, magic bar, and portrait."""

    # ── Health Bar ─────────────────────────────────────────
    health_bg_rect = pygame.Rect(HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, health_bg_rect)

    health_fill_width = int(HEALTH_BAR_WIDTH * player.get_health_fraction())
    if health_fill_width > 0:
        pygame.draw.rect(screen, HEALTH_BAR_FILL_COLOR,
            pygame.Rect(HEALTH_BAR_X, HEALTH_BAR_Y, health_fill_width, HEALTH_BAR_HEIGHT))

    pygame.draw.rect(screen, OUTLINE_BLACK, health_bg_rect, width=1)

    # ── Endurance Bar ──────────────────────────────────────
    # (Used to run and attack — fills back up when resting)
    endurance_bg_rect = pygame.Rect(ENDURANCE_BAR_X, ENDURANCE_BAR_Y,
                                    ENDURANCE_BAR_WIDTH, ENDURANCE_BAR_HEIGHT)
    pygame.draw.rect(screen, ENDURANCE_BAR_BG_COLOR, endurance_bg_rect)

    endurance_fill_width = int(ENDURANCE_BAR_WIDTH * player.get_endurance_fraction())
    if endurance_fill_width > 0:
        pygame.draw.rect(screen, ENDURANCE_BAR_FILL_COLOR,
            pygame.Rect(ENDURANCE_BAR_X, ENDURANCE_BAR_Y,
                        endurance_fill_width, ENDURANCE_BAR_HEIGHT))

    pygame.draw.rect(screen, OUTLINE_BLACK, endurance_bg_rect, width=1)

    # ── Strength Bar ───────────────────────────────────────
    # (Orange — shows physical power; grows when you level up Strength)
    strength_bg_rect = pygame.Rect(STRENGTH_BAR_X, STRENGTH_BAR_Y,
                                   STRENGTH_BAR_WIDTH, STRENGTH_BAR_HEIGHT)
    pygame.draw.rect(screen, STRENGTH_BAR_BG_COLOR, strength_bg_rect)

    strength_fill_width = int(STRENGTH_BAR_WIDTH * player.get_strength_fraction())
    if strength_fill_width > 0:
        pygame.draw.rect(screen, STRENGTH_BAR_FILL_COLOR,
            pygame.Rect(STRENGTH_BAR_X, STRENGTH_BAR_Y,
                        strength_fill_width, STRENGTH_BAR_HEIGHT))

    pygame.draw.rect(screen, OUTLINE_BLACK, strength_bg_rect, width=1)

    # ── Magic Bar ──────────────────────────────────────────
    # (Purple — shows magical power; grows when you level up Magic)
    magic_bg_rect = pygame.Rect(MAGIC_BAR_X, MAGIC_BAR_Y,
                                 MAGIC_BAR_WIDTH, MAGIC_BAR_HEIGHT)
    pygame.draw.rect(screen, MAGIC_BAR_BG_COLOR, magic_bg_rect)

    magic_fill_width = int(MAGIC_BAR_WIDTH * player.get_magic_fraction())
    if magic_fill_width > 0:
        pygame.draw.rect(screen, MAGIC_BAR_FILL_COLOR,
            pygame.Rect(MAGIC_BAR_X, MAGIC_BAR_Y,
                        magic_fill_width, MAGIC_BAR_HEIGHT))

    pygame.draw.rect(screen, OUTLINE_BLACK, magic_bg_rect, width=1)

    # ── Character Portrait ─────────────────────────────────
    portrait_rect = pygame.Rect(PORTRAIT_X, PORTRAIT_Y, PORTRAIT_SIZE, PORTRAIT_SIZE)
    portrait_surface = player.get_portrait_surface(PORTRAIT_SIZE)
    screen.blit(portrait_surface, (PORTRAIT_X, PORTRAIT_Y))
    pygame.draw.rect(screen, PORTRAIT_BORDER_COLOR, portrait_rect, width=3)

    # ── HUD Labels ─────────────────────────────────────────

    hp_label = hud_font.render(f"HP  {player.health}/{player.max_health}", True, (255, 255, 255))
    screen.blit(hp_label, (HEALTH_BAR_X + HEALTH_BAR_WIDTH + HUD_LABEL_GAP_X,
                            HEALTH_BAR_Y + HUD_LABEL_NUDGE_Y))

    en_label = hud_font.render(f"EN  {player.endurance}/{player.max_endurance}", True, (255, 255, 255))
    screen.blit(en_label, (ENDURANCE_BAR_X + ENDURANCE_BAR_WIDTH + HUD_LABEL_GAP_X,
                            ENDURANCE_BAR_Y + HUD_LABEL_NUDGE_Y))

    # Strength and magic labels — sit to the right of their (shorter) bars
    str_label = hud_font.render(f"STR {player.strength}", True, (255, 200, 100))
    screen.blit(str_label, (STRENGTH_BAR_X + STRENGTH_BAR_WIDTH + HUD_LABEL_GAP_X,
                             STRENGTH_BAR_Y))

    mag_label = hud_font.render(f"MAG {player.magic}", True, (200, 150, 255))
    screen.blit(mag_label, (MAGIC_BAR_X + MAGIC_BAR_WIDTH + HUD_LABEL_GAP_X,
                             MAGIC_BAR_Y))


# ── Helper: Draw the Level-Up Overlay ─────────────────────

def draw_level_up_overlay(screen, player, level_up_fonts, level_up_surfaces):
    """Draw the level-up choice screen on top of the game.

    The game freezes while this is showing. The player presses 1, 2, 3, or 4
    to pick which stat they want to increase!

    level_up_fonts    — dict with 'title' and 'body' font objects
    level_up_surfaces — dict with pre-built 'dim' and 'panel' surfaces
    """

    # Dim the whole game world behind the panel
    screen.blit(level_up_surfaces["dim"], (0, 0))

    # Draw the dark panel in the center of the screen
    screen.blit(level_up_surfaces["panel"], (LEVELUP_PANEL_X, LEVELUP_PANEL_Y))
    pygame.draw.rect(screen, HERO_GOLD,
        pygame.Rect(LEVELUP_PANEL_X, LEVELUP_PANEL_Y, LEVELUP_PANEL_W, LEVELUP_PANEL_H), width=2)

    # Big gold title at the top of the panel
    new_level = player.level + 1   # Show what level they'll reach after choosing
    title_text = f"LEVEL UP!  You are now Level {new_level}!"
    title = level_up_fonts["title"].render(title_text, True, HERO_GOLD)
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    screen.blit(title, (title_x, LEVELUP_PANEL_Y + 20))

    # Subtitle
    sub = level_up_fonts["body"].render("Choose a stat to increase:", True, (255, 255, 255))
    sub_x = SCREEN_WIDTH // 2 - sub.get_width() // 2
    screen.blit(sub, (sub_x, LEVELUP_PANEL_Y + 70))

    # The four options — each shows the key, the stat name, and a preview of the new value
    options = [
        ("1", "Health",    f"+2 Max HP     (now {player.max_health + 2})"),
        ("2", "Endurance", f"+2 Max EN     (now {player.max_endurance + 2})"),
        ("3", "Strength",  f"+1 STR        (now {player.strength + 1})"),
        ("4", "Magic",     f"+1 MAG        (now {player.magic + 1})"),
    ]

    for i, (key_label, stat_name, preview) in enumerate(options):
        line_text = f"  {key_label}  —  {stat_name}:  {preview}"
        line_surface = level_up_fonts["body"].render(line_text, True, (255, 255, 255))
        line_x = SCREEN_WIDTH // 2 - line_surface.get_width() // 2
        line_y = LEVELUP_PANEL_Y + 110 + i * 38
        screen.blit(line_surface, (line_x, line_y))


def get_level_up_touch_targets(player, level_up_fonts):
    """Return tap targets for the 4 level-up choices."""
    options = [
        ("health",    f"  1  —  Health:  +2 Max HP     (now {player.max_health + 2})"),
        ("endurance", f"  2  —  Endurance:  +2 Max EN     (now {player.max_endurance + 2})"),
        ("strength",  f"  3  —  Strength:  +1 STR        (now {player.strength + 1})"),
        ("magic",     f"  4  —  Magic:  +1 MAG        (now {player.magic + 1})"),
    ]
    targets = []
    for i, (stat_id, line_text) in enumerate(options):
        line_surface = level_up_fonts["body"].render(line_text, True, (255, 255, 255))
        line_x = SCREEN_WIDTH // 2 - line_surface.get_width() // 2
        line_y = LEVELUP_PANEL_Y + 110 + i * 38
        rect = pygame.Rect(line_x - 12, line_y - 4,
                           line_surface.get_width() + 24, line_surface.get_height() + 10)
        targets.append((stat_id, rect))
    return targets


# ── Helper: Draw the Death Screen ─────────────────────────

def draw_death_screen(screen, death_font, lives_remaining):
    """Show a 'You died! Respawning...' message centered on screen.

    We draw this ON TOP of the game world so the player can see
    where they fell before respawning.
    """
    msg = death_font.render("You died!  Respawning...", True, (231, 76, 60))
    msg_x = SCREEN_WIDTH  // 2 - msg.get_width()  // 2
    msg_y = SCREEN_HEIGHT // 2 - msg.get_height() // 2
    screen.blit(msg, (msg_x, msg_y))

    lives_msg = death_font.render(f"Lives left: {lives_remaining}", True, (245, 200, 66))
    lives_x = SCREEN_WIDTH // 2 - lives_msg.get_width() // 2
    screen.blit(lives_msg, (lives_x, msg_y + 42))


def draw_game_over_screen(screen, title_font, body_font):
    """Draw a full game-over overlay after all lives are used."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 10, 220))
    screen.blit(overlay, (0, 0))

    title = title_font.render("GAME OVER", True, (231, 76, 60))
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    screen.blit(title, (title_x, SCREEN_HEIGHT // 2 - 85))

    body = body_font.render("You ran out of lives in Lumoria.", True, (230, 230, 230))
    body_x = SCREEN_WIDTH // 2 - body.get_width() // 2
    screen.blit(body, (body_x, SCREEN_HEIGHT // 2 - 20))

    hint = body_font.render("Press Space or ESC to return to the menu", True, (180, 180, 180))
    hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
    screen.blit(hint, (hint_x, SCREEN_HEIGHT // 2 + 30))

    return_rect = get_end_screen_return_rect()
    pygame.draw.rect(screen, (80, 110, 60), return_rect, border_radius=10)
    return_text = body_font.render("Return to Menu", True, (255, 255, 255))
    screen.blit(return_text, (return_rect.centerx - return_text.get_width() // 2,
                              return_rect.centery - return_text.get_height() // 2))


def get_end_screen_return_rect():
    """Shared touch target for victory/game-over return button."""
    width = min(460, SCREEN_WIDTH - 120)
    return pygame.Rect(SCREEN_WIDTH // 2 - width // 2, SCREEN_HEIGHT // 2 + 90, width, 50)


# ── Helper: Draw the "ESC = Menu" hint ────────────────────

def draw_esc_hint(screen, hint_font):
    """Draw a small hint in the bottom-right corner reminding the player how to return to the menu."""
    hint_surface = hint_font.render("ESC = Menu", True, (200, 200, 200))
    hint_x = SCREEN_WIDTH  - hint_surface.get_width()  - 10
    hint_y = SCREEN_HEIGHT - hint_surface.get_height() - 10
    screen.blit(hint_surface, (hint_x, hint_y))


def get_pointer_pos(event):
    """Return pixel coordinates for mouse/touch events, or None."""
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        return event.pos
    if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
        surface = pygame.display.get_surface()
        if surface is not None:
            sw, sh = surface.get_size()
        else:
            sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        return (int(event.x * sw), int(event.y * sh))
    return None


def get_orientation(screen_w, screen_h):
    """Return the logical orientation for touch layout."""
    if screen_w >= screen_h:
        return "landscape"
    return "portrait"


def build_touch_layout(screen_w, screen_h, orientation):
    """Return touch-control geometry for the current orientation."""
    pad = 16
    base = max(72, int(min(screen_w, screen_h) * 0.11))
    joystick_radius = max(70, int(base * 1.2))
    attack_radius = max(48, int(base * 0.95))
    interact_radius = max(38, int(base * 0.68))
    pause_radius = max(24, int(base * 0.45))
    # Larger invisible tap zones are much more forgiving on phone screens.
    attack_hit_radius = max(attack_radius + 18, int(attack_radius * 1.45))
    interact_hit_radius = max(interact_radius + 10, int(interact_radius * 1.20))
    pause_hit_radius = max(pause_radius + 8, int(pause_radius * 1.25))

    if orientation == "portrait":
        joy_center = (pad + joystick_radius, screen_h - pad - joystick_radius - 40)
        atk_center = (screen_w - pad - attack_radius, screen_h - pad - attack_radius - 20)
        interact_center = (
            screen_w - pad - attack_radius - interact_radius * 2 - 20,
            screen_h - pad - interact_radius - 90
        )
    else:
        joy_center = (pad + joystick_radius, screen_h - pad - joystick_radius)
        atk_center = (screen_w - pad - attack_radius, screen_h - pad - attack_radius)
        interact_center = (
            screen_w - pad - attack_radius - interact_radius * 2 - 26,
            screen_h - pad - interact_radius - 18
        )

    pause_center = (screen_w - pad - pause_radius, pad + pause_radius)
    return {
        "joystick_center": joy_center,
        "joystick_radius": joystick_radius,
        "knob_radius": max(24, int(joystick_radius * 0.40)),
        "attack_center": atk_center,
        "attack_radius": attack_radius,
        "attack_hit_radius": attack_hit_radius,
        "interact_center": interact_center,
        "interact_radius": interact_radius,
        "interact_hit_radius": interact_hit_radius,
        "pause_center": pause_center,
        "pause_radius": pause_radius,
        "pause_hit_radius": pause_hit_radius,
    }


class TouchControls:
    """Virtual joystick + action buttons for touchscreen play."""

    DEAD_ZONE = 0.22
    RUN_THRESHOLD = 0.72

    def __init__(self, hud_font):
        self.hud_font = hud_font
        self.layout = {}
        self.orientation = "landscape"
        self.update_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.move_pointer_id = None
        self.move_vector = (0.0, 0.0)

        self.attack_tapped = False
        self.interact_tapped = False
        self.pause_tapped = False

        self.interact_enabled = False
        self.interact_label = "USE"

    def update_layout(self, screen_w, screen_h):
        self.orientation = get_orientation(screen_w, screen_h)
        self.layout = build_touch_layout(screen_w, screen_h, self.orientation)

    def set_interact(self, enabled, label):
        self.interact_enabled = enabled
        self.interact_label = label if enabled else "USE"

    def begin_frame(self):
        self.attack_tapped = False
        self.interact_tapped = False
        self.pause_tapped = False

    def _pointer_id(self, event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            return ("finger", event.finger_id)
        return ("mouse", 0)

    def _distance_sq(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return dx * dx + dy * dy

    def _set_move_vector_from_pos(self, pos):
        cx, cy = self.layout["joystick_center"]
        radius = float(self.layout["joystick_radius"])
        nx = max(-1.0, min(1.0, (pos[0] - cx) / radius))
        ny = max(-1.0, min(1.0, (pos[1] - cy) / radius))
        self.move_vector = (nx, ny)

    def _clear_move_if_matching_pointer(self, pointer_id):
        if self.move_pointer_id == pointer_id:
            self.move_pointer_id = None
            self.move_vector = (0.0, 0.0)

    def handle_event(self, event):
        pos = get_pointer_pos(event)
        if pos is None:
            return
        pointer_id = self._pointer_id(event)

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 1) != 1:
                return
            if event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", 1) != 1:
                return
            if event.type == pygame.MOUSEMOTION and not getattr(event, "buttons", (0, 0, 0))[0]:
                return

        if event.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
            if self._distance_sq(pos, self.layout["joystick_center"]) <= self.layout["joystick_radius"] ** 2:
                self.move_pointer_id = pointer_id
                self._set_move_vector_from_pos(pos)
                return
            if self._distance_sq(pos, self.layout["attack_center"]) <= self.layout["attack_hit_radius"] ** 2:
                self.attack_tapped = True
                return
            if self.interact_enabled and (
                self._distance_sq(pos, self.layout["interact_center"]) <= self.layout["interact_hit_radius"] ** 2
            ):
                self.interact_tapped = True
                return
            if self._distance_sq(pos, self.layout["pause_center"]) <= self.layout["pause_hit_radius"] ** 2:
                self.pause_tapped = True
                return

        if event.type in (pygame.FINGERMOTION, pygame.MOUSEMOTION):
            if self.move_pointer_id == pointer_id:
                self._set_move_vector_from_pos(pos)
            return

        if event.type in (pygame.FINGERUP, pygame.MOUSEBUTTONUP):
            self._clear_move_if_matching_pointer(pointer_id)

    def get_player_input(self):
        nx, ny = self.move_vector
        mag_sq = nx * nx + ny * ny
        if mag_sq < self.DEAD_ZONE * self.DEAD_ZONE:
            return {"left": False, "right": False, "up": False, "down": False, "run": False}
        mag = mag_sq ** 0.5
        return {
            "left": nx < -self.DEAD_ZONE,
            "right": nx > self.DEAD_ZONE,
            "up": ny < -self.DEAD_ZONE,
            "down": ny > self.DEAD_ZONE,
            "run": mag >= self.RUN_THRESHOLD,
        }

    def draw(self, screen):
        # Joystick base + knob
        joy_center = self.layout["joystick_center"]
        joy_radius = self.layout["joystick_radius"]
        pygame.draw.circle(screen, (40, 40, 40), joy_center, joy_radius)
        pygame.draw.circle(screen, (200, 200, 200), joy_center, joy_radius, 3)
        knob_x = int(joy_center[0] + self.move_vector[0] * joy_radius * 0.6)
        knob_y = int(joy_center[1] + self.move_vector[1] * joy_radius * 0.6)
        pygame.draw.circle(screen, (220, 220, 220), (knob_x, knob_y), self.layout["knob_radius"])

        # Attack button
        pygame.draw.circle(screen, (200, 35, 35), self.layout["attack_center"], self.layout["attack_radius"])
        pygame.draw.circle(screen, (255, 255, 255), self.layout["attack_center"], self.layout["attack_radius"], 2)
        atk = self.hud_font.render("ATK", True, (255, 255, 255))
        screen.blit(atk, (self.layout["attack_center"][0] - atk.get_width() // 2,
                          self.layout["attack_center"][1] - atk.get_height() // 2))

        # Interact button (context sensitive)
        if self.interact_enabled:
            pygame.draw.circle(screen, (180, 120, 20),
                               self.layout["interact_center"], self.layout["interact_radius"])
            use_surf = self.hud_font.render(self.interact_label, True, (255, 255, 255))
            screen.blit(use_surf, (self.layout["interact_center"][0] - use_surf.get_width() // 2,
                                   self.layout["interact_center"][1] - use_surf.get_height() // 2))

        # Pause button
        pygame.draw.circle(screen, (30, 30, 30), self.layout["pause_center"], self.layout["pause_radius"])
        pause_surf = self.hud_font.render("II", True, (245, 200, 66))
        screen.blit(pause_surf, (self.layout["pause_center"][0] - pause_surf.get_width() // 2,
                                 self.layout["pause_center"][1] - pause_surf.get_height() // 2))


# ── Helper: Draw the Pause Overlay ────────────────────────

def draw_pause_overlay(screen, pause_fonts, pause_surfaces, audio_enabled, selected_setting_index):
    """Draw the full-screen pause overlay with CONTROLS and SETTINGS sections."""

    screen.blit(pause_surfaces["dim"], (0, 0))

    panel_x = SCREEN_WIDTH  // 2 - PAUSE_PANEL_WIDTH  // 2
    panel_y = SCREEN_HEIGHT // 2 - PAUSE_PANEL_HEIGHT // 2

    screen.blit(pause_surfaces["panel"], (panel_x, panel_y))
    panel_rect = pygame.Rect(panel_x, panel_y, PAUSE_PANEL_WIDTH, PAUSE_PANEL_HEIGHT)
    pygame.draw.rect(screen, HERO_GOLD, panel_rect, width=2)

    title_surface = pause_fonts["title"].render("PAUSED", True, PAUSE_TITLE_COLOR)
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
    screen.blit(title_surface, (title_x, panel_y + 20))

    controls_heading = pause_fonts["section"].render("CONTROLS", True, PAUSE_TITLE_COLOR)
    screen.blit(controls_heading, (panel_x + 30, panel_y + 80))

    controls_list = [
        "Arrow Keys / WASD  =  Move",
        "Shift              =  Run (costs Endurance)",
        "Space              =  Attack (costs Endurance)",
        "Touch Joystick     =  Move / Run",
        "Touch Buttons      =  ATK / USE / Pause",
        "P                  =  Pause / Unpause",
        "ESC                =  Return to Menu",
    ]

    for line_index, control_text in enumerate(controls_list):
        line_surface = pause_fonts["body"].render(control_text, True, PAUSE_BODY_COLOR)
        line_y = panel_y + 108 + line_index * 23
        screen.blit(line_surface, (panel_x + 30, line_y))

    settings_heading = pause_fonts["section"].render("SETTINGS", True, PAUSE_TITLE_COLOR)
    screen.blit(settings_heading, (panel_x + 30, panel_y + 248))

    audio_state_text = "ON" if audio_enabled else "OFF"
    audio_color = PAUSE_SELECT_COLOR if selected_setting_index == 0 else PAUSE_BODY_COLOR

    if selected_setting_index == 0:
        arrow_surface = pause_fonts["body"].render(">", True, PAUSE_SELECT_COLOR)
        screen.blit(arrow_surface, (panel_x + 15, panel_y + 278))

    audio_surface = pause_fonts["body"].render(f"Audio:  {audio_state_text}", True, audio_color)
    screen.blit(audio_surface, (panel_x + 30, panel_y + 278))

    # Touch-friendly pause actions on the right side
    pause_targets = get_pause_touch_targets()
    pygame.draw.rect(screen, (60, 110, 80), pause_targets["resume"], border_radius=8)
    pygame.draw.rect(screen, (120, 60, 60), pause_targets["menu"], border_radius=8)
    resume_surf = pause_fonts["body"].render("Resume", True, (255, 255, 255))
    menu_surf = pause_fonts["body"].render("Main Menu", True, (255, 255, 255))
    screen.blit(resume_surf, (pause_targets["resume"].centerx - resume_surf.get_width() // 2,
                              pause_targets["resume"].centery - resume_surf.get_height() // 2))
    screen.blit(menu_surf, (pause_targets["menu"].centerx - menu_surf.get_width() // 2,
                            pause_targets["menu"].centery - menu_surf.get_height() // 2))

    footer_text = "Tap Resume/Audio/Menu  |  P/ESC = Unpause  |  Enter/Space = Toggle"
    footer_surface = pause_fonts["body"].render(footer_text, True, (160, 160, 160))
    footer_x = SCREEN_WIDTH // 2 - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, panel_y + PAUSE_PANEL_HEIGHT - 35))


def get_pause_touch_targets():
    """Return tap targets for pause actions."""
    panel_x = SCREEN_WIDTH  // 2 - PAUSE_PANEL_WIDTH  // 2
    panel_y = SCREEN_HEIGHT // 2 - PAUSE_PANEL_HEIGHT // 2
    targets = {
        "resume": pygame.Rect(panel_x + 320, panel_y + 250, 160, 36),
        "audio":  pygame.Rect(panel_x + 20, panel_y + 270, 220, 34),
        "menu":   pygame.Rect(panel_x + 320, panel_y + 300, 160, 36),
    }
    return targets


# ── Story Intro Screen ─────────────────────────────────────

async def run_story_intro(screen, clock, fonts):
    """Show a two-screen story intro before the game starts."""

    intro_screens = [
        [
            "The world of Lumoria was once filled with magic.",
            "The Ancient Wizard's Star kept everything peaceful and bright.",
            "But Voltrak the Shockblade Eel cracked open the Dimensional Portal Gate",
            "and sent monsters flooding into the world. Lumoria is in danger!",
        ],
        [
            "YOUR QUEST:",
            "",
            "Collect magical shards dropped by defeated monsters.",
            "Defeat the two helper-bosses: Grimrak and Zara.",
            "Light the Ancient Dimensional Portal Gate.",
            "Then face Voltrak himself — and save Lumoria!",
        ],
    ]

    for screen_lines in intro_screens:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    waiting = False

            screen.fill(SELECT_SCREEN_BG)

            y_cursor = 180
            for line in screen_lines:
                if line == "YOUR QUEST:":
                    text_surface = fonts["small_bold"].render(line, True, HERO_GOLD)
                elif line == "":
                    y_cursor += 20
                    continue
                else:
                    text_surface = fonts["small"].render(line, True, SELECT_SCREEN_TEXT)

                text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
                screen.blit(text_surface, (text_x, y_cursor))
                y_cursor += 44

            hint = fonts["hint"].render("Press Space/Enter or tap to continue", True, HERO_GOLD)
            hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
            screen.blit(hint, (hint_x, SCREEN_HEIGHT - SELECT_HINT_OFFSET))

            pygame.display.flip()
            clock.tick(TARGET_FPS)
            await asyncio.sleep(0)

    return True


# ── Helper: Character Selection Screen ────────────────────

async def run_character_selection(screen, clock, fonts):
    """Show the character selection screen and return the class the player chose."""

    chosen_class = None
    option_hitboxes = []

    key_to_class = {
        pygame.K_1: CHARACTER_CLASSES[0],
        pygame.K_2: CHARACTER_CLASSES[1],
        pygame.K_3: CHARACTER_CLASSES[2],
        pygame.K_4: CHARACTER_CLASSES[3],
        pygame.K_5: CHARACTER_CLASSES[4],
        pygame.K_6: CHARACTER_CLASSES[5],
    }

    for index, class_name in enumerate(CHARACTER_CLASSES):
        option_text = f"  {index + 1}  —  {class_name}"
        option_surface = fonts["small"].render(option_text, True, SELECT_SCREEN_TEXT)
        option_x = SCREEN_WIDTH // 2 - option_surface.get_width() // 2
        option_y = SELECT_OPTIONS_Y + index * SELECT_OPTION_GAP
        hitbox = pygame.Rect(option_x - 20, option_y - 6,
                             option_surface.get_width() + 40, option_surface.get_height() + 12)
        option_hitboxes.append((class_name, hitbox))

    quit_label = fonts["hint"].render("Quit", True, (255, 220, 220))
    quit_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - quit_label.get_width() // 2 - 20,
        SCREEN_HEIGHT - SELECT_HINT_OFFSET - 42,
        quit_label.get_width() + 40,
        quit_label.get_height() + 12,
    )

    while chosen_class is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in key_to_class:
                    chosen_class = key_to_class[event.key]
                elif event.key == pygame.K_ESCAPE:
                    return None
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pointer_pos = get_pointer_pos(event)
                if pointer_pos is None:
                    continue
                for class_name, rect in option_hitboxes:
                    if rect.collidepoint(pointer_pos):
                        chosen_class = class_name
                        break
                if quit_rect.collidepoint(pointer_pos):
                    return None

        screen.fill(SELECT_SCREEN_BG)

        title_surface = fonts["big"].render(GAME_TITLE, True, HERO_GOLD)
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, SELECT_TITLE_Y))

        sub_surface = fonts["small"].render("Choose Your Hero!", True, SELECT_SCREEN_TEXT)
        sub_x = SCREEN_WIDTH // 2 - sub_surface.get_width() // 2
        screen.blit(sub_surface, (sub_x, SELECT_SUBTITLE_Y))

        for index, class_name in enumerate(CHARACTER_CLASSES):
            option_text = f"  {index + 1}  —  {class_name}"
            option_surface = fonts["small"].render(option_text, True, SELECT_SCREEN_TEXT)
            option_x = SCREEN_WIDTH // 2 - option_surface.get_width() // 2
            option_y = SELECT_OPTIONS_Y + index * SELECT_OPTION_GAP
            screen.blit(option_surface, (option_x, option_y))

        hint_surface = fonts["hint"].render(
            "Press 1 - 6 or tap a hero   |   ESC = Quit", True, HERO_GOLD)
        hint_x = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
        screen.blit(hint_surface, (hint_x, SCREEN_HEIGHT - SELECT_HINT_OFFSET))
        pygame.draw.rect(screen, (90, 40, 40), quit_rect, border_radius=8)
        screen.blit(quit_label, (quit_rect.centerx - quit_label.get_width() // 2,
                                 quit_rect.centery - quit_label.get_height() // 2))

        pygame.display.flip()
        clock.tick(TARGET_FPS)
        await asyncio.sleep(0)

    return chosen_class


# ── Main Game Loop ─────────────────────────────────────────

async def main():
    """Set up pygame and run the game from start to finish."""

    # IMPORTANT: pre_init must come BEFORE pygame.init()!
    # On Windows, calling mixer.init() AFTER pygame.init() can silently fail,
    # meaning you'd get no sound and no error message. pre_init reserves the
    # audio settings first so pygame.init() sets up the mixer correctly.
    # 44100 Hz = CD-quality sample rate, -16 = 16-bit signed audio,
    # 2 = stereo (two channels: left + right), 512 = small buffer for low lag.
    pygame.mixer.pre_init(44100, -16, 2, 512)

    pygame.init()

    # ── Set up audio — SoundManager configures channels after pre_init ─────
    sounds = SoundManager()

    # ── Create all fonts HERE, once, right after pygame.init() ────────────
    hud_font  = pygame.font.SysFont("Arial", 11)
    hint_font = pygame.font.SysFont("Arial", 13)

    select_fonts = {
        "big":        pygame.font.SysFont("Arial", 48, bold=True),
        "small":      pygame.font.SysFont("Arial", 24),
        "small_bold": pygame.font.SysFont("Arial", 24, bold=True),
        "hint":       pygame.font.SysFont("Arial", 18),
    }

    pause_fonts = {
        "title":   pygame.font.SysFont("Arial", 42, bold=True),
        "section": pygame.font.SysFont("Arial", 22, bold=True),
        "body":    pygame.font.SysFont("Arial", 18),
    }

    # Fonts for the level-up overlay
    level_up_fonts = {
        "title": pygame.font.SysFont("Arial", 28, bold=True),
        "body":  pygame.font.SysFont("Arial", 20),
    }

    # Font for the big red "You died!" message
    death_font = pygame.font.SysFont("Arial", 36, bold=True)

    # Fonts for the Voltrak boss fight
    voltrak_bar_font  = pygame.font.SysFont("Arial", 13, bold=True)   # Label under the boss bar
    victory_title_font = pygame.font.SysFont("Arial", 42, bold=True)  # "VOLTRAK IS DEFEATED!"
    victory_body_font  = pygame.font.SysFont("Arial", 20)             # Sub-text and hint

    npc_font = pygame.font.SysFont("Arial", 14)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    # ── Load attack and projectile sprite sheets ───────────
    # Must happen AFTER set_mode() so convert_alpha() works.
    Projectile.load_sprites()
    AttackEffect.load_sprites()

    # ── Pre-build overlay surfaces ─────────────────────────
    # We build these once so we don't create new surfaces 60 times per second!
    pause_surfaces = {
        "dim":   pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
        "panel": pygame.Surface((PAUSE_PANEL_WIDTH, PAUSE_PANEL_HEIGHT), pygame.SRCALPHA),
    }
    pause_surfaces["dim"].fill(PAUSE_OVERLAY_COLOR)
    pause_surfaces["panel"].fill(PAUSE_PANEL_COLOR)

    level_up_surfaces = {
        "dim":   pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
        "panel": pygame.Surface((LEVELUP_PANEL_W, LEVELUP_PANEL_H), pygame.SRCALPHA),
    }
    level_up_surfaces["dim"].fill((0, 0, 0, 180))
    level_up_surfaces["panel"].fill((20, 10, 40, 230))

    # ── Outer loop: keeps going back to the menu instead of quitting ───────
    app_running = True

    while app_running:

        # ── Start menu music ───────────────────────────────
        sounds.play_menu_music()

        # ── Character Selection ────────────────────────────
        chosen_class = await run_character_selection(screen, clock, select_fonts)
        if chosen_class is None:
            app_running = False
            break

        # ── Story Intro ────────────────────────────────────
        intro_ok = await run_story_intro(screen, clock, select_fonts)
        if not intro_ok:
            app_running = False
            break

        # ── Create the Player ──────────────────────────────
        player = Player(chosen_class, SCREEN_WIDTH, SCREEN_HEIGHT)

        # ── Create the World ───────────────────────────────
        world = World()
        enemy_list = create_enemy_group()
        companions, villagers, summoner = create_npc_group()

        item_list = create_items_group(SHARD_POSITIONS)
        for pos in HEALTH_POTION_POSITIONS:
            item_list.append(HealthPotion(pos[0], pos[1]))

        # ── Flying projectiles and melee flash effects ─────
        # projectile_list holds any shurikens or laser blasts currently in the air.
        # attack_effects holds brief coloured flashes showing where melee weapons hit.
        projectile_list = []   # Flying shurikens and laser blasts
        attack_effects  = []   # Brief visual flashes showing melee attack areas
        enemy_proj_list = []   # Projectiles fired by Zara (and future enemies)

        # ── Switch to exploration music ────────────────────
        sounds.play_exploration_music()

        # ── Pause state ────────────────────────────────────
        game_paused            = False
        audio_enabled          = True
        selected_setting_index = 0

        # ── For hurt-sound detection ───────────────────────
        # We compare health before/after enemy updates each frame.
        prev_health = None

        # ── Level-up overlay state ─────────────────────────
        level_up_active = False   # True while showing the level-up choice screen

        # ── Boss and portal tracking ───────────────────────
        # These flags track our progress through the boss fights!
        grimrak_spawned     = False   # Have we created Grimrak yet?
        zara_spawned        = False   # Have we created Zara yet?
        miniboss_list       = []      # Holds Grimrak and Zara once they're active
        miniboss1_defeated  = False   # True once Grimrak is permanently beaten
        miniboss2_defeated  = False   # True once Zara is permanently beaten
        portal_key_spawned    = False   # True once we've dropped the key in the world
        portal_open           = False   # True once the player uses the key at the gate
        portal_overlay_active = False   # True while the "portal opened!" splash is visible
        portal_overlay_timer  = 0       # Countdown — auto-dismisses the splash after 3 seconds

        # Voltrak arena and companions
        arena_mode         = False   # True once we enter the final arena map
        voltrak_list       = []      # List containing Voltrak when in arena mode
        fighter_companions = []      # CompanionFighters summoned by the player
        voltrak_defeated   = False   # True once Voltrak is beaten — shows victory screen!
        lives_remaining    = MAX_LIVES
        game_over_lives    = False   # True after the 3rd death; run is over.

        # Reusable slam warning surface to avoid creating a new one every draw frame.
        slam_warning_surf = pygame.Surface((130, 130), pygame.SRCALPHA)
        touch_controls = TouchControls(hud_font)

        def handle_interact_action():
            """Handle the same behavior as pressing E."""
            nonlocal portal_open, arena_mode, world

            # First, try interacting with the Summoner if the player is close.
            summoner_rect = pygame.Rect(
                summoner.x, summoner.y, summoner.sprite_width, summoner.sprite_height
            )
            player_rect = pygame.Rect(
                player.x, player.y, player.sprite_width, player.sprite_height
            )
            if summoner_rect.inflate(80, 80).colliderect(player_rect):
                summon_result = summoner.on_interact()
                if summon_result == "summon":
                    fighter_companions.append(CompanionFighter(player.x + 20, player.y + 20))

            # The portal gate is 96 px wide and 128 px tall.
            portal_rect = pygame.Rect(PORTAL_X, PORTAL_Y, 96, 128)
            near_portal = portal_rect.inflate(40, 40).colliderect(player_rect)
            if player.has_portal_key and near_portal and not portal_open:
                portal_open = True
                arena_mode = True
                world = VoltrakArena()
                player.x, player.y = 600, 330
                fighter_companions.clear()

                if summoner.pre_activated_voltrak:
                    fighter_companions.append(CompanionFighter(480, 300))
                    fighter_companions.append(CompanionFighter(720, 300))
                else:
                    fighter_companions.append(CompanionFighter(560, 300))

                if not voltrak_list:
                    voltrak_list.append(Voltrak(550, 280))

                enemy_list.clear()
                miniboss_list.clear()
                item_list.clear()
                enemy_proj_list.clear()

        def handle_attack_action():
            """Handle the same behavior as pressing Space to attack."""
            attacked = player.try_attack()
            if not attacked:
                return

            sounds.play("attack_swing")

            if player.is_ranged_weapon():
                facing_vectors = {
                    "right": (1, 0), "left": (-1, 0),
                    "down":  (0, 1), "up":   (0, -1),
                }
                fdx, fdy = facing_vectors.get(player.facing, (1, 0))
                speed = Projectile.SHURIKEN_SPEED
                px = player.x + player.sprite_width  // 2 - Projectile.SHURIKEN_SIZE // 2
                py = player.y + player.sprite_height // 2 - Projectile.SHURIKEN_SIZE // 2
                proj = Projectile(px, py, fdx * speed, fdy * speed,
                                  "shuriken", player.get_attack_damage())
                projectile_list.append(proj)
            else:
                zones = player.get_attack_zones()
                if zones:
                    attack_effects.append(AttackEffect(zones, player.weapon_type))

        def get_interact_context():
            """Return whether interact should be enabled and its touch label."""
            player_rect = pygame.Rect(player.x, player.y, player.sprite_width, player.sprite_height)

            # Summoner has priority when nearby.
            summoner_rect = pygame.Rect(
                summoner.x, summoner.y, summoner.sprite_width, summoner.sprite_height
            )
            near_summoner = summoner_rect.inflate(80, 80).colliderect(player_rect)
            if near_summoner:
                if summoner.phase == 2 and not summoner.pre_activated_voltrak:
                    return True, "ACT"
                if summoner.can_summon():
                    return True, "SUM"

            portal_rect = pygame.Rect(PORTAL_X, PORTAL_Y, 96, 128)
            near_portal = portal_rect.inflate(40, 40).colliderect(player_rect)
            if player.has_portal_key and near_portal and not portal_open:
                return True, "ENTER"

            return False, "USE"

        # ── Game Loop ──────────────────────────────────────
        game_running = True
        while game_running:
            sw, sh = screen.get_size()
            touch_controls.update_layout(sw, sh)
            touch_controls.begin_frame()

            interact_enabled, interact_label = get_interact_context()
            touch_controls.set_interact(interact_enabled, interact_label)

            # ── Handle Events ──────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    app_running  = False

                # Feed touch/mouse events into the virtual controls.
                touch_controls.handle_event(event)

                if event.type == pygame.KEYDOWN:

                    # ── Level-up overlay intercepts ALL input while active ──
                    # When the level-up screen is showing, only 1–4 work!
                    if level_up_active:
                        if event.key in LEVELUP_OPTION_KEYS:
                            stat_chosen = LEVELUP_OPTION_KEYS[event.key]
                            player.apply_level_up(stat_chosen)
                            level_up_active = False
                        # Swallow all other keys — nothing else happens while choosing

                    # ── ESC: check overlays in priority order ──────────────
                    elif event.key == pygame.K_ESCAPE:
                        if voltrak_defeated:
                            game_running = False   # You won! ESC goes back to the title screen
                        elif game_over_lives:
                            game_running = False   # Out of lives — back to menu.
                        elif portal_overlay_active:
                            portal_overlay_active = False   # Dismiss the intro splash → fight begins!
                        elif game_paused:
                            game_paused = False
                        else:
                            game_running = False

                    elif event.key == pygame.K_SPACE and voltrak_defeated:
                        # Let Space return to menu too, matching the victory-screen hint text.
                        game_running = False
                    elif event.key == pygame.K_SPACE and game_over_lives:
                        game_running = False

                    # ── P: toggle the pause menu ────────────
                    elif event.key == pygame.K_p:
                        game_paused = not game_paused

                    # ── Keys that only work while PAUSED ────
                    elif game_paused:
                        if event.key == pygame.K_UP:
                            selected_setting_index = max(0, selected_setting_index - 1)
                        elif event.key == pygame.K_DOWN:
                            selected_setting_index = min(NUM_SETTINGS - 1, selected_setting_index + 1)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if selected_setting_index == 0:
                                audio_enabled = not audio_enabled
                                sounds.set_enabled(audio_enabled)

                    # ── E: enter the portal — only when close to it AND holding the key ──
                    elif event.key == pygame.K_e:
                        handle_interact_action()

                    # ── Space: attack — only when playing normally ──
                    elif event.key == pygame.K_SPACE:
                        handle_attack_action()

                # Tap support for overlays and pause actions.
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    pointer_pos = get_pointer_pos(event)
                    if pointer_pos is None:
                        continue

                    if level_up_active:
                        for stat_id, rect in get_level_up_touch_targets(player, level_up_fonts):
                            if rect.collidepoint(pointer_pos):
                                player.apply_level_up(stat_id)
                                level_up_active = False
                                break
                    elif game_paused:
                        targets = get_pause_touch_targets()
                        if targets["resume"].collidepoint(pointer_pos):
                            game_paused = False
                        elif targets["audio"].collidepoint(pointer_pos):
                            audio_enabled = not audio_enabled
                            sounds.set_enabled(audio_enabled)
                        elif targets["menu"].collidepoint(pointer_pos):
                            game_running = False
                    elif voltrak_defeated or game_over_lives:
                        if get_end_screen_return_rect().collidepoint(pointer_pos):
                            game_running = False
                    elif portal_overlay_active:
                        portal_overlay_active = False

            # ── Update ─────────────────────────────────────
            # Only update when not paused AND not showing the level-up screen

            # Dispatch virtual touch buttons (edge-triggered actions).
            if touch_controls.pause_tapped:
                if game_paused:
                    game_paused = False
                elif not level_up_active and not voltrak_defeated and not game_over_lives:
                    game_paused = True
            if touch_controls.interact_tapped:
                if not game_paused and not level_up_active and not portal_overlay_active:
                    handle_interact_action()
            if touch_controls.attack_tapped:
                if not game_paused and not level_up_active and not portal_overlay_active \
                        and not voltrak_defeated and not game_over_lives:
                    handle_attack_action()

            if not game_paused and not level_up_active and not voltrak_defeated and not game_over_lives:

                # ── Handle player death state first ────────
                # While the player is dead, we count down the timer and skip
                # all other updates. The "You died!" screen shows during this time.
                if player.is_dead_flag:
                    ready_to_respawn = player.update_death_timer()
                    if ready_to_respawn:
                        if lives_remaining > 0:
                            # Respawn at the first respawn point (could be smarter later!)
                            rx, ry = RESPAWN_POINTS[0]
                            player.respawn(rx, ry)
                            sounds.play("respawn")
                            sounds.play_exploration_music()
                        else:
                            # No lives left — lock into game-over state.
                            game_over_lives = True

                else:
                    # ── Check melee attack hits FIRST, before handle_input resets the flag ──
                    # WHY first? handle_attack() sets player.attacking = True in the event
                    # loop above. But handle_input() resets it to False at its very start.
                    # If we called handle_input() before this check, attacking would always be
                    # False here and enemies would NEVER take damage!
                    #
                    # Melee only — ranged weapons use the projectile_list below!
                    if player.attacking and not player.is_ranged_weapon():
                        attack_zones = player.get_attack_zones()

                        for zone in attack_zones:
                            # Check all normal enemies
                            for enemy in enemy_list:
                                if not enemy.is_dead():
                                    enemy_rect = pygame.Rect(enemy.x, enemy.y,
                                                             enemy.sprite_width, enemy.sprite_height)
                                    if zone.colliderect(enemy_rect) and not enemy._already_hit_this_swing:
                                        # Assassin uses special one-shot damage;
                                        # all other classes use the normal formula
                                        if player.weapon_type == "daggers":
                                            dmg = player.get_assassin_damage(enemy.max_health, False)
                                        else:
                                            dmg = player.get_attack_damage()
                                        enemy.take_damage(dmg)
                                        enemy._already_hit_this_swing = True
                                        sounds.play("attack_hit")
                                        # Check for drops RIGHT NOW before update() resets these flags!
                                        if enemy.just_died:
                                            item_list.append(MagicalShard(enemy.x, enemy.y))
                                        if enemy.potion_drop:
                                            item_list.append(HealthPotion(enemy.x, enemy.y))

                            # Check all mini-bosses (Grimrak, Zara) — same zone check
                            for boss in miniboss_list:
                                if not boss.is_permanently_dead():
                                    boss_rect = pygame.Rect(boss.x, boss.y,
                                                            boss.sprite_width, boss.sprite_height)
                                    if zone.colliderect(boss_rect):
                                        # Assassin daggers still do special damage on bosses!
                                        if player.weapon_type == "daggers":
                                            dmg = player.get_assassin_damage(boss.max_health, True)
                                        else:
                                            dmg = player.get_attack_damage()
                                        boss.take_damage(dmg)
                                        sounds.play("attack_hit")
                                        # Mini-bosses always drop a shard AND a big golden potion!
                                        # Check RIGHT NOW before boss.update() resets these flags.
                                        if boss.just_died:
                                            item_list.append(MagicalShard(boss.x, boss.y))
                                        if boss.boss_potion_drop:
                                            item_list.append(BigHealthPotion(boss.x, boss.y))

                            # Check Voltrak — the final boss takes melee damage too!
                            for voltrak in voltrak_list:
                                if voltrak.is_permanently_dead():
                                    continue
                                voltrak_rect = pygame.Rect(voltrak.x, voltrak.y,
                                                           voltrak.sprite_width, voltrak.sprite_height)
                                if zone.colliderect(voltrak_rect):
                                    if player.weapon_type == "daggers":
                                        dmg = player.get_assassin_damage(voltrak.max_health, True)
                                    else:
                                        dmg = player.get_attack_damage()
                                    voltrak.take_damage(dmg)
                                    sounds.play("attack_hit")
                                    # Did that hit defeat Voltrak? Check now — before update() resets the flag!
                                    if voltrak.just_died:
                                        voltrak_defeated = True

                    # Move the player
                    keys_pressed = pygame.key.get_pressed()
                    player.handle_input(keys_pressed, touch_controls.get_player_input())
                    player.keep_on_screen(SCREEN_WIDTH, SCREEN_HEIGHT)

                    # ── Footstep sounds ─────────────────────────────────────
                    # Play a step sound while the player is moving. We check
                    # which animation is playing to know if they're walking or running.
                    if player.current_animation in ("walk", "run"):
                        sounds.play_footstep(running=player.current_animation == "run")
                    else:
                        sounds.reset_footstep()

                    # Did the player just run out of health from enemy contact?
                    if not player.is_alive():
                        player.trigger_death()
                        lives_remaining = max(0, lives_remaining - 1)
                        if lives_remaining <= 0:
                            game_over_lives = True
                        sounds.play("player_die")   # Short death stinger — plays right away
                        sounds.play_game_over()     # Stop music and play game-over track

                    # Snapshot health before enemy updates so we can detect hurt
                    prev_health = player.health

                    # Update the world (animates portal gate and water tiles)
                    world.update()

                    # Update normal enemies — they wander, chase, and attack.
                    for enemy in enemy_list:
                        enemy.update(player)
                        # If the enemy just landed a hit, show a red flash at the player!
                        # This makes enemy attacks VISIBLE — you can see and feel the hit.
                        if enemy.just_attacked:
                            player_hit_rect = pygame.Rect(
                                player.x, player.y,
                                player.sprite_width, player.sprite_height,
                            )
                            attack_effects.append(AttackEffect([player_hit_rect], "enemy_melee"))

                    # Update mini-bosses and check if they've been permanently defeated
                    for boss in miniboss_list:
                        boss.update(player)
                        # Same red flash when a mini-boss hits — they hit harder, same visual cue
                        if boss.just_attacked:
                            player_hit_rect = pygame.Rect(
                                player.x, player.y,
                                player.sprite_width, player.sprite_height,
                            )
                            attack_effects.append(AttackEffect([player_hit_rect], "enemy_melee"))

                    # Grimrak ground slam — deals 3 HP if the player is in the orange zone
                    for boss in miniboss_list:
                        if hasattr(boss, "slam_active") and boss.slam_active > 0:
                            slam_rect = pygame.Rect(boss.x - 25, boss.y - 25, 130, 130)
                            player_rect = pygame.Rect(
                                player.x, player.y, player.sprite_width, player.sprite_height
                            )
                            if slam_rect.colliderect(player_rect):
                                player.take_damage(3)
                                sounds.play_hurt()

                    # Collect any new projectiles Zara (or future bosses) just fired
                    for boss in miniboss_list:
                        if hasattr(boss, "pending_projectiles"):
                            enemy_proj_list.extend(boss.pending_projectiles)

                    # ── Auto-dismiss the portal intro splash after 3 seconds ───
                    if portal_overlay_active:
                        portal_overlay_timer -= 1
                        if portal_overlay_timer <= 0:
                            portal_overlay_active = False

                    # ── Update Voltrak — the final boss! ────────────────────
                    # We skip his update while the intro splash is showing so the
                    # player gets a few seconds to read it before the fight starts.
                    for voltrak in voltrak_list:
                        if voltrak.is_permanently_dead() or portal_overlay_active:
                            continue
                        voltrak.update(player)

                        # Did any shock bolts just fire? Check if the player is standing in one!
                        # Shock damage is checked the frame the bolts appear — then zones stay
                        # visible but no longer deal damage (so the player can dodge next volley).
                        if voltrak.shock_just_fired:
                            player_rect = pygame.Rect(player.x, player.y,
                                                      player.sprite_width, player.sprite_height)
                            for zone_entry in voltrak.shock_zones:
                                zone_rect = zone_entry[0]
                                if zone_rect.colliderect(player_rect):
                                    player.take_damage(voltrak.SHOCK_DAMAGE)
                                    sounds.play_hurt()
                                    break   # One shock hit per volley — don't stack all 4 bolts

                        # Did Voltrak just die during this update? (e.g. from damage-over-time)
                        if voltrak.just_died:
                            voltrak_defeated = True

                    # Victory condition: if the arena boss is dead, show the victory screen.
                    if voltrak_list and voltrak_list[0].is_permanently_dead():
                        voltrak_defeated = True

                    # Move enemy projectiles and check if they hit the player
                    player_rect = pygame.Rect(
                        player.x, player.y, player.sprite_width, player.sprite_height
                    )
                    for proj in enemy_proj_list[:]:
                        proj.update()
                        if not proj.alive:
                            enemy_proj_list.remove(proj)
                            continue
                        if proj.get_rect().colliderect(player_rect):
                            player.take_damage(proj.damage)
                            sounds.play_hurt()
                            proj.alive = False
                            enemy_proj_list.remove(proj)

                    # ── Hurt detection ──────────────────────────────────────
                    # If health dropped during enemy updates, play the hurt sound
                    if player.health < prev_health:
                        sounds.play_hurt()

                    # Has Grimrak been beaten for the first time?
                    if (not miniboss1_defeated
                            and len(miniboss_list) >= 1
                            and isinstance(miniboss_list[0], Grimrak)
                            and miniboss_list[0].is_permanently_dead()):
                        miniboss1_defeated = True
                        # If Zara hasn't spawned yet, go back to exploration music
                        if not zara_spawned:
                            sounds.play_exploration_music()

                    # Has Zara been beaten for the first time?
                    if (not miniboss2_defeated
                            and len(miniboss_list) >= 2
                            and isinstance(miniboss_list[1], Zara)
                            and miniboss_list[1].is_permanently_dead()):
                        miniboss2_defeated = True
                        sounds.play_exploration_music()
                        summoner.notify_bosses_beaten()

                    # Drop the portal key ONCE when BOTH mini-bosses are defeated!
                    if (miniboss1_defeated and miniboss2_defeated and not portal_key_spawned):
                        portal_key_spawned = True
                        kx, ky = PORTAL_KEY_DROP_POS
                        item_list.append(PortalKey(kx, ky))

                    # Spawn Grimrak at 25 shards collected (only once!)
                    if player.shards_collected >= GRIMRAK_SPAWN_SHARDS and not grimrak_spawned:
                        grimrak_spawned = True
                        gx, gy = GRIMRAK_SPAWN_POS
                        miniboss_list.append(Grimrak(gx, gy))
                        sounds.play_grimrak_music()

                    # Spawn Zara at 50 shards collected (only once!)
                    if player.shards_collected >= ZARA_SPAWN_SHARDS and not zara_spawned:
                        zara_spawned = True
                        zx, zy = ZARA_SPAWN_POS
                        miniboss_list.append(Zara(zx, zy))
                        sounds.play_zara_music()

                    # Update companions (they follow the player)
                    for companion in companions:
                        companion.update(player)

                    # Update fighter companions (they actively attack nearby enemies/bosses)
                    fighter_targets = miniboss_list + voltrak_list
                    for fighter in fighter_companions:
                        fighter.update(player, enemy_list, fighter_targets)

                    # Update villagers (they show speech bubbles when nearby)
                    for villager in villagers:
                        villager.update(player)

                    # Update summoner hint bubble timing
                    summoner.update(player)

                    # Check if the player walked over any items and collected them.
                    # item_list[:] is a copy — safe to remove items while looping!
                    for item in item_list[:]:
                        item.update()
                        if item.check_collection(player):
                            # Play the right collection sound based on what was picked up
                            if isinstance(item, MagicalShard):
                                sounds.play("collect_shard")
                            elif isinstance(item, HealthPotion):
                                sounds.play("collect_health")
                            elif isinstance(item, BigHealthPotion):
                                sounds.play("collect_health")   # Big golden heal — same jingle!
                            elif isinstance(item, PortalKey):
                                sounds.play("collect_portal_key")
                                # player.has_portal_key is set inside PortalKey._on_collected
                            item_list.remove(item)

                    # Did the player earn a level-up from their last shard pickup?
                    if player.level_up_pending:
                        level_up_active = True
                        sounds.play_level_up_fanfare()

                    # ── Update all flying projectiles ───────────────────────
                    # Shurikens and lasers move each frame and disappear when they
                    # hit an enemy or travel too far (600 px).
                    for proj in projectile_list[:]:   # copy the list since we may remove items
                        proj.update()
                        if not proj.alive:
                            projectile_list.remove(proj)
                            continue
                        proj_rect = proj.get_rect()

                        hit_something = False

                        # Check if the projectile hit any regular enemy
                        for enemy in enemy_list:
                            if not enemy.is_dead():
                                enemy_rect = pygame.Rect(enemy.x, enemy.y,
                                                         enemy.sprite_width, enemy.sprite_height)
                                if proj_rect.colliderect(enemy_rect):
                                    enemy.take_damage(proj.damage)
                                    sounds.play("attack_hit")
                                    if enemy.just_died:
                                        item_list.append(MagicalShard(enemy.x, enemy.y))
                                    if enemy.potion_drop:
                                        item_list.append(HealthPotion(enemy.x, enemy.y))
                                    proj.alive = False
                                    hit_something = True
                                    break   # One projectile = one enemy hit

                        # If it didn't hit a regular enemy, check mini-bosses
                        if not hit_something:
                            for boss in miniboss_list:
                                if not boss.is_permanently_dead():
                                    boss_rect = pygame.Rect(boss.x, boss.y,
                                                            boss.sprite_width, boss.sprite_height)
                                    if proj_rect.colliderect(boss_rect):
                                        boss.take_damage(proj.damage)
                                        sounds.play("attack_hit")
                                        if boss.just_died:
                                            item_list.append(MagicalShard(boss.x, boss.y))
                                        if boss.boss_potion_drop:
                                            item_list.append(BigHealthPotion(boss.x, boss.y))
                                        proj.alive = False
                                        hit_something = True
                                        break

                        # If it didn't hit a mini-boss either, check Voltrak!
                        if not hit_something:
                            for voltrak in voltrak_list:
                                if voltrak.is_permanently_dead():
                                    continue
                                voltrak_rect = pygame.Rect(voltrak.x, voltrak.y,
                                                           voltrak.sprite_width, voltrak.sprite_height)
                                if proj_rect.colliderect(voltrak_rect):
                                    voltrak.take_damage(proj.damage)
                                    sounds.play("attack_hit")
                                    # Check for victory right after the hit!
                                    if voltrak.just_died:
                                        voltrak_defeated = True
                                    proj.alive = False
                                    hit_something = True
                                    break

                        # Remove the projectile if it hit something
                        if not proj.alive and proj in projectile_list:
                            projectile_list.remove(proj)

                    # ── Update melee attack effect timers ───────────────────
                    # Each effect counts down and removes itself when done.
                    for fx in attack_effects[:]:
                        fx.update()
                        if not fx.alive:
                            attack_effects.remove(fx)

            # ── Draw ───────────────────────────────────────
            # Layers: world → items → villagers → enemies → mini-bosses
            #         → companions → player → projectiles → effects → HUD → overlays

            # 1. Draw the tile world (grass, paths, trees, portal gate)
            world.draw(screen)

            # 2. Draw collectible items
            for item in item_list:
                item.draw(screen)

            # 3. Draw villager NPCs
            for villager in villagers:
                villager.draw(screen, npc_font)

            # 3b. Draw the Summoner NPC
            summoner.draw(screen, npc_font)

            # 4. Draw regular enemies (with health bars)
            for enemy in enemy_list:
                enemy.draw(screen)

            # 5. Draw mini-bosses (also have health bars via the Enemy parent class)
            for boss in miniboss_list:
                boss.draw(screen)

            # 5a. Draw Grimrak's slam zone (orange danger area) while active.
            for boss in miniboss_list:
                if hasattr(boss, "slam_active") and boss.slam_active > 0:
                    alpha = int(160 * boss.slam_active / 20)
                    slam_warning_surf.fill((255, 140, 0, alpha))
                    screen.blit(slam_warning_surf, (boss.x - 25, boss.y - 25))

            # 5b. Draw Voltrak (the final boss) and his electric shock zones
            for voltrak in voltrak_list:
                if not voltrak.is_permanently_dead():
                    voltrak.draw(screen)       # Sprite + small health bar above
                    voltrak.draw_shocks(screen)   # Electric bolt zones glowing on the ground

            # 5c. Draw enemy projectiles (Zara bolts) between boss and companion layers.
            for proj in enemy_proj_list:
                proj.draw(screen)

            # 6. Draw companion NPCs on top of enemies
            for companion in companions:
                companion.draw(screen)
            for fighter in fighter_companions:
                fighter.draw(screen)

            # 7. Draw the player on top of everything in the world
            player.draw(screen)

            # 8. Draw ranged projectiles — shurikens and laser blasts!
            for proj in projectile_list:
                proj.draw(screen)

            # 9. Draw melee attack flash effects — brief coloured zones showing hit areas
            for fx in attack_effects:
                fx.draw(screen)

            # 10. Draw the HUD (health, endurance, strength, magic bars + portrait)
            draw_hud(screen, player, hud_font)

            # 11. Shard counter and level — top-right corner
            shard_text = hud_font.render(
                f"Shards: {player.shards_collected}   LVL {player.level}", True, (26, 188, 156))
            screen.blit(shard_text, (SCREEN_WIDTH - shard_text.get_width() - 12, 12))

            # 11b. Lives counter — top-right under shard text
            lives_text = hud_font.render(f"Lives: {lives_remaining}", True, (245, 200, 66))
            screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 12, 34))

            # 12. Show how many more shards until the next boss spawns (only in the overworld).
            if not arena_mode:
                if not grimrak_spawned:
                    shards_needed = GRIMRAK_SPAWN_SHARDS - player.shards_collected
                    boss_hint = hud_font.render(
                        f"Collect {shards_needed} more shards to awaken Grimrak!", True, (255, 200, 100))
                    screen.blit(boss_hint,
                        (SCREEN_WIDTH // 2 - boss_hint.get_width() // 2, SCREEN_HEIGHT - 30))
                elif not zara_spawned:
                    shards_needed = ZARA_SPAWN_SHARDS - player.shards_collected
                    boss_hint = hud_font.render(
                        f"Collect {shards_needed} more shards to awaken Zara!", True, (200, 150, 255))
                    screen.blit(boss_hint,
                        (SCREEN_WIDTH // 2 - boss_hint.get_width() // 2, SCREEN_HEIGHT - 30))

            # 13. Portal key indicator and proximity prompts
            if player.has_portal_key and not portal_open:
                # Check if the player is close enough to the portal gate
                portal_rect   = pygame.Rect(PORTAL_X, PORTAL_Y, 96, 128)
                player_rect   = pygame.Rect(player.x, player.y,
                                            player.sprite_width, player.sprite_height)
                near_portal   = portal_rect.inflate(40, 40).colliderect(player_rect)

                if near_portal:
                    # Player is RIGHT NEXT to the gate — show "Press E" prompt
                    key_hint = hud_font.render(
                        "[ Press E to enter the portal! ]", True, HERO_GOLD)
                else:
                    # Player has the key but isn't near the gate yet
                    key_hint = hud_font.render(
                        "[ Portal Key collected — walk to the gate to open it! ]", True, HERO_GOLD)
                screen.blit(key_hint,
                    (SCREEN_WIDTH // 2 - key_hint.get_width() // 2, SCREEN_HEIGHT - 50))

            # 13b. Voltrak boss bar — shown at the top-centre while the fight is active
            if voltrak_list and not voltrak_list[0].is_permanently_dead() and not portal_overlay_active:
                draw_voltrak_boss_bar(screen, voltrak_list[0], voltrak_bar_font)

            # 13c. Portal intro splash — shown once when the portal opens.
            # Auto-dismisses after 3 seconds, or press ESC to skip right into the fight!
            if portal_overlay_active:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((80, 0, 120, 200))   # Deep purple, semi-transparent
                screen.blit(overlay, (0, 0))
                boss_title = hint_font.render(
                    "THE PORTAL IS OPEN!", True, HERO_GOLD)
                boss_sub   = hint_font.render(
                    "Voltrak the Shockblade Eel has emerged!", True, (220, 180, 255))
                boss_fight = hint_font.render(
                    "FIGHT FOR LUMORIA!", True, (255, 200, 100))
                dismiss_hint = hint_font.render(
                    "Press ESC to begin the battle!", True, (200, 200, 200))
                screen.blit(boss_title,
                    (SCREEN_WIDTH // 2 - boss_title.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
                screen.blit(boss_sub,
                    (SCREEN_WIDTH // 2 - boss_sub.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
                screen.blit(boss_fight,
                    (SCREEN_WIDTH // 2 - boss_fight.get_width() // 2, SCREEN_HEIGHT // 2 + 16))
                screen.blit(dismiss_hint,
                    (SCREEN_WIDTH // 2 - dismiss_hint.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

            # 14. ESC hint in the bottom-right corner
            draw_esc_hint(screen, hint_font)

            # 14b. On-screen touch controls for mobile play (hidden on blocking overlays)
            if (not game_paused and not level_up_active and not voltrak_defeated
                    and not game_over_lives and not player.is_dead_flag
                    and not portal_overlay_active):
                touch_controls.draw(screen)

            # 15. Pause overlay (on top of the game)
            if game_paused:
                draw_pause_overlay(screen, pause_fonts, pause_surfaces,
                                   audio_enabled, selected_setting_index)

            # 16. Death screen — on top of even the pause overlay
            if player.is_dead_flag:
                draw_death_screen(screen, death_font, lives_remaining)

            # 17. Level-up overlay — the topmost layer of all (unless you've just won!)
            if level_up_active:
                draw_level_up_overlay(screen, player, level_up_fonts, level_up_surfaces)

            # 18. Victory screen — shown when Voltrak is defeated. Nothing else matters now!
            if voltrak_defeated:
                draw_victory_screen(screen, victory_title_font, victory_body_font)

            # 19. Game-over screen — shown after all lives are spent.
            if game_over_lives:
                draw_game_over_screen(screen, victory_title_font, victory_body_font)

            # ── Advance audio timers ────────────────────────
            sounds.tick()

            # ── Show the Frame ─────────────────────────────
            pygame.display.flip()
            clock.tick(TARGET_FPS)
            await asyncio.sleep(0)

    pygame.quit()


# ── Entry Point ────────────────────────────────────────────
asyncio.run(main())
