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

# Import the World class, and the lists of where shards and potions start
from game.world   import World, SHARD_POSITIONS, HEALTH_POTION_POSITIONS

# Import the function that creates all the enemies, plus the two mini-boss classes
from game.enemies import create_enemy_group, Grimrak, Zara

# Import the function that creates all the friendly NPCs (companions + villagers)
from game.npc     import create_npc_group

# Import items — factory function plus all item types we use directly
from game.items   import create_items_group, HealthPotion, MagicalShard, PortalKey

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
STRENGTH_BAR_WIDTH  =  80
STRENGTH_BAR_HEIGHT =  10

# Magic bar — sits just below the strength bar
MAGIC_BAR_X      =  12
MAGIC_BAR_Y      =  70
MAGIC_BAR_WIDTH  =  80
MAGIC_BAR_HEIGHT =  10

# Portrait — shifted down to make room for the new stat bars
PORTRAIT_X    =  12
PORTRAIT_Y    =  84   # Was 60, now 84 to clear the strength and magic bars
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

# ── Respawn Points ─────────────────────────────────────────
# When the player dies, they come back at the first respawn point.
# (We'll add logic to pick the nearest one later!)
RESPAWN_POINTS = [
    (640, 360),   # Center of the map — the starting spot
    (200, 300),   # Near the first villager
    (850, 450),   # Right side of the map
]


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


# ── Helper: Draw the Death Screen ─────────────────────────

def draw_death_screen(screen, death_font):
    """Show a 'You died! Respawning...' message centered on screen.

    We draw this ON TOP of the game world so the player can see
    where they fell before respawning.
    """
    msg = death_font.render("You died!  Respawning...", True, (231, 76, 60))
    msg_x = SCREEN_WIDTH  // 2 - msg.get_width()  // 2
    msg_y = SCREEN_HEIGHT // 2 - msg.get_height() // 2
    screen.blit(msg, (msg_x, msg_y))


# ── Helper: Draw the "ESC = Menu" hint ────────────────────

def draw_esc_hint(screen, hint_font):
    """Draw a small hint in the bottom-right corner reminding the player how to return to the menu."""
    hint_surface = hint_font.render("ESC = Menu", True, (200, 200, 200))
    hint_x = SCREEN_WIDTH  - hint_surface.get_width()  - 10
    hint_y = SCREEN_HEIGHT - hint_surface.get_height() - 10
    screen.blit(hint_surface, (hint_x, hint_y))


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
        "P                  =  Pause / Unpause",
        "ESC                =  Return to Menu",
    ]

    for line_index, control_text in enumerate(controls_list):
        line_surface = pause_fonts["body"].render(control_text, True, PAUSE_BODY_COLOR)
        line_y = panel_y + 110 + line_index * 26
        screen.blit(line_surface, (panel_x + 30, line_y))

    settings_heading = pause_fonts["section"].render("SETTINGS", True, PAUSE_TITLE_COLOR)
    screen.blit(settings_heading, (panel_x + 30, panel_y + 240))

    audio_state_text = "ON" if audio_enabled else "OFF"
    audio_color = PAUSE_SELECT_COLOR if selected_setting_index == 0 else PAUSE_BODY_COLOR

    if selected_setting_index == 0:
        arrow_surface = pause_fonts["body"].render(">", True, PAUSE_SELECT_COLOR)
        screen.blit(arrow_surface, (panel_x + 15, panel_y + 270))

    audio_surface = pause_fonts["body"].render(f"Audio:  {audio_state_text}", True, audio_color)
    screen.blit(audio_surface, (panel_x + 30, panel_y + 270))

    footer_text = "P or ESC = Unpause   |   Up/Down = Navigate   |   Enter/Space = Toggle"
    footer_surface = pause_fonts["body"].render(footer_text, True, (160, 160, 160))
    footer_x = SCREEN_WIDTH // 2 - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, panel_y + PAUSE_PANEL_HEIGHT - 35))


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

            hint = fonts["hint"].render("Press Space or Enter to continue", True, HERO_GOLD)
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

    key_to_class = {
        pygame.K_1: CHARACTER_CLASSES[0],
        pygame.K_2: CHARACTER_CLASSES[1],
        pygame.K_3: CHARACTER_CLASSES[2],
        pygame.K_4: CHARACTER_CLASSES[3],
        pygame.K_5: CHARACTER_CLASSES[4],
        pygame.K_6: CHARACTER_CLASSES[5],
    }

    while chosen_class is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in key_to_class:
                    chosen_class = key_to_class[event.key]
                elif event.key == pygame.K_ESCAPE:
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
            "Press 1 - 6 to choose your character   |   ESC = Quit", True, HERO_GOLD)
        hint_x = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
        screen.blit(hint_surface, (hint_x, SCREEN_HEIGHT - SELECT_HINT_OFFSET))

        pygame.display.flip()
        clock.tick(TARGET_FPS)
        await asyncio.sleep(0)

    return chosen_class


# ── Main Game Loop ─────────────────────────────────────────

async def main():
    """Set up pygame and run the game from start to finish."""

    pygame.init()

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

    npc_font = pygame.font.SysFont("Arial", 14)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

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
        companions, villagers = create_npc_group()

        item_list = create_items_group(SHARD_POSITIONS)
        for pos in HEALTH_POTION_POSITIONS:
            item_list.append(HealthPotion(pos[0], pos[1]))

        # ── Pause state ────────────────────────────────────
        game_paused            = False
        audio_enabled          = True
        selected_setting_index = 0

        # ── Level-up overlay state ─────────────────────────
        level_up_active = False   # True while showing the level-up choice screen

        # ── Boss and portal tracking ───────────────────────
        # These flags track our progress through the boss fights!
        grimrak_spawned     = False   # Have we created Grimrak yet?
        zara_spawned        = False   # Have we created Zara yet?
        miniboss_list       = []      # Holds Grimrak and Zara once they're active
        miniboss1_defeated  = False   # True once Grimrak is permanently beaten
        miniboss2_defeated  = False   # True once Zara is permanently beaten
        portal_key_spawned  = False   # True once we've dropped the key in the world
        portal_open         = False   # True once the player uses the key at the gate

        # ── Game Loop ──────────────────────────────────────
        game_running = True
        while game_running:

            # ── Handle Events ──────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    app_running  = False

                if event.type == pygame.KEYDOWN:

                    # ── Level-up overlay intercepts ALL input while active ──
                    # When the level-up screen is showing, only 1–4 work!
                    if level_up_active:
                        if event.key in LEVELUP_OPTION_KEYS:
                            stat_chosen = LEVELUP_OPTION_KEYS[event.key]
                            player.apply_level_up(stat_chosen)
                            level_up_active = False
                        # Swallow all other keys — nothing else happens while choosing

                    # ── ESC: return to character selection ──
                    elif event.key == pygame.K_ESCAPE:
                        if game_paused:
                            game_paused = False
                        else:
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

                    # ── Space: attack — only when playing normally ──
                    elif event.key == pygame.K_SPACE:
                        player.handle_attack(event)

            # ── Update ─────────────────────────────────────
            # Only update when not paused AND not showing the level-up screen

            if not game_paused and not level_up_active:

                # ── Handle player death state first ────────
                # While the player is dead, we count down the timer and skip
                # all other updates. The "You died!" screen shows during this time.
                if player.is_dead_flag:
                    ready_to_respawn = player.update_death_timer()
                    if ready_to_respawn:
                        # Respawn at the first respawn point (could be smarter later!)
                        rx, ry = RESPAWN_POINTS[0]
                        player.respawn(rx, ry)

                else:
                    # ── Check attack hits FIRST, before handle_input resets the flag ──
                    # WHY first? handle_attack() sets player.attacking = True in the event
                    # loop above. But handle_input() resets it to False at its very start.
                    # If we called handle_input() before this check, attacking would always be
                    # False here and enemies would NEVER take damage!
                    if player.attacking:
                        attack_rect = player.get_attack_rect()
                        attack_dmg  = player.get_attack_damage()   # Weapon + stat-based damage

                        # Check all normal enemies
                        for enemy in enemy_list:
                            if not enemy.is_dead():
                                enemy_rect = pygame.Rect(enemy.x, enemy.y,
                                                         enemy.sprite_width, enemy.sprite_height)
                                if attack_rect.colliderect(enemy_rect):
                                    enemy.take_damage(attack_dmg)

                        # Check all mini-bosses (Grimrak, Zara) — same damage formula
                        for boss in miniboss_list:
                            if not boss.is_permanently_dead():
                                boss_rect = pygame.Rect(boss.x, boss.y,
                                                        boss.sprite_width, boss.sprite_height)
                                if attack_rect.colliderect(boss_rect):
                                    boss.take_damage(attack_dmg)

                    # Move the player
                    keys_pressed = pygame.key.get_pressed()
                    player.handle_input(keys_pressed)
                    player.keep_on_screen(SCREEN_WIDTH, SCREEN_HEIGHT)

                    # Did the player just run out of health from enemy contact?
                    if not player.is_alive():
                        player.trigger_death()

                    # Update the world (animates portal gate and water tiles)
                    world.update()

                    # Update normal enemies — they wander, chase, and attack.
                    # Also check if any just died and should drop a shard.
                    for enemy in enemy_list:
                        enemy.update(player)
                        # just_died is True (60% chance) on the single frame an enemy dies
                        if enemy.just_died:
                            item_list.append(MagicalShard(enemy.x, enemy.y))

                    # Update mini-bosses and check if they've been permanently defeated
                    for boss in miniboss_list:
                        boss.update(player)

                    # Has Grimrak been beaten for the first time?
                    if (not miniboss1_defeated
                            and len(miniboss_list) >= 1
                            and isinstance(miniboss_list[0], Grimrak)
                            and miniboss_list[0].is_permanently_dead()):
                        miniboss1_defeated = True

                    # Has Zara been beaten for the first time?
                    if (not miniboss2_defeated
                            and len(miniboss_list) >= 2
                            and isinstance(miniboss_list[1], Zara)
                            and miniboss_list[1].is_permanently_dead()):
                        miniboss2_defeated = True

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

                    # Spawn Zara at 50 shards collected (only once!)
                    if player.shards_collected >= ZARA_SPAWN_SHARDS and not zara_spawned:
                        zara_spawned = True
                        zx, zy = ZARA_SPAWN_POS
                        miniboss_list.append(Zara(zx, zy))

                    # Update companions (they follow the player)
                    for companion in companions:
                        companion.update(player)

                    # Update villagers (they show speech bubbles when nearby)
                    for villager in villagers:
                        villager.update(player)

                    # Check if the player walked over any items and collected them.
                    # item_list[:] is a copy — safe to remove items while looping!
                    for item in item_list[:]:
                        item.update()
                        if item.check_collection(player):
                            # If the player picked up the portal key, mark it
                            if isinstance(item, PortalKey):
                                pass   # player.has_portal_key is set inside PortalKey._on_collected
                            item_list.remove(item)

                    # Did the player earn a level-up from their last shard pickup?
                    if player.level_up_pending:
                        level_up_active = True

            # ── Draw ───────────────────────────────────────
            # Layers: world → items → villagers → enemies → mini-bosses
            #         → companions → player → HUD → overlays

            # 1. Draw the tile world (grass, paths, trees, portal gate)
            world.draw(screen)

            # 2. Draw collectible items
            for item in item_list:
                item.draw(screen)

            # 3. Draw villager NPCs
            for villager in villagers:
                villager.draw(screen, npc_font)

            # 4. Draw regular enemies (with health bars)
            for enemy in enemy_list:
                enemy.draw(screen)

            # 5. Draw mini-bosses (also have health bars via the Enemy parent class)
            for boss in miniboss_list:
                boss.draw(screen)

            # 6. Draw companion NPCs on top of enemies
            for companion in companions:
                companion.draw(screen)

            # 7. Draw the player on top of everything in the world
            player.draw(screen)

            # 8. Draw the HUD (health, endurance, strength, magic bars + portrait)
            draw_hud(screen, player, hud_font)

            # 9. Shard counter and level — top-right corner
            shard_text = hud_font.render(
                f"Shards: {player.shards_collected}   LVL {player.level}", True, (26, 188, 156))
            screen.blit(shard_text, (SCREEN_WIDTH - shard_text.get_width() - 12, 12))

            # 10. Show how many more shards until the next boss spawns
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

            # 11. Portal key indicator — shows if the player is carrying it
            if player.has_portal_key and not portal_open:
                key_hint = hud_font.render(
                    "[ Portal Key collected — walk to the gate to open it! ]", True, HERO_GOLD)
                screen.blit(key_hint,
                    (SCREEN_WIDTH // 2 - key_hint.get_width() // 2, SCREEN_HEIGHT - 50))

            # 12. ESC hint in the bottom-right corner
            draw_esc_hint(screen, hint_font)

            # 13. Pause overlay (on top of the game)
            if game_paused:
                draw_pause_overlay(screen, pause_fonts, pause_surfaces,
                                   audio_enabled, selected_setting_index)

            # 14. Death screen — on top of even the pause overlay
            if player.is_dead_flag:
                draw_death_screen(screen, death_font)

            # 15. Level-up overlay — the topmost layer of all
            if level_up_active:
                draw_level_up_overlay(screen, player, level_up_fonts, level_up_surfaces)

            # ── Show the Frame ─────────────────────────────
            pygame.display.flip()
            clock.tick(TARGET_FPS)
            await asyncio.sleep(0)

    pygame.quit()


# ── Entry Point ────────────────────────────────────────────
asyncio.run(main())
