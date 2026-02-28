# ============================================================
# main.py — The Ancient Wizard's Star
#
# This is the very first file Python runs when the game starts.
# It sets up the screen, runs the character selection, and then
# kicks off the main game loop where all the action happens!
# ============================================================

import asyncio
import pygame

# We import the Player class from the game folder
from game.player import Player

# ── Screen & Game Constants ────────────────────────────────
# Keeping numbers up here with names makes them easy to find and change.

SCREEN_WIDTH  = 1280   # How wide the game window is, in pixels
SCREEN_HEIGHT =  720   # How tall the game window is, in pixels
TARGET_FPS    =   60   # We want the game to run at 60 frames per second — super smooth!
GAME_TITLE    = "The Ancient Wizard's Star"

# ── Background Color ───────────────────────────────────────
GRASS_GREEN = (76, 175, 80)   # A cheerful green for the placeholder world background

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
SELECT_HIGHLIGHT    = (245, 200,  66)   # Gold for the title

# The six playable character classes, in the order keys 1–6 select them
CHARACTER_CLASSES = ["Wizard", "Knight", "Assassin", "Miner", "Ninja", "Robot"]


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
    pygame.draw.rect(screen, PORTRAIT_BORDER_COLOR, portrait_rect, width=3)   # Gold border, 3 pixels thick

    # ── HUD Labels ─────────────────────────────────────────

    # "HP" label to the right of the health bar
    hp_label = hud_font.render(f"HP  {player.health}/{player.max_health}", True, (255, 255, 255))
    screen.blit(hp_label, (HEALTH_BAR_X + HEALTH_BAR_WIDTH + 6, HEALTH_BAR_Y + 1))

    # "EN" label to the right of the energy bar
    en_label = hud_font.render(f"EN  {player.energy}/{player.max_energy}", True, (255, 255, 255))
    screen.blit(en_label, (ENERGY_BAR_X + ENERGY_BAR_WIDTH + 6, ENERGY_BAR_Y + 1))


# ── Helper: Character Selection Screen ────────────────────

async def run_character_selection(screen, clock):
    """Show the character selection screen and return the class the player chose."""

    # We keep looping until the player presses a key 1–6
    chosen_class = None
    selection_font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    selection_font_small = pygame.font.SysFont("Arial", 24)
    selection_font_hint  = pygame.font.SysFont("Arial", 18)

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
                pygame.quit()
                return None   # Player closed the window — signal the game to exit

            if event.type == pygame.KEYDOWN:
                # Check if they pressed a key that maps to a class
                if event.key in key_to_class:
                    chosen_class = key_to_class[event.key]

        # ── Draw the selection screen ──────────────────────
        screen.fill(SELECT_SCREEN_BG)   # Dark blue background feels mysterious

        # Big gold title at the top
        title_surface = selection_font_big.render(GAME_TITLE, True, HERO_GOLD)
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2   # Center horizontally
        screen.blit(title_surface, (title_x, 80))

        # Subtitle
        sub_surface = selection_font_small.render("Choose Your Hero!", True, SELECT_SCREEN_TEXT)
        sub_x = SCREEN_WIDTH // 2 - sub_surface.get_width() // 2
        screen.blit(sub_surface, (sub_x, 160))

        # List each class with its key number
        for index, class_name in enumerate(CHARACTER_CLASSES):
            # index goes 0, 1, 2, 3, 4, 5 — we add 1 so keys show as 1–6
            option_text = f"  {index + 1}  —  {class_name}"
            option_surface = selection_font_small.render(option_text, True, SELECT_SCREEN_TEXT)
            option_x = SCREEN_WIDTH // 2 - option_surface.get_width() // 2
            option_y = 230 + index * 45   # Stack options 45 pixels apart vertically
            screen.blit(option_surface, (option_x, option_y))

        # Small hint at the bottom
        hint_surface = selection_font_hint.render("Press 1 - 6 to choose your character", True, HERO_GOLD)
        hint_x = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
        screen.blit(hint_surface, (hint_x, SCREEN_HEIGHT - 60))

        pygame.display.flip()   # Show everything we just drew
        clock.tick(TARGET_FPS)
        await asyncio.sleep(0)  # REQUIRED for pygbag — lets the browser breathe

    return chosen_class


# ── Main Game Loop ─────────────────────────────────────────

async def main():
    """Set up pygame and run the game from start to finish."""

    # Initialize pygame — this must happen before anything else
    pygame.init()

    # We create the HUD font here once — creating fonts inside the game loop every frame would be slow
    hud_font = pygame.font.SysFont("Arial", 11)

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)   # Text shown in the window title bar

    # The clock keeps our game running at exactly 60 frames per second
    clock = pygame.time.Clock()

    # ── Character Selection ────────────────────────────────
    # Before the game starts, let the player pick who they want to be
    chosen_class = await run_character_selection(screen, clock)

    # If chosen_class is None the player closed the window during selection
    if chosen_class is None:
        pygame.quit()
        return

    # ── Create the Player ──────────────────────────────────
    # Now that we know the class, we can build the player object
    player = Player(chosen_class, SCREEN_WIDTH, SCREEN_HEIGHT)

    # ── Game Loop ──────────────────────────────────────────
    # This loop runs once every frame (up to 60 times per second)
    game_running = True
    while game_running:

        # ── Handle Events ──────────────────────────────────
        # Events are things the player does: pressing keys, clicking the mouse, closing the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False   # Player closed the window — stop the loop

        # ── Update ─────────────────────────────────────────
        # Read which keys are being held down right now
        keys_pressed = pygame.key.get_pressed()

        # Move the player based on the keys they're holding
        player.handle_input(keys_pressed)

        # Make sure the player can't walk off the screen
        player.keep_on_screen(SCREEN_WIDTH, SCREEN_HEIGHT)

        # ── Draw ───────────────────────────────────────────
        # We draw in layers — background first, then characters, then HUD on top

        # 1. Fill the whole screen with green to represent the ground/grass
        screen.fill(GRASS_GREEN)

        # 2. Draw the player character on top of the background
        player.draw(screen)

        # 3. Draw the HUD (health/energy bars) on top of everything
        draw_hud(screen, player, hud_font)

        # ── Show the Frame ─────────────────────────────────
        pygame.display.flip()   # Flip sends everything we drew to the actual screen

        # Wait just long enough so we run at 60 FPS (not faster, not much slower)
        clock.tick(TARGET_FPS)

        # REQUIRED for pygbag — this tiny pause lets the browser handle other things
        await asyncio.sleep(0)

    # Clean up pygame when the game is done
    pygame.quit()


# ── Entry Point ────────────────────────────────────────────
# asyncio.run(main()) is the magic that starts the whole game!
# pygbag needs the async/await pattern to work in the browser.
asyncio.run(main())
