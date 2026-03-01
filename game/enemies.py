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
ATTACK_RANGE = 40        # Pixels — regular enemy deals damage when this close to the player
ENEMY_ATTACK_DAMAGE = 1  # How much health the player loses from one regular enemy hit
ATTACK_COOLDOWN = 90     # Frames between enemy attacks (90 frames = 1.5 seconds at 60 FPS)

# Mini-bosses are bigger sprites, so they need a wider attack range.
# They also hit harder — fighting a boss should feel dangerous!
BOSS_ATTACK_DAMAGE = 3   # 3× a regular enemy — bosses are no joke!
BOSS_ATTACK_RANGE  = 60  # Wider reach (Grimrak is 80 px wide, Zara is 64 px wide)

# Animation timing for enemy sprite sheets.
# These numbers control how quickly frames advance in each state.
ENEMY_ANIM_IDLE_SPEED   = 14   # frames between animation frame advances while wandering
ENEMY_ANIM_WALK_SPEED   =  8   # frames between advances while chasing
ENEMY_ANIM_ATTACK_SPEED =  5   # frames between advances during attack animation
ENEMY_ATTACK_ANIM_TICKS = 12   # how many frames to hold the attack animation
WANDER_CHANGE_TICKS = 150  # How often (in frames) an enemy picks a new wander direction
RESPAWN_TICKS = 600      # Frames before a dead enemy respawns at its start point (10 seconds)

# Chance that a defeated enemy drops a magical shard.
# 0.60 = 60% chance. random.random() gives a number between 0.0 and 1.0,
# so "< SHARD_DROP_CHANCE" is True 60% of the time.
SHARD_DROP_CHANCE = 0.60

# Chance that a defeated enemy drops a small health potion.
# 0.25 = 25% chance — less common than shards (60%)
HEALTH_POTION_DROP_CHANCE = 0.25

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


def _load_enemy_animations(base_name, w, h, fallback_sprite):
    """Try to load walk and attack sprite sheets for an enemy.

    Looks for:
      assets/BASE_walk.png   — horizontal strip, 4 frames of w×h px
      assets/BASE_attack.png — horizontal strip, 4 frames of w×h px

    If either file is missing, falls back to a 1-frame list containing
    the existing fallback_sprite so the game still works without art.

    Returns: {"idle": [sprite], "walk": [...], "attack": [...]}
    """
    animations = {
        "idle": [fallback_sprite],
        "walk": [fallback_sprite],
        "attack": [fallback_sprite],
    }

    def _load_sheet_frames(filename):
        path = ASSET_ROOT / filename
        try:
            sheet = pygame.image.load(str(path)).convert_alpha()
            frames = []
            for i in range(4):
                frame_rect = pygame.Rect(i * w, 0, w, h)
                frame = sheet.subsurface(frame_rect).copy()
                frames.append(frame)
            return frames
        except Exception:
            return [fallback_sprite]

    animations["walk"] = _load_sheet_frames(f"{base_name}_walk.png")
    animations["attack"] = _load_sheet_frames(f"{base_name}_attack.png")
    return animations


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
                                  # Also used by the Assassin's special damage formula!

        # Movement
        self.speed = speed        # How fast the enemy moves when chasing the player

        # Sprite (the picture drawn on screen)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprite = sprite      # A single pygame.Surface (one image, no animation yet)

        # Animation state machine:
        # idle   = wandering
        # walk   = chasing
        # attack = playing the attack swing/strike animation
        self.animations        = {}      # filled by subclass; empty = use static self.sprite
        self.anim_state        = "idle"  # "idle", "walk", or "attack"
        self.anim_frame        = 0       # current frame index into animations[anim_state]
        self.anim_tick         = 0       # counts up; advance frame when it hits the speed threshold
        self.attack_anim_ticks = 0       # counts down after an attack so we hold the attack pose

        # State machine — what is this enemy doing right now?
        self.state = STATE_WANDER

        # Attack stats — stored on the instance so subclasses (MiniBoss) can override them
        self.attack_damage = ENEMY_ATTACK_DAMAGE  # HP the player loses per hit
        self.attack_range  = ATTACK_RANGE         # Distance in pixels to start attacking

        # Signal flag: True for exactly ONE frame when this enemy lands a hit on the player.
        # main.py reads this to play a sound and show a red flash at the player's position.
        self.just_attacked = False

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

        # Potion drop flag: True for exactly one frame when a defeated enemy drops a potion.
        # main.py reads this to know it should spawn a small health potion at our position!
        self.potion_drop = False

        # Hit-this-swing flag: prevents the same enemy from being hit more than once
        # during a single melee swing. main.py sets this to True when it hits us,
        # and we reset it to False at the start of every update() frame.
        self._already_hit_this_swing = False

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

        # Reset the one-frame signal flags at the very top of update().
        # WHY here? Because if we put it after the STATE_DEAD check, the early
        # return would skip it, and just_died would stay True for all 600 frames
        # of the respawn period — spawning 600 shards instead of 1!
        self.just_died     = False
        self.potion_drop   = False
        self.just_attacked = False   # Reset before we decide whether to attack this frame

        # Reset the swing flag each frame so we can be hit again next frame.
        # This stops an attack zone from hitting us 60 times per second, but
        # does allow us to be hit again on the player's NEXT swing.
        self._already_hit_this_swing = False

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

        # If we are not currently holding an attack animation, match animation to movement state.
        if self.attack_anim_ticks <= 0:
            if self.state == STATE_WANDER:
                self._set_anim_state("idle")
            elif self.state == STATE_CHASE:
                self._set_anim_state("walk")

        # --- Attack the player if they're very close (and cooldown allows it) ---
        if dist < self.attack_range and self.attack_cooldown_ticks <= 0:
            player.take_damage(self.attack_damage)
            self.just_attacked = True            # Signal main.py: show a red flash + play sound!
            # Start the cooldown timer so we can't hit again immediately
            self.attack_cooldown_ticks = ATTACK_COOLDOWN
            # Start the attack animation and hold it briefly.
            self._set_anim_state("attack")
            self.attack_anim_ticks = ENEMY_ATTACK_ANIM_TICKS

        # Count down attack animation hold timer.
        if self.attack_anim_ticks > 0:
            self.attack_anim_ticks -= 1
            if self.attack_anim_ticks <= 0:
                if self.state == STATE_CHASE:
                    self._set_anim_state("walk")
                else:
                    self._set_anim_state("idle")

        # Count down the attack cooldown each frame
        if self.attack_cooldown_ticks > 0:
            self.attack_cooldown_ticks -= 1

        # Step the animation forward at the speed for the current state.
        self._advance_animation()

    def _set_anim_state(self, new_state):
        """Switch animation state and safely reset frame counters when state changes."""
        if self.anim_state != new_state:
            self.anim_state = new_state
            self.anim_frame = 0
            self.anim_tick = 0

    def _advance_animation(self):
        """Step the animation forward by one frame if enough ticks have passed."""
        speed_map = {
            "idle":   ENEMY_ANIM_IDLE_SPEED,
            "walk":   ENEMY_ANIM_WALK_SPEED,
            "attack": ENEMY_ANIM_ATTACK_SPEED,
        }
        speed = speed_map.get(self.anim_state, ENEMY_ANIM_WALK_SPEED)
        self.anim_tick += 1
        if self.anim_tick >= speed:
            self.anim_tick = 0
            frames = self.animations.get(self.anim_state, [])
            if frames:
                self.anim_frame = (self.anim_frame + 1) % len(frames)

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
        """The enemy has been defeated! Switch to the dead state and maybe signal drops.

        There's a 60% chance (SHARD_DROP_CHANCE) that a defeated enemy drops a shard.
        There's also a 25% chance (HEALTH_POTION_DROP_CHANCE) of a small health potion drop.
        just_died = True signals main.py to create a shard at this position.
        potion_drop = True signals main.py to create a small health potion here.
        """
        self.state = STATE_DEAD
        self.respawn_ticks = 0
        # random.random() gives a random number between 0.0 and 1.0 each time.
        # If it's less than 0.60, we drop a shard — so 60% of the time we do!
        self.just_died = random.random() < SHARD_DROP_CHANCE
        # 25% chance to also drop a small health potion — nice bonus for the player!
        self.potion_drop = random.random() < HEALTH_POTION_DROP_CHANCE

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

        # Pick the correct animation frame for the current state.
        # If no animations are loaded, fall back to the static sprite.
        frames = self.animations.get(self.anim_state, [])
        frame  = frames[self.anim_frame] if frames else self.sprite
        screen.blit(frame, (self.x, self.y))

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
        self.animations = _load_enemy_animations("enemy_evil_ninja", 44, 44, sprite)


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
        self.animations = _load_enemy_animations("enemy_skeleton", 44, 48, sprite)


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
        self.animations = _load_enemy_animations("enemy_zombie", 44, 48, sprite)


class EnemyProjectile:
    """A projectile fired by an enemy toward the player.

    Travels in a straight line until it hits the player or goes too far.
    Drawn as a filled circle (no sprite required — keeps it simple!).
    """

    def __init__(self, x, y, target_x, target_y, speed, damage, color, max_travel=500):
        self.x          = x
        self.y          = y
        self.damage     = damage
        self.color      = color      # (R, G, B)
        self.radius     = 8
        self.alive      = True
        self.traveled   = 0
        self.max_travel = max_travel

        # Unit vector pointing from the firing position toward the target
        dx   = target_x - x
        dy   = target_y - y
        dist = math.sqrt(dx * dx + dy * dy) or 1
        self.dx = dx / dist * speed
        self.dy = dy / dist * speed

    def update(self):
        self.x        += self.dx
        self.y        += self.dy
        self.traveled += math.sqrt(self.dx ** 2 + self.dy ** 2)
        if self.traveled >= self.max_travel:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


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
        """Set up a mini-boss — same as a regular enemy, but bigger, tougher, and permanent."""
        super().__init__(spawn_x, spawn_y, health, speed, sprite_width, sprite_height, sprite)

        # Bosses hit much harder and have a wider reach than regular enemies!
        # We override the instance variables set in Enemy.__init__ so the base attack
        # logic in Enemy.update() automatically uses these stronger values.
        self.attack_damage = BOSS_ATTACK_DAMAGE   # 3 HP per hit (vs 1 for regular enemies)
        self.attack_range  = BOSS_ATTACK_RANGE    # 60 px reach (vs 40 — big sprites need more)

        # Boss-specific potion drop flag: True for one frame when a mini-boss is defeated.
        # Mini-bosses drop a BIG golden potion — a full heal for the player!
        self.boss_potion_drop = False

    def update(self, player):
        """Update the mini-boss each frame — same as a regular enemy, but also resets boss_potion_drop."""
        # Reset the boss potion drop flag each frame, same as just_died and potion_drop.
        # It should only be True for the one frame when the boss dies!
        self.boss_potion_drop = False
        # Let the parent Enemy class handle all the regular update logic
        super().update(player)

    def _respawn(self):
        """Mini-bosses NEVER come back after being defeated — this does nothing on purpose!"""
        pass   # Override the parent's respawn so they stay dead forever

    def _die(self):
        """Mini-bosses always drop a BIG health potion when defeated — you earned it!

        They also drop a shard and they never respawn. Beating a mini-boss
        is a huge moment, so we make sure the reward feels great!
        """
        self.state = STATE_DEAD
        self.respawn_ticks = 0
        self.just_died = True           # Always drop a shard too
        self.boss_potion_drop = True    # The big reward: a full-heal potion!
        self.potion_drop = False        # Skip the small potion (they get the big one)

    def is_permanently_dead(self):
        """Return True if this mini-boss has been beaten and won't come back."""
        return self.state == STATE_DEAD


class Grimrak(MiniBoss):
    """Grimrak the Stone Golem — the FIRST mini-boss!

    He's big, slow, and very tough. You'll need many hits to defeat him.
    Spawns when you collect 25 magical shards!

    Sprite file: assets/boss_grimrak.png — 80 x 80 px
    Fallback color: dark grey (like a stone golem!)
    """

    def __init__(self, spawn_x, spawn_y):
        """Create Grimrak at the given position."""
        sprite = _load_sprite("boss_grimrak.png", 80, 80, (80, 80, 80))
        super().__init__(
            spawn_x, spawn_y,
            health=20,          # Very tough — needs LOTS of hits!
            speed=1,            # Slow and heavy like a boulder
            sprite_width=80,
            sprite_height=80,
            sprite=sprite,
        )
        self.animations = _load_enemy_animations("boss_grimrak", 80, 80, sprite)

        # Ground slam special attack:
        # cooldown counts down while chasing, then we activate a short slam window.
        self.slam_cooldown = 300   # 5 seconds at 60 FPS; counts down to 0 then slams
        self.slam_active   = 0     # counts down from 20 when a slam is happening (0.33 s)

    def update(self, player):
        """Update Grimrak and run his ground-slam timer logic."""
        super().update(player)

        if self.state == STATE_DEAD:
            return

        if self.state == STATE_CHASE:
            self.slam_cooldown -= 1
            if self.slam_cooldown <= 0:
                self.slam_cooldown = 300
                self.slam_active   = 20

        if self.slam_active > 0:
            self.slam_active -= 1


class Zara(MiniBoss):
    """Zara the Storm Witch — the SECOND mini-boss!

    She's faster than Grimrak but has less health. The story says she switches
    sides when defeated and joins your team — but that feature is coming later!
    Spawns when you collect 50 magical shards total!

    Sprite file: assets/boss_zara.png — 64 x 64 px
    Fallback color: electric purple (she controls lightning!)
    """

    def __init__(self, spawn_x, spawn_y):
        """Create Zara at the given position."""
        sprite = _load_sprite("boss_zara.png", 64, 64, (130, 0, 200))
        super().__init__(
            spawn_x, spawn_y,
            health=15,          # Tough, but not as tough as Grimrak
            speed=2,            # Faster than the golem — she floats!
            sprite_width=64,
            sprite_height=64,
            sprite=sprite,
        )
        self.animations = _load_enemy_animations("boss_zara", 64, 64, sprite)

        # Zara's ranged magic bolt ability.
        self.bolt_cooldown       = 180   # 3 seconds; counts down to 0 then fires
        self.pending_projectiles = []    # handed off to main.py each frame

    def update(self, player):
        """Update Zara and fire a purple bolt every few seconds while chasing."""
        super().update(player)

        self.pending_projectiles = []   # reset each frame
        if self.state == STATE_DEAD:
            return

        if self.state == STATE_CHASE:
            self.bolt_cooldown -= 1
            if self.bolt_cooldown <= 0:
                self.bolt_cooldown = 180
                cx, cy = self.get_center()
                px, py = player.x + 24, player.y + 24
                self.pending_projectiles.append(
                    EnemyProjectile(cx, cy, px, py,
                                    speed=6, damage=2, color=(180, 0, 255))
                )


# ------------------------------------------------------------
# FINAL BOSS — Voltrak the Shockblade Eel!
# ------------------------------------------------------------

class Voltrak(MiniBoss):
    """Voltrak the Shockblade Eel — the FINAL BOSS of The Ancient Wizard's Star!

    He is a ninja-style land-eel who fights with an electric sword.
    He chases the player and fires electric shock bolts in all 4 directions.

    Two phases:
    - Phase 1 (full health to 50%): speed 2, shocks every 2 seconds
    - Phase 2 (below 50% health):   speed 3, shocks every 1.17 seconds — DANGER!

    Beat Grimrak and Zara first, collect the Portal Key, and step through
    the portal gate to start this boss fight!

    Sprite: assets/boss_ninja_land_eel.png (128 x 64 px)
    Fallback color: dark teal — like a deep-water eel
    """

    # How many frames pass between electric shock volleys
    SHOCK_INTERVAL_PHASE1 = 120   # 2.0 seconds (60 FPS) in Phase 1
    SHOCK_INTERVAL_PHASE2 = 70    # 1.17 seconds in Phase 2 — MUCH more dangerous!

    # Electric shock bolt dimensions
    SHOCK_RANGE     = 200   # Pixels the bolt travels from Voltrak's centre
    SHOCK_THICKNESS = 20    # Narrow side of each bolt rectangle

    # How long each shock zone stays on screen (pure visual — damage is checked at fire time)
    SHOCK_DURATION = 18     # 0.3 seconds

    SHOCK_DAMAGE    = 2     # HP lost if the player is standing in a shock zone when it fires
    PHASE2_THRESHOLD = 0.5  # Switch to Phase 2 when health falls below 50%

    def __init__(self, spawn_x, spawn_y):
        """Create Voltrak at the given position."""
        sprite = _load_sprite("boss_ninja_land_eel.png", 128, 64, (20, 100, 80))
        super().__init__(
            spawn_x, spawn_y,
            health=40,          # Very tough — needs a LOT of hits!
            speed=2,            # Fast, like Zara
            sprite_width=128,
            sprite_height=64,
            sprite=sprite,
        )
        self.shock_timer      = 90    # First shock fires after 1.5 seconds — gives the player a moment to react
        self.shock_zones      = []    # List of [rect, timer_remaining] — the visible electric bolts
        self.shock_just_fired = False # True for exactly ONE frame when shocks fire; main.py checks this!

    def update(self, player):
        """Update Voltrak each frame: move, chase, attack, and fire electric shocks."""

        # Reset the one-frame shock signal at the very start
        self.shock_just_fired = False

        # Call MiniBoss → Enemy update: handles wandering, chasing, melee contact, and dying
        super().update(player)

        # If Voltrak is dead, nothing left to do
        if self.state == STATE_DEAD:
            return

        # Phase 2 kicks in at half health — Voltrak gets angrier!
        phase2 = self.health <= self.max_health * self.PHASE2_THRESHOLD
        self.speed = 3 if phase2 else 2
        shock_interval = self.SHOCK_INTERVAL_PHASE2 if phase2 else self.SHOCK_INTERVAL_PHASE1

        # Age existing shock zones — remove any that have expired (timer reaches 0)
        self.shock_zones = [[rect, t - 1] for rect, t in self.shock_zones if t > 1]

        # Count down toward the next shock volley
        self.shock_timer -= 1
        if self.shock_timer <= 0:
            self.shock_timer = shock_interval
            self._fire_shocks()
            self.shock_just_fired = True   # Signal main.py to check collision THIS frame!

    def _fire_shocks(self):
        """Fire electric shock bolts in all 4 cardinal directions.

        Each bolt is a thin rectangle stretching SHOCK_RANGE pixels from
        Voltrak's centre. main.py checks player collision immediately
        after shock_just_fired is set to deal damage.
        """
        # Centre of Voltrak's sprite — bolts shoot outward from here
        cx = self.x + self.sprite_width  // 2
        cy = self.y + self.sprite_height // 2

        r = self.SHOCK_RANGE
        t = self.SHOCK_THICKNESS
        d = self.SHOCK_DURATION

        # Shoot bolts right, left, down, and up — a cross-shaped electric blast!
        self.shock_zones.append([pygame.Rect(cx,        cy - t//2, r, t), d])   # Right
        self.shock_zones.append([pygame.Rect(cx - r,    cy - t//2, r, t), d])   # Left
        self.shock_zones.append([pygame.Rect(cx - t//2, cy,        t, r), d])   # Down
        self.shock_zones.append([pygame.Rect(cx - t//2, cy - r,    t, r), d])   # Up

    def draw_shocks(self, screen):
        """Draw all active shock zones as glowing electric bolts.

        The bolts fade from bright cyan to transparent as their timer counts down.
        A bright white core over a wide cyan glow gives the electric feel!
        """
        if not self.shock_zones:
            return

        # Draw all shock zones onto a single transparent surface,
        # then blit it to screen — this lets us use per-pixel alpha (transparency)!
        shock_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

        for zone_rect, timer_remaining in self.shock_zones:
            fade = timer_remaining / self.SHOCK_DURATION   # 1.0 = fresh, 0.0 = expired

            # Outer glow: wide cyan rectangle, fades out over time
            outer_alpha = int(130 * fade)
            pygame.draw.rect(shock_surf, (80, 200, 255, outer_alpha), zone_rect, border_radius=4)

            # Bright white core: a narrower inset rectangle, stays bright longer
            inset  = 6
            inner  = zone_rect.inflate(-inset * 2, -inset * 2)
            if inner.width > 0 and inner.height > 0:
                inner_alpha = int(220 * fade)
                pygame.draw.rect(shock_surf, (220, 240, 255, inner_alpha), inner, border_radius=2)

        screen.blit(shock_surf, (0, 0))

    def _die(self):
        """Voltrak is defeated — the world of Lumoria is saved!

        We set just_died = True so main.py knows to trigger the victory screen.
        No potion drop needed — winning IS the reward!
        """
        self.state        = STATE_DEAD
        self.respawn_ticks = 0
        self.just_died    = True    # main.py watches this flag to trigger the victory screen!
        self.boss_potion_drop = False   # No big potion — you just WON the game!
        self.potion_drop  = False


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
