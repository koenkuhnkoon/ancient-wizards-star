"""game/items.py — Collectible items: magical shards and health potions.

Magical shards are dropped by enemies and give back a little energy.
Health potions sit in the world and restore some health when you walk over them.
Both items bob gently up and down so they're easy to spot.
"""

import math
from pathlib import Path

import pygame

# ---------------------------------------------------------------------------
# Constants — change these numbers to tweak how items feel
# ---------------------------------------------------------------------------

COLLECTION_RANGE   = 20    # Pixels — player collects item when their center is
                            # this close to the item center
FLOAT_SPEED        = 0.04  # How fast items bob up and down (pixels per frame)
FLOAT_RANGE        = 5     # How many pixels up and down the item travels
SHARD_ANIM_SPEED   = 10    # Game ticks between shard spin animation frames
HEALTH_POTION_HEAL = 3     # How much health a health potion restores

OUTLINE_COLOR = (26, 26, 26)   # Very dark outline used on placeholder sprites
ASSET_ROOT    = Path("assets") # All item sprites live inside the assets/ folder


# ---------------------------------------------------------------------------
# Helper functions — used by item classes below to load their sprites
# ---------------------------------------------------------------------------

def _load_static_sprite(filename, width, height, fallback_color):
    """Load a single PNG from assets/. If it's missing, return a colored
    placeholder instead so the game still runs while art is being made.

    filename       — e.g. "item_health_potion.png"
    width, height  — the expected size in pixels
    fallback_color — (R, G, B) colour used if the file can't be loaded
    """
    path = ASSET_ROOT / filename
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        # Make sure the image is exactly the right size
        if img.get_size() != (width, height):
            img = pygame.transform.scale(img, (width, height))
        return img
    except Exception:
        # File missing or broken — draw a solid coloured box instead
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(fallback_color)
        pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=1)
        return surface


def _load_animated_sheet(filename, frame_width, frame_height, frame_count, fallback_color):
    """Load a horizontal sprite sheet PNG and slice it into a list of frames.

    A sprite sheet is one big PNG that has all frames of an animation placed
    side by side, like a film strip. We cut it up here into separate pieces.

    filename               — e.g. "item_magical_shard.png"
    frame_width/height     — size of ONE frame in pixels
    frame_count            — how many frames are on the sheet
    fallback_color         — (R, G, B) used if the file can't be loaded
    """
    path = ASSET_ROOT / filename
    try:
        sheet = pygame.image.load(str(path)).convert_alpha()
        frames = []
        for i in range(frame_count):
            # Grab the i-th frame from left to right across the sheet
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(
                sheet,
                (0, 0),
                area=pygame.Rect(i * frame_width, 0, frame_width, frame_height),
            )
            frames.append(frame.convert_alpha())
        return frames
    except Exception:
        # Image is missing — make identical placeholder frames so the
        # animation code still works without crashing
        placeholder = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        placeholder.fill(fallback_color)
        pygame.draw.rect(placeholder, OUTLINE_COLOR, placeholder.get_rect(), width=1)
        return [placeholder] * frame_count   # All frames look the same


# ---------------------------------------------------------------------------
# Base class — shared behaviour for every collectible item
# ---------------------------------------------------------------------------

class Item:
    """The base class for all collectible items in the world.

    Every item:
    - Has a position (x, y) in the world
    - Bobs gently up and down (the 'float' animation)
    - Disappears once the player walks close enough to pick it up
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y         = float(y)  # Remember the starting Y for the float animation
        self.float_offset   = 0.0       # How far up/down from base_y the item currently is
        self.float_direction = 1        # +1 = moving up, -1 = moving down
        self.collected      = False     # Becomes True once the player picks this up

    def _get_center(self):
        """Return the (x, y) centre point of this item.

        Used when checking whether the player is close enough to collect it.
        Subclasses should override this if their sprite size is different.
        """
        # Default assumes a 16x16 sprite, so the centre is 8 pixels in from each edge
        return (self.x + 8, self.y + 8)

    def update(self):
        """Move the item gently up and down each game tick."""
        if self.collected:
            return   # No need to animate something already picked up

        # Nudge the float offset in the current direction
        self.float_offset += FLOAT_SPEED * self.float_direction

        # Reverse direction when we reach the top or bottom of the travel range
        if self.float_offset >= FLOAT_RANGE:
            self.float_direction = -1   # Start moving down
        elif self.float_offset <= 0:
            self.float_direction = 1    # Start moving up

    def check_collection(self, player):
        """Check if the player is close enough to collect this item.

        player — the Player object (must have .x and .y attributes)

        Returns True the moment the item is collected, False otherwise.
        """
        if self.collected:
            return False   # Already gone!

        # Find both centres
        item_cx, item_cy = self._get_center()

        # Player sprite is 48x48, so the centre is 24 pixels in from each edge
        player_cx = player.x + 24
        player_cy = player.y + 24

        # Pythagorean distance between the two centres
        dist = math.sqrt((player_cx - item_cx) ** 2 + (player_cy - item_cy) ** 2)

        if dist <= COLLECTION_RANGE:
            self._on_collected(player)   # Apply the item's effect
            self.collected = True
            return True

        return False

    def _on_collected(self, player):
        """What happens when the player picks up this item.

        Override this in each subclass to give the item its special effect.
        The base class does nothing on its own.
        """
        pass

    def draw(self, screen):
        """Draw the item on screen. Override in each subclass."""
        pass


# ---------------------------------------------------------------------------
# MagicalShard — spinning collectible dropped by enemies, restores energy
# ---------------------------------------------------------------------------

class MagicalShard(Item):
    """A glowing magical shard dropped by defeated enemies.

    Collect these to restore a bit of energy!
    The shard spins and bobs up and down to catch your eye.

    Sprite file: item_magical_shard.png
      - 64 x 16 pixels total (4 frames, each 16 x 16)
      - Frames play left-to-right to create a spin effect
    """

    def __init__(self, x, y):
        super().__init__(x, y)

        # Load the 4-frame spin animation from the sprite sheet.
        # item_magical_shard.png is 64px wide × 16px tall — 4 frames of 16×16.
        self.frames = _load_animated_sheet(
            "item_magical_shard.png",
            frame_width=16,
            frame_height=16,
            frame_count=4,
            fallback_color=(26, 188, 156),   # Teal placeholder if art is missing
        )
        self.frame_index = 0   # Which frame we're showing right now
        self.frame_tick  = 0   # Counts up every game tick; resets each time we advance a frame

    def _get_center(self):
        """Centre of a 16x16 shard sprite."""
        return (self.x + 8, self.y + 8)

    def update(self):
        """Float up and down AND spin through the animation frames."""
        super().update()   # Let the parent handle the floating

        if self.collected:
            return

        # Count ticks; when we hit SHARD_ANIM_SPEED, move to the next frame
        self.frame_tick += 1
        if self.frame_tick >= SHARD_ANIM_SPEED:
            self.frame_tick  = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def _on_collected(self, player):
        """Picking up a shard adds to the shard total — and might trigger a level-up!"""
        player.collect_shard()   # Let the Player track the count and check for level-ups

    def draw(self, screen):
        """Draw the current spin frame, shifted up or down by the float animation."""
        if self.collected:
            return
        draw_y = self.y + int(self.float_offset)
        screen.blit(self.frames[self.frame_index], (self.x, draw_y))


# ---------------------------------------------------------------------------
# HealthPotion — static sprite placed in the world, restores health
# ---------------------------------------------------------------------------

class HealthPotion(Item):
    """A red health potion sitting in the world, waiting to be picked up.

    Walk over it to restore some health!

    Sprite file: item_health_potion.png
      - 16 x 16 pixels, single static image (no animation frames)
    """

    def __init__(self, x, y):
        super().__init__(x, y)

        # Load the single potion image.
        # Red fallback colour if the art file isn't there yet.
        self.sprite = _load_static_sprite(
            "item_health_potion.png",
            width=16,
            height=16,
            fallback_color=(231, 76, 60),   # Red placeholder
        )

    def _get_center(self):
        """Centre of a 16x16 potion sprite."""
        return (self.x + 8, self.y + 8)

    def _on_collected(self, player):
        """Picking up a health potion restores some health!"""
        player.restore_health(HEALTH_POTION_HEAL)

    def draw(self, screen):
        """Draw the potion, shifted up or down by the float animation."""
        if self.collected:
            return
        draw_y = self.y + int(self.float_offset)
        screen.blit(self.sprite, (self.x, draw_y))


# ---------------------------------------------------------------------------
# PortalKey — dropped when both mini-bosses are defeated, opens the portal gate
# ---------------------------------------------------------------------------

class PortalKey(Item):
    """The Portal Key — a special item dropped when BOTH mini-bosses are defeated!

    Pick it up, then walk to the portal gate to open it and face the final boss.
    It glows golden so you know it's super important!

    Sprite file: item_portal_key.png — 20 x 20 px
    Fallback color: shiny gold if the art file isn't ready yet
    """

    def __init__(self, x, y):
        super().__init__(x, y)

        # Load the key sprite — gold colored placeholder if the file is missing
        self.sprite = _load_static_sprite(
            "item_portal_key.png",
            width=20,
            height=20,
            fallback_color=(245, 200, 66),   # Hero gold — shiny!
        )

    def _get_center(self):
        """Centre of a 20x20 key sprite."""
        return (self.x + 10, self.y + 10)

    def _on_collected(self, player):
        """The player picks up the Portal Key! Mark it on the player object."""
        player.has_portal_key = True   # main.py checks this flag near the portal

    def draw(self, screen):
        """Draw the key, shifted up or down by the float animation."""
        if self.collected:
            return
        draw_y = self.y + int(self.float_offset)
        screen.blit(self.sprite, (self.x, draw_y))


# ---------------------------------------------------------------------------
# Factory function — handy shortcut used by main.py to set up the level
# ---------------------------------------------------------------------------

def create_items_group(shard_positions):
    """Create a list of MagicalShard items at the given positions.

    shard_positions — a list of (x, y) tuples, one per shard you want in the world.
                      Example: [(200, 300), (450, 120), (700, 500)]

    Returns a plain Python list of Item objects.
    main.py can add HealthPotion objects to the same list afterwards.

    Example usage in main.py:
        items = create_items_group([(200, 300), (450, 120)])
        items.append(HealthPotion(600, 400))
    """
    items = []
    for x, y in shard_positions:
        items.append(MagicalShard(x, y))
    return items
