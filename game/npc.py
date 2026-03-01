"""game/npc.py — Friendly characters in the world of Lumoria.

This file has companion fighters who follow the player, and villagers
who share helpful hints when you walk up to them.

Written for The Ancient Wizard's Star (Python + Pygame).
Made by a dad and his 8-year-old son — keep it simple and fun!
"""

# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
import math               # we need math to calculate distances
from pathlib import Path  # lets us build file paths the safe way
import pygame             # the game library


# ------------------------------------------------------------------
# Constants — change these numbers to tune how NPCs behave!
# ------------------------------------------------------------------

# How close a companion gets before it stops following the player.
# If we let them get too close, they'd walk on top of the player!
COMPANION_FOLLOW_DISTANCE = 80   # pixels

# How fast a companion moves when it's chasing the player
COMPANION_SPEED = 3              # pixels per frame

# How close the player must be to a villager to trigger their hint bubble
DIALOGUE_TRIGGER_RANGE = 80     # pixels

# How many frames the hint bubble stays on screen (60 frames = 1 second)
# 300 frames = 5 seconds — long enough to read comfortably!
DIALOGUE_DISPLAY_TICKS = 300    # frames

# Padding is the gap between the bubble's edge and the text inside it
BUBBLE_PADDING = 8              # pixels on each side

# Speech bubble colours — warm and friendly!
BUBBLE_COLOR        = (240, 240, 200)  # pale yellow background
BUBBLE_TEXT_COLOR   = ( 30,  30,  30)  # very dark text — easy to read
BUBBLE_BORDER_COLOR = (100,  80,  20)  # dark gold border

# Dark outline colour used on placeholder sprites
OUTLINE_COLOR = (26, 26, 26)

# All game images live inside the assets/ folder
ASSET_ROOT = Path("assets")


# ------------------------------------------------------------------
# _load_sprite() — module-level helper used by every NPC class
# ------------------------------------------------------------------

def _load_sprite(filename, width, height, fallback_color):
    """Load a PNG sprite from assets/. If the file is missing, return a coloured placeholder.

    Why a placeholder?  Art files get added slowly while the game code grows.
    A coloured rectangle lets us run and test the game before every picture is ready.

    Args:
        filename       — the PNG file name (e.g. "npc_villager.png")
        width, height  — the size we want the sprite to be
        fallback_color — an (R, G, B) colour to use if the file is missing
    """
    path = ASSET_ROOT / filename
    try:
        # Try to load the real PNG file
        img = pygame.image.load(str(path)).convert_alpha()

        # Make sure the image is exactly the right size
        if img.get_size() != (width, height):
            img = pygame.transform.scale(img, (width, height))

        return img

    except Exception:
        # File is missing or couldn't be loaded — make a coloured rectangle instead
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(fallback_color)
        # Draw a dark outline so we can see where the sprite is
        pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=2)
        return surface


# ------------------------------------------------------------------
# NPC — the base class that all friendly characters inherit from
# ------------------------------------------------------------------

class NPC:
    """The base class for all friendly characters in the world.

    A 'base class' is like a recipe that other classes (Villager,
    CompanionKnight, CompanionWizard) borrow from and build on top of.
    It holds the things every NPC has in common:
      - a position (x, y)
      - a sprite image
      - a way to draw itself
      - a way to figure out how far away the player is
    """

    def __init__(self, x, y, sprite):
        """Set up the NPC at position (x, y) with the given sprite image.

        In Pygame, (0, 0) is the top-left corner of the screen.
        x grows to the right; y grows downward.
        """
        self.x = x                              # pixels from the left edge of the screen
        self.y = y                              # pixels from the top edge of the screen
        self.sprite = sprite                    # the image we draw on screen
        self.sprite_width  = sprite.get_width()   # how many pixels wide the sprite is
        self.sprite_height = sprite.get_height()  # how many pixels tall the sprite is

    def get_center(self):
        """Return the center point of this NPC as a (x, y) tuple.

        We use the center when measuring distances — it's more accurate
        than measuring from the top-left corner!
        """
        center_x = self.x + self.sprite_width  // 2
        center_y = self.y + self.sprite_height // 2
        return (center_x, center_y)

    def _distance_to_player(self, player):
        """Calculate how far away the player is (in pixels).

        We use the Pythagorean theorem: distance = sqrt( dx² + dy² )
        That's the straight-line distance between two points.

        The player sprite is 48×48 px, so its center is 24 px from its top-left corner.
        """
        npc_x, npc_y = self.get_center()

        # Player center — player sprites are always 48×48, so center is at +24
        player_x = player.x + 24
        player_y = player.y + 24

        # Pythagorean theorem to get the straight-line distance
        dx = player_x - npc_x
        dy = player_y - npc_y
        return math.sqrt(dx * dx + dy * dy)

    def draw(self, screen):
        """Draw the NPC sprite on the screen at its current position."""
        screen.blit(self.sprite, (self.x, self.y))


# ------------------------------------------------------------------
# Villager — a friendly hint-giver who stands still
# ------------------------------------------------------------------

class Villager(NPC):
    """A friendly villager who stands in one spot and shares helpful hints.

    When you walk close to them, a speech bubble appears above their head!
    The bubble stays visible for DIALOGUE_DISPLAY_TICKS frames, then fades away.
    Walk close again to see the hint a second time.
    """

    def __init__(self, x, y, hint_text):
        """Create a villager at position (x, y) with a hint message.

        Args:
            x, y      — where in the world the villager stands (in pixels)
            hint_text — the message they share when the player comes near
        """
        # Load the villager sprite — 44×44 px, green placeholder if file is missing
        sprite = _load_sprite("npc_villager.png", 44, 44, (60, 160, 80))
        super().__init__(x, y, sprite)

        self.hint_text      = hint_text   # the message this villager will say
        self.dialogue_ticks = 0           # counts down while the speech bubble is showing;
                                          # 0 means the bubble is hidden

    def update(self, player):
        """Check if the player is nearby; if so, show the hint bubble.

        This is called once every frame (60 times per second) by the game loop.
        """
        dist = self._distance_to_player(player)

        # Only start the bubble if the player is close AND the bubble isn't already showing.
        # The second condition stops the bubble from restarting every single frame.
        if dist < DIALOGUE_TRIGGER_RANGE and self.dialogue_ticks <= 0:
            self.dialogue_ticks = DIALOGUE_DISPLAY_TICKS   # start the countdown!

    def draw(self, screen, font):
        """Draw the villager and their speech bubble if the bubble is active.

        Args:
            screen — the Pygame surface we're drawing onto
            font   — the Pygame font used to render the hint text
        """
        # Draw the sprite first (from the NPC base class)
        super().draw(screen)

        # If the bubble is still counting down, show it and tick down by one
        if self.dialogue_ticks > 0:
            self._draw_bubble(screen, font, self.hint_text)
            self.dialogue_ticks -= 1   # one frame closer to the bubble disappearing

    def _draw_bubble(self, screen, font, text):
        """Draw a speech bubble with text floating above the NPC.

        Steps:
          1. Measure how big the text is
          2. Size the bubble to fit around the text (with padding)
          3. Position it above the NPC's head, centered horizontally
          4. Clamp it so it doesn't go off the screen edges
          5. Draw the bubble background, border, then the text
        """
        # Step 1 — measure the text so we know how big the bubble needs to be
        text_surface = font.render(text, True, BUBBLE_TEXT_COLOR)
        text_width   = text_surface.get_width()
        text_height  = text_surface.get_height()

        # Step 2 — the bubble is the text size plus padding on all four sides
        bubble_width  = text_width  + BUBBLE_PADDING * 2
        bubble_height = text_height + BUBBLE_PADDING * 2

        # Step 3 — position the bubble above the NPC's head, centered over it
        bubble_x = self.x + self.sprite_width  // 2 - bubble_width  // 2
        bubble_y = self.y - bubble_height - 8   # 8 pixels above the NPC's top edge

        # Step 4 — clamp so the bubble stays on screen (screen is 1280 pixels wide)
        bubble_x = max(4, min(bubble_x, 1280 - bubble_width - 4))
        bubble_y = max(4, bubble_y)   # don't let it go above the top of the screen

        # Step 5a — draw the pale yellow bubble background
        pygame.draw.rect(
            screen,
            BUBBLE_COLOR,
            (bubble_x, bubble_y, bubble_width, bubble_height),
            border_radius=6,   # rounded corners look friendlier!
        )

        # Step 5b — draw the dark gold border around the bubble
        pygame.draw.rect(
            screen,
            BUBBLE_BORDER_COLOR,
            (bubble_x, bubble_y, bubble_width, bubble_height),
            width=2,
            border_radius=6,
        )

        # Step 5c — draw the text inside the bubble (offset by BUBBLE_PADDING)
        screen.blit(text_surface, (bubble_x + BUBBLE_PADDING, bubble_y + BUBBLE_PADDING))


# ------------------------------------------------------------------
# CompanionKnight — a brave fighter who follows the player
# ------------------------------------------------------------------

class CompanionKnight(NPC):
    """The Companion Knight follows you on your adventure!

    They're always close by, ready to fight alongside you.
    They move toward you when you walk far away, but stop when they're
    within COMPANION_FOLLOW_DISTANCE pixels so they don't crowd you.
    """

    def __init__(self, x, y):
        """Create the Companion Knight at position (x, y).

        Sprite: npc_companion_knight.png — 48×48 px
        Fallback colour: steel blue (70, 130, 180)
        """
        sprite = _load_sprite("npc_companion_knight.png", 48, 48, (70, 130, 180))
        super().__init__(x, y, sprite)

    def update(self, player):
        """Follow the player, but stop when close enough — don't crowd them!

        How it works:
          1. Measure the distance to the player
          2. If far enough away, work out the direction toward the player
          3. Move COMPANION_SPEED pixels in that direction
        """
        dist = self._distance_to_player(player)

        # Only move if we're farther away than the follow distance
        if dist > COMPANION_FOLLOW_DISTANCE:
            npc_x, npc_y = self.get_center()

            # Player's center position
            player_x = player.x + 24
            player_y = player.y + 24

            # Work out the direction to the player as a unit vector
            # (dividing by dist turns it into a direction with length exactly 1)
            direction_x = (player_x - npc_x) / dist
            direction_y = (player_y - npc_y) / dist

            # Move toward the player by COMPANION_SPEED pixels this frame
            self.x += int(direction_x * COMPANION_SPEED)
            self.y += int(direction_y * COMPANION_SPEED)

    def draw(self, screen):
        """Draw the companion knight on the screen."""
        super().draw(screen)


# ------------------------------------------------------------------
# CompanionWizard — a magical supporter who follows the player
# ------------------------------------------------------------------

class CompanionWizard(NPC):
    """The Companion Wizard follows you too — with magical support!

    They behave exactly like the Companion Knight (follow and stop),
    but have a different look (purple placeholder) and sprite file.
    In a future update, the wizard might cast spells from a distance!
    """

    def __init__(self, x, y):
        """Create the Companion Wizard at position (x, y).

        Sprite: npc_companion_wizard.png — 48×48 px
        Fallback colour: purple (148, 0, 211)
        """
        sprite = _load_sprite("npc_companion_wizard.png", 48, 48, (148, 0, 211))
        super().__init__(x, y, sprite)

    def update(self, player):
        """Follow the player, keeping a comfortable distance.

        Same logic as CompanionKnight — measure, check distance, then move.
        """
        dist = self._distance_to_player(player)

        # Only move if farther away than the follow distance
        if dist > COMPANION_FOLLOW_DISTANCE:
            npc_x, npc_y = self.get_center()

            # Player's center position
            player_x = player.x + 24
            player_y = player.y + 24

            # Calculate the direction to the player
            direction_x = (player_x - npc_x) / dist
            direction_y = (player_y - npc_y) / dist

            # Move toward the player
            self.x += int(direction_x * COMPANION_SPEED)
            self.y += int(direction_y * COMPANION_SPEED)

    def draw(self, screen):
        """Draw the companion wizard on the screen."""
        super().draw(screen)


# ------------------------------------------------------------------
# create_npc_group() — factory function to build all NPCs at once
# ------------------------------------------------------------------

def create_npc_group():
    """Create all the NPCs that live in the world of Lumoria.

    Spawn positions come from NPC_SPAWN_POINTS in game/world.py:
      companion_knight → (700, 370)
      companion_wizard → (580, 370)
      villager_1       → (200, 310)
      villager_2       → (600, 200)

    The player starts near the screen centre (640, 360), so the
    companions start just to the right and left of the player.

    Returns:
        companions — list: [CompanionKnight, CompanionWizard]
                     These follow the player around the world.
        villagers  — list: [Villager, Villager]
                     These stand still and share hints when you walk near.
    """

    # --- Companions ---
    # They start near the player's starting position so they feel nearby right away
    companion_knight = CompanionKnight(700, 370)   # just to the right of the player
    companion_wizard = CompanionWizard(580, 370)   # just to the left of the player

    # --- Villagers ---
    # Scattered around the world — each gives a different useful tip!
    villager_1 = Villager(
        200, 310,
        "Be careful near the eastern swamp — those sewage creatures are extra grumpy!",
    )
    villager_2 = Villager(
        600, 200,
        "The Ancient Wizard's Star smells like fresh rain. Please save it!",
    )

    companions = [companion_knight, companion_wizard]
    villagers  = [villager_1, villager_2]

    return companions, villagers
