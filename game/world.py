"""game/world.py — The land of Lumoria.

Draws all the map tiles and animates the portal gate.
Written for The Ancient Wizard's Star (Python + Pygame).
Made by a dad and his 8-year-old son — keep it simple and fun!
"""

# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
from pathlib import Path     # lets us build file paths the safe way
import pygame                # the game library

# ------------------------------------------------------------------
# Constants — change these to resize the world!
# ------------------------------------------------------------------

# Each tile is a 32x32-pixel square
TILE_SIZE = 32

# The map is 40 tiles wide × 22 tiles tall (fills a 1280×704 window)
MAP_COLS = 40
MAP_ROWS = 22

# Tile type IDs — these are just numbers that stand for tile kinds
TILE_GRASS = 0
TILE_DIRT  = 1
TILE_WALL  = 2
TILE_TREE  = 3
TILE_WATER = 4

# Where the portal gate is drawn (in pixels from the top-left corner)
PORTAL_X = 1050
PORTAL_Y = 200

# How many game ticks pass before the portal moves to its next animation frame
# (lower number = faster animation)
PORTAL_FRAME_SPEED = 8

# All game images live inside the assets/ folder
ASSET_ROOT = Path("assets")

# A very dark colour used to draw outlines on placeholder tiles
OUTLINE_COLOR = (26, 26, 26)

# ------------------------------------------------------------------
# Fallback colours — used when a tile PNG is missing
# We pick colours that look roughly right so the game still runs!
# ------------------------------------------------------------------
FALLBACK_COLORS = {
    TILE_GRASS: (76,  175,  80),   # leafy green
    TILE_DIRT:  (139, 115,  85),   # brown earth
    TILE_WALL:  (100, 100, 100),   # grey stone
    TILE_TREE:  (34,  139,  34),   # forest green
    TILE_WATER: (64,  164, 223),   # sky blue
}

FALLBACK_PORTAL_COLOR = (150, 0, 200)   # purple glow for a missing portal

# ------------------------------------------------------------------
# MAP_GRID
#
# This is the map of Lumoria!  Each row is a list of 40 numbers.
# Row 0 is the TOP of the screen; row 21 is the BOTTOM.
#
# Short aliases to keep the lines readable:
#   G = grass, D = dirt path, W = wall, T = tree, A = water
# ------------------------------------------------------------------
G = TILE_GRASS
D = TILE_DIRT
W = TILE_WALL
T = TILE_TREE
A = TILE_WATER

MAP_GRID = [
    # row 0 — top wall (all stone)
    [W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W],

    # row 1 — just inside the top wall
    [W,G,G,G,G,G,G,G,G,G, G,G,T,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,T,G,G,G,G,G,W],

    # row 2
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 3
    [W,G,G,T,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,T,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 4
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,T,G, G,G,G,G,G,G,G,G,G,W],

    # row 5
    [W,G,G,G,G,G,G,T,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 6
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,T,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,T,G,W],

    # row 7
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 8 — the dirt path starts to wiggle up here
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 9 — path wiggles up a row here (columns 20-27)
    [W,G,G,D,D,D,D,D,D,D, D,D,D,D,D,D,D,D,D,D, D,D,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 10 — main dirt path
    [W,G,G,D,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,D,D,D,D,D,D,D,D, D,D,D,D,D,D,G,G,G,W],

    # row 11 — main dirt path (middle lane)
    [W,G,G,D,G,G,T,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,D,G,G,G,G,G,W],

    # row 12 — path wiggles down a row here (columns 3-21)
    [W,G,G,D,D,D,D,D,D,D, D,D,D,D,D,D,D,D,D,D, D,D,G,G,G,G,G,G,G,G, G,G,G,D,G,G,G,G,G,W],

    # row 13
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,T, G,G,G,D,G,G,G,G,G,W],

    # row 14 — water patch columns 4-6
    [W,G,G,G,A,A,A,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,D,G,G,G,T,G,W],

    # row 15 — water patch columns 4-6
    [W,G,G,G,A,A,A,G,G,G, G,G,T,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,D,G,G,G,G,G,W],

    # row 16 — water patch columns 4-6
    [W,G,G,G,A,A,A,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,T,G,G,G,G,G, G,G,G,D,G,G,G,G,G,W],

    # row 17
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,D,G,G,G,G,G,W],

    # row 18
    [W,G,T,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,D,D,D,G,G,G,W],

    # row 19
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,T,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,D,G,G,G,W],

    # row 20 — just inside the bottom wall
    [W,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,G, G,G,G,G,G,G,G,G,G,W],

    # row 21 — bottom wall (all stone)
    [W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W, W,W,W,W,W,W,W,W,W,W],
]

# ------------------------------------------------------------------
# Spawn points — where things start on the map
# ------------------------------------------------------------------

# Where enemies first appear (x, y in pixels)
ENEMY_SPAWN_POINTS = [
    (160, 200),
    (320, 480),
    (500, 150),
    (700, 400),
    (250, 530),
    (850, 180),
    (600, 560),
    (400, 300),
]

# Where friendly companion NPCs start
# The player starts near the screen centre (640, 360)
NPC_SPAWN_POINTS = {
    "companion_knight": (700, 370),
    "companion_wizard": (580, 370),
    "villager_1":       (200, 310),
    "villager_2":       (600, 200),
}

# Where health potions are waiting to be picked up
HEALTH_POTION_POSITIONS = [(300, 200), (750, 500), (500, 350)]

# Where magical shards are scattered around the world
SHARD_POSITIONS = [(200, 400), (400, 150), (650, 300), (900, 450), (350, 500)]


# ------------------------------------------------------------------
# World class
# ------------------------------------------------------------------

class World:
    """The World knows what every tile looks like and draws the whole map.

    It also animates the water tiles and the glowing portal gate.
    """

    def __init__(self):
        # --- Load static tile images (they don't move) ---
        self.tile_images = {
            TILE_GRASS: self._load_static_tile("tile_grass.png",  FALLBACK_COLORS[TILE_GRASS]),
            TILE_DIRT:  self._load_static_tile("tile_dirt.png",   FALLBACK_COLORS[TILE_DIRT]),
            TILE_WALL:  self._load_static_tile("tile_wall.png",   FALLBACK_COLORS[TILE_WALL]),
            TILE_TREE:  self._load_static_tile("tile_tree_top.png", FALLBACK_COLORS[TILE_TREE]),
        }

        # --- Load animated water frames ---
        # Water has 4 frames that play in a loop to look like it's rippling
        self.water_frames = self._load_animated_sheet(
            filename     = "tile_water.png",
            frame_width  = TILE_SIZE,
            frame_height = TILE_SIZE,
            frame_count  = 4,
        )

        # --- Load animated portal gate frames ---
        # The portal gate has 8 frames.  Its PNG is 1024 px wide even though
        # 8 × 96 = 768 px — that's fine, we just read the first 8 frames.
        self.portal_frames = self._load_animated_sheet(
            filename     = "world_portal_gate.png",
            frame_width  = 96,
            frame_height = 128,
            frame_count  = 8,
        )

        # --- Animation state ---
        # frame_tick counts up every game update; when it reaches PORTAL_FRAME_SPEED
        # we move to the next portal picture.
        self.frame_tick          = 0   # counts game ticks
        self.portal_frame_index  = 0   # which portal picture we're showing
        self.water_frame_index   = 0   # which water picture we're showing

    # ------------------------------------------------------------------
    # Private helper: load a single static tile image
    # ------------------------------------------------------------------
    def _load_static_tile(self, filename: str, fallback_color: tuple) -> pygame.Surface:
        """Try to load a tile PNG from the assets folder.

        If the file is missing or broken, we make a coloured square instead
        so the game still runs even without all the artwork.
        """
        tile_path = ASSET_ROOT / filename
        try:
            if not tile_path.exists():
                # File not there yet — use a coloured placeholder
                raise FileNotFoundError(f"Missing tile: {tile_path}")

            image = pygame.image.load(str(tile_path)).convert_alpha()

            # Make sure the tile is exactly TILE_SIZE × TILE_SIZE
            if image.get_size() != (TILE_SIZE, TILE_SIZE):
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

            return image

        except Exception:
            # Something went wrong — draw a coloured square so we can still see the map
            return self._make_placeholder_tile(fallback_color)

    # ------------------------------------------------------------------
    # Private helper: load an animated sprite sheet and slice it into frames
    # ------------------------------------------------------------------
    def _load_animated_sheet(
        self,
        filename:     str,
        frame_width:  int,
        frame_height: int,
        frame_count:  int,
    ) -> list:
        """Load a horizontal sprite sheet PNG and slice it into a list of frames.

        A sprite sheet is one wide image with all the animation frames side by side.
        We cut it into equal pieces, one per frame.

        If the file is missing we return a list of placeholder coloured squares.
        """
        sheet_path = ASSET_ROOT / filename
        try:
            if not sheet_path.exists():
                raise FileNotFoundError(f"Missing sheet: {sheet_path}")

            sheet = pygame.image.load(str(sheet_path)).convert_alpha()

            # Slice the sheet — same pattern as _slice_sheet in game/assets.py
            frames = []
            for index in range(frame_count):
                # Make a blank surface the right size for one frame
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)

                # Copy the correct slice of the sheet onto the blank frame
                source_rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
                frame.blit(sheet, (0, 0), area=source_rect)

                frames.append(frame.convert_alpha())

            return frames

        except Exception:
            # Sheet missing or broken — build placeholder frames
            return self._make_placeholder_frames(frame_width, frame_height, frame_count)

    # ------------------------------------------------------------------
    # Private helper: make a solid-coloured placeholder tile surface
    # ------------------------------------------------------------------
    def _make_placeholder_tile(self, color: tuple) -> pygame.Surface:
        """Return a TILE_SIZE × TILE_SIZE coloured square with a dark outline.

        We use this whenever a tile PNG hasn't been drawn yet.
        The dark outline helps us see where tiles are on the map.
        """
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surface.fill(color)
        # Draw the dark outline (2 pixels thick)
        pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=2)
        return surface

    # ------------------------------------------------------------------
    # Private helper: make a list of placeholder frames for an animation
    # ------------------------------------------------------------------
    def _make_placeholder_frames(
        self,
        frame_width:  int,
        frame_height: int,
        frame_count:  int,
    ) -> list:
        """Return a list of coloured placeholder frames for a missing sprite sheet.

        Each frame is just a purple rectangle so we can see the animation is running.
        """
        frames = []
        for _ in range(frame_count):
            surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            surface.fill(FALLBACK_PORTAL_COLOR)   # purple — easy to spot!
            pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=2)
            frames.append(surface)
        return frames

    # ------------------------------------------------------------------
    # update — call this once per game tick (60 times per second)
    # ------------------------------------------------------------------
    def update(self):
        """Advance the portal and water animations one step.

        Every PORTAL_FRAME_SPEED ticks we move to the next frame.
        When we reach the last frame we loop back to the first.
        """
        self.frame_tick += 1

        if self.frame_tick >= PORTAL_FRAME_SPEED:
            self.frame_tick = 0  # reset the tick counter

            # Advance portal gate to the next frame, looping back to 0 at the end
            self.portal_frame_index = (self.portal_frame_index + 1) % len(self.portal_frames)

            # Advance water to the next frame at the same speed
            self.water_frame_index = (self.water_frame_index + 1) % len(self.water_frames)

    # ------------------------------------------------------------------
    # draw — call this every frame inside the game loop
    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        """Draw every tile in MAP_GRID onto the screen.

        We go row by row, column by column.
        (0, 0) is the top-left corner of the screen — the Pygame way!

        After all tiles are drawn we put the portal gate on top.
        """
        # Get the current water frame to show this tick
        current_water = self.water_frames[self.water_frame_index]

        for row_index in range(MAP_ROWS):
            for col_index in range(MAP_COLS):
                # Figure out the pixel position of this tile's top-left corner
                pixel_x = col_index * TILE_SIZE
                pixel_y = row_index * TILE_SIZE

                # Find out what kind of tile this cell is
                tile_type = MAP_GRID[row_index][col_index]

                if tile_type == TILE_WATER:
                    # Water is animated — use the current animation frame
                    screen.blit(current_water, (pixel_x, pixel_y))
                else:
                    # All other tiles are static images stored in tile_images
                    tile_image = self.tile_images.get(tile_type)
                    if tile_image is not None:
                        screen.blit(tile_image, (pixel_x, pixel_y))
                    else:
                        # Unknown tile type?  Draw an obvious red square so we notice!
                        pygame.draw.rect(
                            screen,
                            (255, 0, 0),
                            pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE),
                        )

        # --- Draw the portal gate on top of all tiles ---
        # The portal is 96×128 pixels and sits at a fixed spot in the world
        current_portal = self.portal_frames[self.portal_frame_index]
        screen.blit(current_portal, (PORTAL_X, PORTAL_Y))

    # ------------------------------------------------------------------
    # get_solid_tiles — useful for collision checking
    # ------------------------------------------------------------------
    def get_solid_tiles(self) -> list:
        """Return a list of pygame.Rect for every TILE_WALL cell on the map.

        Other files (like player.py and enemies.py) can use this list to check
        whether a character is about to walk into a wall.

        A pygame.Rect stores a rectangle: its x, y position and its width and height.
        """
        wall_rects = []

        for row_index in range(MAP_ROWS):
            for col_index in range(MAP_COLS):
                if MAP_GRID[row_index][col_index] == TILE_WALL:
                    rect = pygame.Rect(
                        col_index * TILE_SIZE,   # left edge in pixels
                        row_index * TILE_SIZE,   # top edge in pixels
                        TILE_SIZE,               # width
                        TILE_SIZE,               # height
                    )
                    wall_rects.append(rect)

        return wall_rects
