# game/enemies.py
# ============================================================
# All the enemy characters for The Ancient Wizard's Star!
#
# Enemies wander the world, chase the player when close,
# and attack on contact. They respawn after being defeated
# so there's always something to fight.
#
# Written to be easy to read — even for an 8-year-old! :)
# ============================================================

import math
import random
from pathlib import Path

import pygame


# ------------------------------------------------------------
# CONSTANTS — numbers that control how enemies behave.
# Change these to make the game easier or harder!
# ------------------------------------------------------------

CHASE_RANGE = 200        # Pixels — enemy starts chasing when the player is closer than this
ATTACK_RANGE = 40        # Pixels — enemy deals damage when this close to the player
ENEMY_ATTACK_DAMAGE = 1  # How much health the player loses from one enemy hit
ATTACK_COOLDOWN = 90     # Frames between enemy attacks (90 frames = 1.5 seconds at 60 FPS)
WANDER_CHANGE_TICKS = 150  # How often (in frames) an enemy picks a new wander direction
RESPAWN_TICKS = 600      # Frames before a dead enemy respawns at its start point (10 seconds)

# Chance that a defeated enemy drops a magical shard.
# 0.60 = 60% chance. random.random() gives a number between 0.0 and 1.0,
# so "< SHARD_DROP_CHANCE" is True 60% of the time.
SHARD_DROP_CHANCE = 0.60

# Enemy states — tracks what the enemy is doing right now
STATE_WANDER = "wander"  # Slowly walking around
STATE_CHASE  = "chase"   # Running toward the player!
STATE_DEAD   = "dead"    # Waiting to respawn

OUTLINE_COLOR = (26, 26, 26)  # Very dark grey used for health bar outlines
ASSET_ROOT = Path("assets")   # All enemy sprite PNGs live inside the assets/ folder


# ------------------------------------------------------------
# SPRITE LOADER — loads a PNG image, or makes a placeholder
# ------------------------------------------------------------

def _load_sprite(filename, width, height, fallback_color):
    """Try to load a PNG from assets/. If it's missing, return a colored placeholder square instead.

    This means the game still works even if the art isn't ready yet!
    The placeholder is a solid colored rectangle with a dark outline,
    so you can still see the enemy moving around on screen.

    Args:
        filename      -- the PNG filename, e.g. "enemy_evil_ninja.png"
        width         -- how many pixels wide the sprite should be
        height        -- how many pixels tall the sprite should be
        fallback_color -- an (R, G, B) color tuple used for the placeholder
    """
    path = ASSET_ROOT / filename
    try:
        # Try to load the real PNG artwork from disk
        img = pygame.image.load(str(path)).convert_alpha()
        # If the image isn't already the right size, scale it to fit
        if img.get_size() != (width, height):
            img = pygame.transform.scale(img, (width, height))
        return img
    except Exception:
        # Art file not found — make a colored placeholder square so the game still runs
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(fallback_color)
        # Draw a dark outline so the placeholder is easy to see
        pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=2)
        return surface


# ------------------------------------------------------------
# ENEMY BASE CLASS — the blueprint every enemy type uses
# ------------------------------------------------------------

class Enemy:
    """The base class for all enemies. Every enemy type builds on this.

    An Enemy knows how to:
    - Wander slowly around the world
    - Notice when the player gets close and start chasing
    - Attack the player when touching them
    - Take damage and die
    - Respawn after 10 seconds back at its starting spot
    """

    def __init__(self, spawn_x, spawn_y, health, speed, sprite_width, sprite_height, sprite):
        """Set up a brand new enemy at its starting position.

        Args:
            spawn_x       -- starting X position on screen (pixels from left)
            spawn_y       -- starting Y position on screen (pixels from top)
            health        -- how many hits this enemy can take before dying
            speed         -- how fast it moves when chasing (pixels per frame)
            sprite_width  -- width of the enemy image in pixels
            sprite_height -- height of the enemy image in pixels
            sprite        -- a pygame.Surface containing the enemy's picture
        """
        # Current position on screen
        self.x = spawn_x
        self.y = spawn_y

        # Remember where this enemy started — we need this for respawning!
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

        # Health stats
        self.health = health
        self.max_health = health  # Save the full health so we can restore it on respawn

        # Movement
        self.speed = speed        # How fast the enemy moves when chasing the player

        # Sprite (the picture drawn on screen)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprite = sprite      # A single pygame.Surface (one image, no animation yet)

        # State machine — what is this enemy doing right now?
        self.state = STATE_WANDER

        # Attack cooldown — prevents the enemy from dealing damage every single frame
        self.attack_cooldown_ticks = 0

        # Wander timer — counts frames so we can pick a new wander direction periodically
        self.wander_ticks = 0

        # Current wander direction (changes every WANDER_CHANGE_TICKS frames)
        self.wander_dx = 1   # Horizontal: +1 = right, -1 = left, 0 = standing still
        self.wander_dy = 0   # Vertical:   +1 = down,  -1 = up,   0 = standing still

        # Respawn timer — counts frames while the enemy is dead
        self.respawn_ticks = 0

        # Signal flag: True for exactly one frame when this enemy dies.
        # main.py reads this flag to know it should spawn a magical shard at our position!
        self.just_died = False

    # ----------------------------------------------------------
    # HELPER METHODS
    # ----------------------------------------------------------

    def get_center(self):
        """Return the (x, y) pixel position of the enemy's center point.

        Useful for distance calculations and drawing effects.
        """
        center_x = self.x + self.sprite_width // 2
        center_y = self.y + self.sprite_height // 2
        return (center_x, center_y)

    def _distance_to_player(self, player):
        """Calculate how many pixels away the player is from this enemy.

        Uses the Pythagorean theorem: distance = sqrt(dx*dx + dy*dy).
        We measure from center to center so big and small enemies feel the same.
        """
        enemy_cx, enemy_cy = self.get_center()

        # Player sprite is always 48x48 px (see asset_manifest.py), so center is at +24
        player_cx = player.x + 24
        player_cy = player.y + 24

        dx = player_cx - enemy_cx
        dy = player_cy - enemy_cy
        return math.sqrt(dx * dx + dy * dy)

    # ----------------------------------------------------------
    # UPDATE — called every frame by main.py
    # ----------------------------------------------------------

    def update(self, player):
        """Update the enemy each frame — move, decide what to do, attack if close enough.

        This is the main brain of the enemy. It runs 60 times per second!

        Args:
            player -- the Player object (so we can measure distance and deal damage)
        """

        # Reset the just_died flag every frame — it should only be True for ONE frame.
        # WHY here at the very top? Because if we put it after the STATE_DEAD check,
        # the early return would skip it, and just_died would stay True for all 600
        # frames of the respawn period — spawning 600 shards instead of 1!
        self.just_died = False

        # --- Dead state: count down to respawn, then come back to life ---
        if self.state == STATE_DEAD:
            self.respawn_ticks += 1
            if self.respawn_ticks >= RESPAWN_TICKS:
                self._respawn()
            return  # Dead enemies don't move or attack — stop here

        dist = self._distance_to_player(player)

        # --- Decide whether to wander or chase ---
        # Start chasing when the player enters our CHASE_RANGE
        if self.state == STATE_WANDER and dist < CHASE_RANGE:
            self.state = STATE_CHASE

        # Give up the chase when the player gets far enough away (x1.3 gives a little leeway
        # so the enemy doesn't switch back and forth rapidly at the edge of range)
        elif self.state == STATE_CHASE and dist > CHASE_RANGE * 1.3:
            self.state = STATE_WANDER

        # --- Move based on current state ---
        if self.state == STATE_WANDER:
            self._do_wander()
        elif self.state == STATE_CHASE:
            self._move_toward_player(player)

        # --- Attack the player if they're very close (and cooldown allows it) ---
        if dist < ATTACK_RANGE and self.attack_cooldown_ticks <= 0:
            player.take_damage(ENEMY_ATTACK_DAMAGE)
            # Start the cooldown timer so we can't hit again immediately
            self.attack_cooldown_ticks = ATTACK_COOLDOWN

        # Count down the attack cooldown each frame
        if self.attack_cooldown_ticks > 0:
            self.attack_cooldown_ticks -= 1

    # ----------------------------------------------------------
    # MOVEMENT METHODS
    # ----------------------------------------------------------

    def _do_wander(self):
        """Pick a random direction and slowly wander around the map.

        Every WANDER_CHANGE_TICKS frames, pick a new direction to walk.
        Sometimes the enemy just stands still — that looks natural!
        Wandering is always slow (1 pixel per frame) so enemies don't zoom
        across the screen when the player isn't nearby.
        """
        self.wander_ticks += 1

        # Time to pick a new direction?
        if self.wander_ticks >= WANDER_CHANGE_TICKS:
            # Possible directions: right, left, down, up, or standing still
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
            self.wander_dx, self.wander_dy = random.choice(directions)
            self.wander_ticks = 0  # Reset the timer

        # Move 1 pixel in the chosen direction (slow wandering speed)
        self.x += self.wander_dx * 1
        self.y += self.wander_dy * 1

        # Keep the enemy inside the screen boundaries.
        # 1280 and 720 match SCREEN_WIDTH and SCREEN_HEIGHT defined in main.py.
        self.x = max(0, min(self.x, 1280 - self.sprite_width))
        self.y = max(0, min(self.y, 720 - self.sprite_height))

    def _move_toward_player(self, player):
        """Chase the player! Move directly toward them at this enemy's speed.

        We figure out which direction the player is, turn that into a unit vector
        (a direction with length exactly 1), then multiply by speed to get the
        correct number of pixels to move this frame.
        """
        enemy_cx, enemy_cy = self.get_center()

        # Player center (player sprite is always 48x48 px)
        player_cx = player.x + 24
        player_cy = player.y + 24

        dx = player_cx - enemy_cx
        dy = player_cy - enemy_cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            return  # Already on top of the player — skip so we don't divide by zero

        # Normalize: divide by distance to get a direction with length 1
        direction_x = dx / dist
        direction_y = dy / dist

        # Move at this enemy's chase speed (pixels per frame)
        self.x += int(direction_x * self.speed)
        self.y += int(direction_y * self.speed)

    # ----------------------------------------------------------
    # HEALTH & DEATH
    # ----------------------------------------------------------

    def take_damage(self, amount):
        """The enemy gets hit! Reduce health and check if it has died.

        Args:
            amount -- how many health points to remove
        """
        # health can't go below 0
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self._die()

    def _die(self):
        """The enemy has been defeated! Switch to the dead state and maybe signal a shard drop.

        There's a 60% chance (SHARD_DROP_CHANCE) that a defeated enemy drops a shard.
        just_died = True signals main.py to create a shard at this position.
        just_died = False means no shard this time — the enemy was defeated but dropped nothing.
        """
        self.state = STATE_DEAD
        self.respawn_ticks = 0
        # random.random() gives a random number between 0.0 and 1.0 each time.
        # If it's less than 0.60, we drop a shard — so 60% of the time we do!
        self.just_died = random.random() < SHARD_DROP_CHANCE

    def _respawn(self):
        """Bring the enemy back to life at its original starting position.

        Full health, wandering state — like it was just placed on the map.
        """
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.health = self.max_health
        self.state = STATE_WANDER
        self.wander_ticks = 0
        self.respawn_ticks = 0

    def is_dead(self):
        """Return True if this enemy is currently in the dead state."""
        return self.state == STATE_DEAD

    # ----------------------------------------------------------
    # DRAWING
    # ----------------------------------------------------------

    def draw(self, screen):
        """Draw the enemy sprite and a small health bar above it.

        Dead enemies are invisible — we skip drawing them entirely.

        Args:
            screen -- the pygame display surface to draw onto
        """
        if self.state == STATE_DEAD:
            return  # Nothing to draw while dead

        # Draw the enemy sprite at its current position
        screen.blit(self.sprite, (self.x, self.y))

        # --- Health bar ---
        # Draw a small horizontal bar 8 pixels above the enemy's top edge.
        # The bar is as wide as the enemy sprite and 5 pixels tall.
        bar_x = self.x
        bar_y = self.y - 8       # 8 px above the top of the sprite
        bar_width = self.sprite_width
        bar_height = 5

        # Dark red background — represents the health that's already been lost
        pygame.draw.rect(screen, (120, 20, 20), (bar_x, bar_y, bar_width, bar_height))

        # Bright red fill — shrinks as health drops
        health_fraction = self.health / self.max_health  # 1.0 = full health, 0.0 = dead
        fill_width = int(bar_width * health_fraction)
        if fill_width > 0:
            pygame.draw.rect(screen, (220, 50, 50), (bar_x, bar_y, fill_width, bar_height))

        # Thin dark outline around the whole health bar
        pygame.draw.rect(screen, OUTLINE_COLOR, (bar_x, bar_y, bar_width, bar_height), width=1)


# ------------------------------------------------------------
# ENEMY SUBCLASSES — specific enemy types
# ------------------------------------------------------------

class EvilNinja(Enemy):
    """A fast, sneaky enemy. Low health but moves quickly!

    The EvilNinja is the most common enemy in the world.
    It doesn't take many hits to beat, but it runs fast — watch out!

    Sprite file: assets/enemy_evil_ninja.png  (44 x 44 px)
    Fallback color: dark purple if the PNG is missing
    """

    def __init__(self, spawn_x, spawn_y):
        """Create an EvilNinja at the given position."""
        # Load the sprite (or a dark-purple placeholder if the art isn't ready yet)
        sprite = _load_sprite("enemy_evil_ninja.png", 44, 44, (60, 0, 80))
        super().__init__(
            spawn_x, spawn_y,
            health=3,           # Only 3 hits to defeat — nice and easy!
            speed=2,            # Speed 2 = moves 2 pixels per frame when chasing
            sprite_width=44,
            sprite_height=44,
            sprite=sprite,
        )


class Skeleton(Enemy):
    """A creepy skeleton enemy. Slower than the ninja, but a bit tougher.

    Skeletons shamble toward you at a slow pace. They won't catch you
    easily, but they can take more hits than the ninjas.

    Sprite file: assets/enemy_skeleton.png  (44 x 48 px)
    Fallback color: pale bone-white if the PNG is missing
    """

    def __init__(self, spawn_x, spawn_y):
        """Create a Skeleton at the given position."""
        # Load the sprite (or a pale bone-white placeholder)
        sprite = _load_sprite("enemy_skeleton.png", 44, 48, (200, 190, 170))
        super().__init__(
            spawn_x, spawn_y,
            health=4,           # 4 hits to defeat
            speed=1,            # Slow — only 1 pixel per frame when chasing
            sprite_width=44,
            sprite_height=48,
            sprite=sprite,
        )


class Zombie(Enemy):
    """The toughest basic enemy — slow and shambling, but takes many hits to defeat!

    Zombies are the hardest regular enemy in the world. They move just
    as slowly as skeletons, but you'll need to hit them more times to beat them.
    Don't let them surround you!

    Sprite file: assets/enemy_zombie.png  (44 x 48 px)
    Fallback color: sickly green if the PNG is missing
    """

    def __init__(self, spawn_x, spawn_y):
        """Create a Zombie at the given position."""
        # Load the sprite (or a sickly-green placeholder)
        sprite = _load_sprite("enemy_zombie.png", 44, 48, (80, 120, 60))
        super().__init__(
            spawn_x, spawn_y,
            health=5,           # 5 hits to defeat — the toughest basic enemy!
            speed=1,            # Slow — only 1 pixel per frame when chasing
            sprite_width=44,
            sprite_height=48,
            sprite=sprite,
        )


# ------------------------------------------------------------
# MINI-BOSS BASE CLASS — tougher enemies that don't respawn!
# ------------------------------------------------------------

class MiniBoss(Enemy):
    """The base class for mini-boss enemies.

    Mini-bosses are much tougher than regular enemies and they do NOT respawn
    once defeated. You only have to beat them once — then they're gone for good!

    Luca, mini-bosses are the big challenge enemies before the final boss!
    """

    def __init__(self, spawn_x, spawn_y, health, speed, sprite_width, sprite_height, sprite):
        """Set up a mini-boss — same as a regular enemy, but permanent."""
        super().__init__(spawn_x, spawn_y, health, speed, sprite_width, sprite_height, sprite)

    def _respawn(self):
        """Mini-bosses NEVER come back after being defeated — this does nothing on purpose!"""
        pass   # Override the parent's respawn so they stay dead forever

    def is_permanently_dead(self):
        """Return True if this mini-boss has been beaten and won't come back."""
        return self.state == STATE_DEAD


class Grimrak(MiniBoss):
    """Grimrak the Stone Golem — the FIRST mini-boss!

    He's big, slow, and very tough. You'll need many hits to defeat him.
    Spawns when you collect 25 magical shards!

    Sprite file: assets/enemy_grimrak.png — 80 x 80 px
    Fallback color: dark grey (like a stone golem!)
    """

    def __init__(self, spawn_x, spawn_y):
        """Create Grimrak at the given position."""
        sprite = _load_sprite("enemy_grimrak.png", 80, 80, (80, 80, 80))
        super().__init__(
            spawn_x, spawn_y,
            health=20,          # Very tough — needs LOTS of hits!
            speed=1,            # Slow and heavy like a boulder
            sprite_width=80,
            sprite_height=80,
            sprite=sprite,
        )


class Zara(MiniBoss):
    """Zara the Storm Witch — the SECOND mini-boss!

    She's faster than Grimrak but has less health. The story says she switches
    sides when defeated and joins your team — but that feature is coming later!
    Spawns when you collect 50 magical shards total!

    Sprite file: assets/enemy_zara.png — 64 x 64 px
    Fallback color: electric purple (she controls lightning!)
    """

    def __init__(self, spawn_x, spawn_y):
        """Create Zara at the given position."""
        sprite = _load_sprite("enemy_zara.png", 64, 64, (130, 0, 200))
        super().__init__(
            spawn_x, spawn_y,
            health=15,          # Tough, but not as tough as Grimrak
            speed=2,            # Faster than the golem — she floats!
            sprite_width=64,
            sprite_height=64,
            sprite=sprite,
        )


# ------------------------------------------------------------
# FACTORY FUNCTION — build the enemy list for the whole world
# ------------------------------------------------------------

def create_enemy_group():
    """Create all the enemies that will appear in the world at game start.

    Returns a list of Enemy objects, each placed at its starting position
    on the map. main.py calls this once when the game loads.

    Enemy types are rotated so we get a nice mix of ninjas, skeletons,
    and zombies spread around the map.
    """

    # Starting positions for each enemy — (x, y) in pixels from top-left of screen.
    # Spread out so enemies aren't all clumped in one spot at the start.
    spawn_points = [
        (160, 200),   # Top-left area
        (320, 480),   # Left side, lower
        (500, 150),   # Top-center area
        (700, 400),   # Center of screen
        (250, 530),   # Bottom-left area
        (850, 180),   # Right side, upper
        (600, 560),   # Bottom-center area
        (400, 300),   # Center-left area
    ]

    # Which enemy type to use at each spawn point — cycles through the three types
    enemy_types = [
        EvilNinja, Skeleton, Zombie,
        EvilNinja, Skeleton, Zombie,
        EvilNinja, Skeleton,
    ]

    # Build the list — pair each enemy class with its spawn point
    enemies = []
    for enemy_class, (spawn_x, spawn_y) in zip(enemy_types, spawn_points):
        enemies.append(enemy_class(spawn_x, spawn_y))

    return enemies
