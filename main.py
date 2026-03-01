# ============================================================
# main.py — The Ancient Wizard's Star
#
# This is the very first file Python runs when the game starts.
# It sets up the screen, runs the character selection, and then
# kicks off the main game loop where all the action happens!
# ============================================================

import asyncio
import pygame

# We import the Player class and the ATTACK_DAMAGE constant from the game folder
from game.player import Player, ATTACK_DAMAGE

# Import the World class, and the lists of where shards and potions start
from game.world   import World, SHARD_POSITIONS, HEALTH_POTION_POSITIONS

# Import the function that creates all the enemies
from game.enemies import create_enemy_group

# Import the function that creates all the friendly NPCs (companions + villagers)
from game.npc     import create_npc_group

# Import items — the factory function plus the two item types we use directly
from game.items   import create_items_group, HealthPotion, MagicalShard

# ── Screen & Game Constants ────────────────────────────────
# Keeping numbers up here with names makes them easy to find and change.

SCREEN_WIDTH  = 1280   # How wide the game window is, in pixels
SCREEN_HEIGHT =  720   # How tall the game window is, in pixels
TARGET_FPS    =   60   # We want the game to run at 60 frames per second — super smooth!
GAME_TITLE    = "The Ancient Wizard's Star"

# ── Background Color ───────────────────────────────────────
GRASS_GREEN = (76, 175, 80)   # A cheerful green for the placeholder world background
                               # (kept here even though the World now draws tiles — harmless!)

# ── HUD (Heads-Up Display) Constants ──────────────────────
# The HUD is the info overlay drawn on top of the game — health bars, energy bars, etc.
# These positions and sizes come directly from the Art Guide.

HEALTH_BAR_X      =  12    # How far from the left edge the health bar starts
HEALTH_BAR_Y      =  12    # How far from the top edge the health bar starts
HEALTH_BAR_WIDTH  = 120    # Total width of the health bar
HEALTH_BAR_HEIGHT =  16    # Height of the health bar

ENERGY_BAR_X      =  12    # Same left edge as the health bar — they line up neatly
ENERGY_BAR_Y      =  34    # A little lower than the health bar
ENERGY_BAR_WIDTH  = 120
ENERGY_BAR_HEIGHT =  16

PORTRAIT_X      =  12    # Character portrait position (top-left corner of the portrait box)
PORTRAIT_Y      =  60
PORTRAIT_SIZE   =  48    # The portrait is a 48 x 48 square

# Spacing between the right edge of a bar and its text label
HUD_LABEL_GAP_X   =   6   # Pixels of space between the bar and the "HP" / "EN" text
HUD_LABEL_NUDGE_Y =   1   # Tiny downward nudge so the text lines up with the center of the bar

# ── HUD Colors ─────────────────────────────────────────────
# From the Art Guide — these exact colors were chosen by the graphic designer!

HEALTH_BAR_FILL_COLOR  = (231,  76,  60)   # #E74C3C — bright red for current health
HEALTH_BAR_BG_COLOR    = ( 90,  26,  26)   # #5A1A1A — dark red for the empty part of the bar
ENERGY_BAR_FILL_COLOR  = (  0, 229, 255)   # #00E5FF — bright cyan for current energy
ENERGY_BAR_BG_COLOR    = (  0,  58,  69)   # #003A45 — dark cyan for the empty part of the bar
PORTRAIT_BORDER_COLOR  = (245, 200,  66)   # #F5C842 — hero gold for the portrait frame
OUTLINE_BLACK          = ( 26,  26,  26)   # #1A1A1A — very dark outline color
HERO_GOLD              = (245, 200,  66)   # #F5C842 — used for titles and highlights

# Colors used on the character selection screen
SELECT_SCREEN_BG    = ( 20,  20,  40)   # Very dark blue — feels magical
SELECT_SCREEN_TEXT  = (255, 255, 255)   # White text so it's easy to read
# Note: gold color on the selection screen uses HERO_GOLD defined above

# The six playable character classes, in the order keys 1–6 select them
CHARACTER_CLASSES = ["Wizard", "Knight", "Assassin", "Miner", "Ninja", "Robot"]

# ── Character Selection Screen Layout Constants ────────────
# Using named constants here means if we ever want to move things around,
# we only need to change the number in ONE place, not hunt through all the code!

SELECT_TITLE_Y    =  80   # Y position of the big gold title
SELECT_SUBTITLE_Y = 160   # Y position of the "Choose Your Hero!" subtitle
SELECT_OPTIONS_Y  = 230   # Y position of the first class option in the list
SELECT_OPTION_GAP =  45   # How many pixels apart each option is spaced vertically
SELECT_HINT_OFFSET =  60  # How many pixels up from the bottom of the screen the hint sits

# ── Pause Screen Constants ─────────────────────────────────
# Colors and sizes for the pause / options overlay

PAUSE_OVERLAY_COLOR  = (  0,   0,   0, 160)  # Black with alpha 160 — semi-transparent dim
PAUSE_PANEL_COLOR    = ( 20,  20,  40, 230)  # Dark blue panel, mostly opaque
PAUSE_TITLE_COLOR    = (245, 200,  66)        # #F5C842 Hero Gold — for "PAUSED" and section headings
PAUSE_BODY_COLOR     = (255, 255, 255)        # White — for regular text items
PAUSE_SELECT_COLOR   = (245, 200,  66)        # Gold highlight on the currently selected setting
PAUSE_PANEL_WIDTH    = 520   # How wide the pause panel is, in pixels
PAUSE_PANEL_HEIGHT   = 400   # How tall the pause panel is, in pixels

# How many items are in the SETTINGS section of the pause menu.
# Update this number when you add more settings to the pause menu!
NUM_SETTINGS = 1   # Right now there is only one setting: Audio ON/OFF


# ── Helper: Draw the HUD ───────────────────────────────────

def draw_hud(screen, player, hud_font):
    """Draw the health bar, energy bar, and character portrait onto the screen."""

    # ── Health Bar ─────────────────────────────────────────
    # First draw the dark background bar (represents missing health)
    health_bg_rect = pygame.Rect(HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, health_bg_rect)

    # Then draw the bright filled portion on top (represents remaining health)
    # get_health_fraction() gives us a number 0.0 to 1.0 so we can scale the bar width
    health_fill_width = int(HEALTH_BAR_WIDTH * player.get_health_fraction())
    if health_fill_width > 0:   # Only draw the fill if there is health remaining
        health_fill_rect = pygame.Rect(HEALTH_BAR_X, HEALTH_BAR_Y, health_fill_width, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(screen, HEALTH_BAR_FILL_COLOR, health_fill_rect)

    # Thin outline around the whole health bar so it looks crisp
    pygame.draw.rect(screen, OUTLINE_BLACK, health_bg_rect, width=1)

    # ── Energy Bar ─────────────────────────────────────────
    # Same idea as the health bar, but uses cyan colors and sits below the health bar
    energy_bg_rect = pygame.Rect(ENERGY_BAR_X, ENERGY_BAR_Y, ENERGY_BAR_WIDTH, ENERGY_BAR_HEIGHT)
    pygame.draw.rect(screen, ENERGY_BAR_BG_COLOR, energy_bg_rect)

    energy_fill_width = int(ENERGY_BAR_WIDTH * player.get_energy_fraction())
    if energy_fill_width > 0:   # Only draw fill if there is energy left
        energy_fill_rect = pygame.Rect(ENERGY_BAR_X, ENERGY_BAR_Y, energy_fill_width, ENERGY_BAR_HEIGHT)
        pygame.draw.rect(screen, ENERGY_BAR_FILL_COLOR, energy_fill_rect)

    pygame.draw.rect(screen, OUTLINE_BLACK, energy_bg_rect, width=1)

    # ── Character Portrait ─────────────────────────────────
    # For now this is just a gold-bordered box — real portrait art comes later!
    portrait_rect = pygame.Rect(PORTRAIT_X, PORTRAIT_Y, PORTRAIT_SIZE, PORTRAIT_SIZE)
    portrait_surface = player.get_portrait_surface(PORTRAIT_SIZE)
    screen.blit(portrait_surface, (PORTRAIT_X, PORTRAIT_Y))
    pygame.draw.rect(screen, PORTRAIT_BORDER_COLOR, portrait_rect, width=3)   # Gold border, 3 pixels thick

    # ── HUD Labels ─────────────────────────────────────────

    # "HP" label to the right of the health bar
    hp_label = hud_font.render(f"HP  {player.health}/{player.max_health}", True, (255, 255, 255))
    screen.blit(hp_label, (HEALTH_BAR_X + HEALTH_BAR_WIDTH + HUD_LABEL_GAP_X, HEALTH_BAR_Y + HUD_LABEL_NUDGE_Y))

    # "EN" label to the right of the energy bar
    en_label = hud_font.render(f"EN  {player.energy}/{player.max_energy}", True, (255, 255, 255))
    screen.blit(en_label, (ENERGY_BAR_X + ENERGY_BAR_WIDTH + HUD_LABEL_GAP_X, ENERGY_BAR_Y + HUD_LABEL_NUDGE_Y))


# ── Helper: Draw the "ESC = Menu" hint ────────────────────

def draw_esc_hint(screen, hint_font):
    """Draw a small hint in the bottom-right corner reminding the player how to return to the menu."""

    hint_surface = hint_font.render("ESC = Menu", True, (200, 200, 200))  # Light grey — unobtrusive

    # Position it 10 pixels from the right and bottom edges of the screen
    hint_x = SCREEN_WIDTH  - hint_surface.get_width()  - 10
    hint_y = SCREEN_HEIGHT - hint_surface.get_height() - 10

    screen.blit(hint_surface, (hint_x, hint_y))


# ── Helper: Draw the Pause Overlay ────────────────────────

def draw_pause_overlay(screen, pause_fonts, pause_surfaces, audio_enabled, selected_setting_index):
    """Draw the full-screen pause overlay with CONTROLS and SETTINGS sections.

    pause_fonts     — a dict with keys 'title', 'section', 'body' holding font objects
    pause_surfaces  — a dict with pre-built 'dim' and 'panel' Surface objects.
                      WHY pass them in? Building a pygame.Surface is slow — if we created them
                      inside this function they would be re-built 60 times per second while paused.
                      We build them ONCE in main() and just reuse them here every frame. Fast!
    audio_enabled   — True if audio is ON, False if audio is OFF
    selected_setting_index — which SETTINGS item is highlighted (0 = Audio toggle for now)
    """

    # ── Dim the game behind the panel ──────────────────────
    # The dim_surface is a semi-transparent black layer the size of the whole screen.
    # Drawing it on top of the game makes everything darker so the panel is easy to read.
    screen.blit(pause_surfaces["dim"], (0, 0))

    # ── Draw the dark panel in the center ──────────────────
    # The panel is a solid rectangle that sits on top of the dim layer.
    panel_x = SCREEN_WIDTH  // 2 - PAUSE_PANEL_WIDTH  // 2   # Center horizontally
    panel_y = SCREEN_HEIGHT // 2 - PAUSE_PANEL_HEIGHT // 2   # Center vertically

    screen.blit(pause_surfaces["panel"], (panel_x, panel_y))

    # Gold border around the panel so it looks clean
    panel_rect = pygame.Rect(panel_x, panel_y, PAUSE_PANEL_WIDTH, PAUSE_PANEL_HEIGHT)
    pygame.draw.rect(screen, HERO_GOLD, panel_rect, width=2)

    # ── "PAUSED" title at the top of the panel ─────────────
    title_surface = pause_fonts["title"].render("PAUSED", True, PAUSE_TITLE_COLOR)
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2   # Center it
    screen.blit(title_surface, (title_x, panel_y + 20))

    # ── CONTROLS section ───────────────────────────────────
    # This tells the player what every key does, so they never feel lost!
    controls_heading = pause_fonts["section"].render("CONTROLS", True, PAUSE_TITLE_COLOR)
    screen.blit(controls_heading, (panel_x + 30, panel_y + 80))

    # List every control, one line at a time
    controls_list = [
        "Arrow Keys / WASD  =  Move",
        "Shift              =  Run",
        "Space              =  Attack",
        "P                  =  Pause / Unpause",
        "ESC                =  Return to Menu",
    ]

    for line_index, control_text in enumerate(controls_list):
        # line_index goes 0, 1, 2, 3, 4 — multiply by 26 to space lines 26 pixels apart
        line_surface = pause_fonts["body"].render(control_text, True, PAUSE_BODY_COLOR)
        line_y = panel_y + 110 + line_index * 26
        screen.blit(line_surface, (panel_x + 30, line_y))

    # ── SETTINGS section ───────────────────────────────────
    settings_heading = pause_fonts["section"].render("SETTINGS", True, PAUSE_TITLE_COLOR)
    screen.blit(settings_heading, (panel_x + 30, panel_y + 240))

    # Audio toggle — shows ON or OFF depending on the current state
    audio_state_text = "ON" if audio_enabled else "OFF"
    audio_text = f"Audio:  {audio_state_text}"

    # Highlight the audio option in gold if it is currently selected, otherwise white
    audio_color = PAUSE_SELECT_COLOR if selected_setting_index == 0 else PAUSE_BODY_COLOR

    # Draw a small arrow ">" before the selected item so the player can see which one is highlighted
    if selected_setting_index == 0:
        arrow_surface = pause_fonts["body"].render(">", True, PAUSE_SELECT_COLOR)
        screen.blit(arrow_surface, (panel_x + 15, panel_y + 270))

    audio_surface = pause_fonts["body"].render(audio_text, True, audio_color)
    screen.blit(audio_surface, (panel_x + 30, panel_y + 270))

    # ── Footer hint at the bottom of the panel ─────────────
    footer_text = "P or ESC = Unpause   |   Up/Down = Navigate   |   Enter/Space = Toggle"
    footer_surface = pause_fonts["body"].render(footer_text, True, (160, 160, 160))  # Grey — subtle
    footer_x = SCREEN_WIDTH // 2 - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, panel_y + PAUSE_PANEL_HEIGHT - 35))


# ── Story Intro Screen ─────────────────────────────────────

async def run_story_intro(screen, clock, fonts):
    """Show a two-screen story intro before the game starts.

    Press Space, Enter, or ESC to skip each screen.
    Returns True if the intro finished, or False if the player closed the window.
    """

    # The intro is split into two screens — one for the world backstory, one for the quest
    intro_screens = [
        # Screen 1: What happened to Lumoria
        [
            "The world of Lumoria was once filled with magic.",
            "The Ancient Wizard's Star kept everything peaceful and bright.",
            "But Voltrak the Shockblade Eel cracked open the Dimensional Portal Gate",
            "and sent monsters flooding into the world. Lumoria is in danger!",
        ],
        # Screen 2: What the player needs to do
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
            # Check for events — did the player press a key or close the window?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False   # Player closed the window — stop everything
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False   # Move on to the next screen

            # Draw the intro screen — dark blue background like the character selection screen
            screen.fill(SELECT_SCREEN_BG)

            # Draw each line of text, centered on screen
            y_cursor = 180
            for line in screen_lines:
                if line == "YOUR QUEST:":
                    # The title line is bigger and gold
                    text_surface = fonts["small_bold"].render(line, True, HERO_GOLD)
                elif line == "":
                    # Empty string = blank line (add some extra space)
                    y_cursor += 20
                    continue
                else:
                    text_surface = fonts["small"].render(line, True, SELECT_SCREEN_TEXT)

                text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
                screen.blit(text_surface, (text_x, y_cursor))
                y_cursor += 44   # Space lines 44 pixels apart

            # Hint at the bottom so the player knows how to continue
            hint = fonts["hint"].render("Press Space or Enter to continue", True, HERO_GOLD)
            hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
            screen.blit(hint, (hint_x, SCREEN_HEIGHT - SELECT_HINT_OFFSET))

            pygame.display.flip()
            clock.tick(TARGET_FPS)
            await asyncio.sleep(0)   # Required for pygbag browser compatibility

    return True   # All intro screens shown — go ahead and start the game


# ── Helper: Character Selection Screen ────────────────────

async def run_character_selection(screen, clock, fonts):
    """Show the character selection screen and return the class the player chose.

    Returns the chosen class name (e.g. "Wizard"), or None if the player quit.

    fonts — a dict with keys 'big', 'small', 'hint' holding font objects created
            once in main() before this function is called.
    """

    # We keep looping until the player presses a key 1–6 or presses ESC / closes the window
    chosen_class = None

    # Map each number key to a character class
    key_to_class = {
        pygame.K_1: CHARACTER_CLASSES[0],   # 1 → Wizard
        pygame.K_2: CHARACTER_CLASSES[1],   # 2 → Knight
        pygame.K_3: CHARACTER_CLASSES[2],   # 3 → Assassin
        pygame.K_4: CHARACTER_CLASSES[3],   # 4 → Miner
        pygame.K_5: CHARACTER_CLASSES[4],   # 5 → Ninja
        pygame.K_6: CHARACTER_CLASSES[5],   # 6 → Robot
    }

    while chosen_class is None:
        # Handle events so the window doesn't freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None   # Player closed the window — signal the game to exit completely

            if event.type == pygame.KEYDOWN:
                # Check if they pressed a key that maps to a class
                if event.key in key_to_class:
                    chosen_class = key_to_class[event.key]

                # ESC on the selection screen quits the game entirely
                elif event.key == pygame.K_ESCAPE:
                    return None   # None means "exit the whole game"

        # ── Draw the selection screen ──────────────────────
        screen.fill(SELECT_SCREEN_BG)   # Dark blue background feels mysterious

        # Big gold title at the top
        title_surface = fonts["big"].render(GAME_TITLE, True, HERO_GOLD)
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2   # Center horizontally
        screen.blit(title_surface, (title_x, SELECT_TITLE_Y))

        # Subtitle
        sub_surface = fonts["small"].render("Choose Your Hero!", True, SELECT_SCREEN_TEXT)
        sub_x = SCREEN_WIDTH // 2 - sub_surface.get_width() // 2
        screen.blit(sub_surface, (sub_x, SELECT_SUBTITLE_Y))

        # List each class with its key number
        for index, class_name in enumerate(CHARACTER_CLASSES):
            # index goes 0, 1, 2, 3, 4, 5 — we add 1 so keys show as 1–6
            option_text = f"  {index + 1}  —  {class_name}"
            option_surface = fonts["small"].render(option_text, True, SELECT_SCREEN_TEXT)
            option_x = SCREEN_WIDTH // 2 - option_surface.get_width() // 2
            option_y = SELECT_OPTIONS_Y + index * SELECT_OPTION_GAP   # Stack options with the named gap
            screen.blit(option_surface, (option_x, option_y))

        # Small hint at the bottom — gold color so it stands out
        hint_surface = fonts["hint"].render("Press 1 - 6 to choose your character   |   ESC = Quit", True, HERO_GOLD)
        hint_x = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
        screen.blit(hint_surface, (hint_x, SCREEN_HEIGHT - SELECT_HINT_OFFSET))

        pygame.display.flip()   # Show everything we just drew
        clock.tick(TARGET_FPS)
        await asyncio.sleep(0)  # REQUIRED for pygbag — lets the browser breathe

    return chosen_class


# ── Main Game Loop ─────────────────────────────────────────

async def main():
    """Set up pygame and run the game from start to finish."""

    # Initialize pygame — this must happen before anything else
    pygame.init()

    # ── Create all fonts HERE, once, right after pygame.init() ────────────
    # WHY here and not inside draw functions?
    # Loading a font from the system is slow — it reads a file and builds a
    # whole font object. If we did that inside draw_hud() or draw() it would
    # happen 60 times per second, making the game slow and stuttery.
    # Creating fonts once here means we do that work only one time, then
    # reuse the same font object for every single frame. Fast!

    hud_font  = pygame.font.SysFont("Arial", 11)   # Small font for HP / EN labels in the HUD
    hint_font = pygame.font.SysFont("Arial", 13)   # Slightly larger for the "ESC = Menu" corner hint

    # Fonts for the character selection screen and the story intro
    select_fonts = {
        "big":        pygame.font.SysFont("Arial", 48, bold=True),  # Big bold title
        "small":      pygame.font.SysFont("Arial", 24),              # Class option list and intro body
        "small_bold": pygame.font.SysFont("Arial", 24, bold=True),  # Bold version for intro headings
        "hint":       pygame.font.SysFont("Arial", 18),              # Small hint at the bottom
    }

    # Fonts for the pause overlay
    pause_fonts = {
        "title":   pygame.font.SysFont("Arial", 42, bold=True),  # "PAUSED"
        "section": pygame.font.SysFont("Arial", 22, bold=True),  # "CONTROLS" / "SETTINGS"
        "body":    pygame.font.SysFont("Arial", 18),              # Individual items
    }

    # Small font for NPC speech bubbles — created once here so it's not recreated every frame
    npc_font = pygame.font.SysFont("Arial", 14)

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)   # Text shown in the window title bar

    # The clock keeps our game running at exactly 60 frames per second
    clock = pygame.time.Clock()

    # ── Pre-build the pause overlay surfaces ──────────────────────────────
    # Creating a pygame.Surface is slow — we don't want to do it 60 times per
    # second while the game is paused! So we build them ONCE here and reuse
    # them every frame. PAUSE_OVERLAY_COLOR and PAUSE_PANEL_COLOR are defined
    # at the top of this file.
    pause_surfaces = {
        "dim":   pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
        "panel": pygame.Surface((PAUSE_PANEL_WIDTH, PAUSE_PANEL_HEIGHT), pygame.SRCALPHA),
    }
    pause_surfaces["dim"].fill(PAUSE_OVERLAY_COLOR)
    pause_surfaces["panel"].fill(PAUSE_PANEL_COLOR)

    # ── Outer loop: keeps going back to the menu instead of quitting ───────
    # When the player presses ESC in-game, we want to return to character
    # selection, not exit the whole program. So we wrap everything in a loop
    # that only stops when the player truly wants to quit.

    app_running = True   # Set to False only when we want to exit completely

    while app_running:

        # ── Character Selection ────────────────────────────
        # Before the game starts, let the player pick who they want to be
        chosen_class = await run_character_selection(screen, clock, select_fonts)

        # If chosen_class is None, the player closed the window or pressed ESC on the menu
        if chosen_class is None:
            app_running = False   # Exit the whole program
            break

        # ── Story Intro ────────────────────────────────────
        # Show a two-screen summary of the world and the quest before the game begins
        intro_ok = await run_story_intro(screen, clock, select_fonts)
        if not intro_ok:
            app_running = False
            break

        # ── Create the Player ──────────────────────────────
        # Now that we know the class, we can build the player object
        player = Player(chosen_class, SCREEN_WIDTH, SCREEN_HEIGHT)

        # ── Create the World ───────────────────────────────
        # Create the tile world (grass, paths, trees, portal gate)
        world = World()

        # Create the 8 enemies — a mix of Evil Ninjas, Skeletons, and Zombies
        enemy_list = create_enemy_group()

        # Create the companion NPCs (they follow you) and villager NPCs (they give hints)
        companions, villagers = create_npc_group()

        # Create starting items: magical shards and health potions scattered around the world
        item_list = create_items_group(SHARD_POSITIONS)
        for pos in HEALTH_POTION_POSITIONS:
            item_list.append(HealthPotion(pos[0], pos[1]))

        # Track how many magical shards the player has collected
        shards_collected = 0

        # ── Pause state ────────────────────────────────────
        game_paused = False          # Is the game currently paused?
        audio_enabled = True         # Audio ON by default (placeholder — no sound system yet)
        selected_setting_index = 0   # Which SETTINGS item the cursor is on (0 = Audio toggle)

        # ── Game Loop ──────────────────────────────────────
        # This loop runs once every frame (up to 60 times per second).
        # It exits when the player presses ESC (return to menu) or closes the window.

        game_running = True
        while game_running:

            # ── Handle Events ──────────────────────────────
            # Events are things the player does: pressing keys, clicking the mouse, closing the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Player closed the window — exit everything
                    game_running = False
                    app_running  = False

                if event.type == pygame.KEYDOWN:

                    # ── ESC: return to character selection ──
                    if event.key == pygame.K_ESCAPE:
                        if game_paused:
                            # If paused, ESC just unpauses (same as pressing P)
                            game_paused = False
                        else:
                            # If not paused, ESC goes back to the character selection screen
                            game_running = False   # Exit the inner game loop; outer loop shows menu

                    # ── P: toggle the pause menu ────────────
                    elif event.key == pygame.K_p:
                        game_paused = not game_paused   # Flip between paused and unpaused

                    # ── Keys that only work while PAUSED ────
                    elif game_paused:

                        if event.key == pygame.K_UP:
                            # Move the selection cursor up (wrap around at the top)
                            selected_setting_index = max(0, selected_setting_index - 1)

                        elif event.key == pygame.K_DOWN:
                            # Move the selection cursor down.
                            # NUM_SETTINGS tells us how many items are in the list — we stop at the last one.
                            selected_setting_index = min(NUM_SETTINGS - 1, selected_setting_index + 1)

                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Toggle whichever setting is currently selected
                            if selected_setting_index == 0:
                                audio_enabled = not audio_enabled   # Flip ON/OFF

                    # ── Space: attack — only works when the game is not paused ──
                    elif event.key == pygame.K_SPACE:
                        # Space bar — player attacks!
                        # This is in the 'elif' chain after 'elif game_paused:', so it only
                        # runs when the game is NOT paused. No attacking through the menu!
                        player.handle_attack(event)

            # ── Update ─────────────────────────────────────
            # Only update (move) the player if the game is NOT paused.
            # While paused, the world freezes but we still draw the overlay.

            if not game_paused:
                # ── Check attack hits FIRST, before handle_input() resets the flag ──
                # WHY first? handle_attack() sets player.attacking = True in the event loop
                # (just above). But handle_input() resets it to False at its very start.
                # If we called handle_input() before this check, attacking would always be
                # False here and enemies would NEVER take damage. Order matters!
                if player.attacking:
                    attack_rect = player.get_attack_rect()
                    for enemy in enemy_list:
                        if not enemy.is_dead():
                            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.sprite_width, enemy.sprite_height)
                            if attack_rect.colliderect(enemy_rect):
                                enemy.take_damage(ATTACK_DAMAGE)

                # Read which keys are being held down right now
                keys_pressed = pygame.key.get_pressed()

                # Move the player based on the keys they're holding
                # NOTE: handle_input() resets player.attacking to False — that's why the
                # attack hit check must happen before this line.
                player.handle_input(keys_pressed)

                # Make sure the player can't walk off the screen
                player.keep_on_screen(SCREEN_WIDTH, SCREEN_HEIGHT)

                # Update the world (animates the portal gate and water tiles)
                world.update()

                # Update all enemies — they wander, chase the player, and attack on contact
                for enemy in enemy_list:
                    enemy.update(player)
                    # If an enemy was just defeated this frame, drop a magical shard at their position
                    if enemy.just_died:
                        item_list.append(MagicalShard(enemy.x, enemy.y))

                # Update companions — they follow the player
                for companion in companions:
                    companion.update(player)

                # Update villagers — they show hint bubbles when the player is nearby
                for villager in villagers:
                    villager.update(player)

                # Check if the player walked over any items and collected them
                for item in item_list[:]:   # Use item_list[:] (a copy) so we can safely remove items while looping
                    item.update()
                    if item.check_collection(player):
                        # Count magical shards separately so we can display them in the HUD
                        if isinstance(item, MagicalShard):
                            shards_collected += 1
                        item_list.remove(item)

            # ── Draw ───────────────────────────────────────────────────────
            # We draw in layers — things at the back go first, things on top go last.

            # 1. Draw the tile world (grass, paths, trees) — this replaces the plain green background
            world.draw(screen)

            # 2. Draw collectible items (shards and potions) — they sit on the ground
            for item in item_list:
                item.draw(screen)

            # 3. Draw villager NPCs — they stand in the world
            for villager in villagers:
                villager.draw(screen, npc_font)

            # 4. Draw enemies (with their health bars above them)
            for enemy in enemy_list:
                enemy.draw(screen)

            # 5. Draw companion NPCs on top of enemies so they're always visible
            for companion in companions:
                companion.draw(screen)

            # 6. Draw the player character on top of everything in the world
            player.draw(screen)

            # 7. Draw the HUD (health bar, energy bar, portrait) — always visible at the top
            draw_hud(screen, player, hud_font)

            # 8. Draw the shard counter in the top-right corner
            shard_text = hud_font.render(f"Shards: {shards_collected}", True, (26, 188, 156))
            screen.blit(shard_text, (SCREEN_WIDTH - shard_text.get_width() - 12, 12))

            # 9. Draw the "ESC = Menu" hint in the bottom-right corner
            draw_esc_hint(screen, hint_font)

            # 10. Draw the pause overlay on top of everything if the game is paused
            if game_paused:
                draw_pause_overlay(screen, pause_fonts, pause_surfaces, audio_enabled, selected_setting_index)

            # ── Show the Frame ─────────────────────────────
            pygame.display.flip()   # Flip sends everything we drew to the actual screen

            # Wait just long enough so we run at 60 FPS (not faster, not much slower)
            clock.tick(TARGET_FPS)

            # REQUIRED for pygbag — this tiny pause lets the browser handle other things
            await asyncio.sleep(0)

    # Clean up pygame when the whole app is done
    pygame.quit()


# ── Entry Point ────────────────────────────────────────────
# asyncio.run(main()) is the magic that starts the whole game!
# pygbag needs the async/await pattern to work in the browser.
asyncio.run(main())
