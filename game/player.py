"""Player entity and animation runtime.

This file controls everything about the player character:
- Moving around the world (arrow keys or WASD)
- Running (hold Shift) — costs Endurance!
- Attacking (press Space) — also costs Endurance!
- Endurance refills slowly when you rest
- Health, Endurance, Strength, and Magic stats
- Collecting shards and levelling up
- Dying and respawning

Koen, this is the most important file in the game — it's all about YOUR hero!
"""

import pygame

from game.assets import load_player_animations

# ---------------------------------------------------------------------------
# Movement constants — how fast the player moves each frame
# ---------------------------------------------------------------------------
WALK_SPEED = 3   # Pixels the player moves per frame when walking
RUN_SPEED  = 6   # Pixels the player moves per frame when running (hold Shift)

# ---------------------------------------------------------------------------
# Starting stats — all characters start with the same HP
# ---------------------------------------------------------------------------
START_HEALTH = 10

# ---------------------------------------------------------------------------
# Per-class stats — each character class starts with different Strength,
# Magic, and Endurance values to make each class feel unique!
#
# STR = Strength   (used for physical weapons like swords and pickaxes)
# MAG = Magic      (used for magic weapons like staffs and laser beams)
# max_endurance    (how much endurance you start with)
# ---------------------------------------------------------------------------
CLASS_STATS = {
    "Wizard":   {"strength": 1, "magic": 5, "max_endurance": 2},
    "Knight":   {"strength": 5, "magic": 1, "max_endurance": 4},
    "Assassin": {"strength": 3, "magic": 2, "max_endurance": 5},
    "Miner":    {"strength": 4, "magic": 1, "max_endurance": 3},
    "Ninja":    {"strength": 3, "magic": 2, "max_endurance": 5},
    "Robot":    {"strength": 4, "magic": 2, "max_endurance": 3},
}

# ---------------------------------------------------------------------------
# Weapon types — each class has a favourite weapon.
# Magic weapons (staff, laser) use the Magic stat for damage.
# All other weapons use the Strength stat.
# ---------------------------------------------------------------------------
CLASS_WEAPONS = {
    "Wizard":   "staff",     # Magic beam from a wizard staff
    "Knight":   "sword",     # Big heavy sword
    "Assassin": "daggers",   # Twin fast daggers
    "Miner":    "pickaxe",   # A very solid pickaxe
    "Ninja":    "shuriken",  # Throwing stars!
    "Robot":    "laser",     # Zap! Laser beam
}

# Which weapon types use Magic (instead of Strength) for damage calculations
WEAPON_USES_MAGIC = {"staff", "laser"}

# ---------------------------------------------------------------------------
# Sprite size — every character sheet frame is 48 × 48 pixels
# ---------------------------------------------------------------------------
SPRITE_SIZE = 48

# ---------------------------------------------------------------------------
# Attack constants — these control how the Space-bar attack works
#
# ATTACK_COOLDOWN: after attacking, the player must wait this many frames
#   before they can attack again.  30 frames at 60 FPS = 0.5 seconds.
#
# ATTACK_RANGE_PX: the attack hits enemies within this many pixels of the
#   player's center in every direction.
#
# ATTACK_BASE_DAMAGE: the flat damage before adding STR or MAG.
#   Total damage = ATTACK_BASE_DAMAGE + strength (or magic for magic weapons).
# ---------------------------------------------------------------------------
ATTACK_COOLDOWN    = 30   # Frames to wait between attacks (30 = 0.5 s at 60 FPS)
ATTACK_RANGE_PX    = 50   # Pixels from player center — enemies inside this square get hit
ATTACK_BASE_DAMAGE =  1   # Base hit damage before adding the player's stat

# ---------------------------------------------------------------------------
# Endurance constants — controls how the endurance bar is spent and refills
# ---------------------------------------------------------------------------
ENDURANCE_RUN_COST    = 1    # Endurance lost every frame while running
ENDURANCE_ATTACK_COST = 2    # Endurance lost each time the player attacks
ENDURANCE_REGEN_RATE  = 90   # Frames between each +1 endurance refill (90 = 1.5 s)

# ---------------------------------------------------------------------------
# Death & respawn constants
# ---------------------------------------------------------------------------
DEATH_DISPLAY_TICKS = 120   # How many frames to show "You died!" (120 = 2 seconds)

# ---------------------------------------------------------------------------
# How many game frames each animation frame stays on screen before advancing.
# Smaller number = faster animation.
# ---------------------------------------------------------------------------
ANIMATION_SPEEDS = {
    "idle":   12,   # Breathing / standing still — slowest, looks relaxed
    "walk":    6,   # Walking — medium speed
    "run":     4,   # Running — quickest legs
    "attack":  5,   # Attack swing — snappy so it feels powerful
}


class Player(pygame.sprite.Sprite):
    """Represents the hero that the player controls on screen.

    Koen, think of this class like a recipe card for the player character.
    Everything the player can DO or HAS lives here!
    """

    def __init__(self, character_class, screen_width, screen_height):
        """Set up the player at the start of the game.

        character_class -- which hero type was chosen (e.g. "Wizard", "Knight")
        screen_width    -- how wide the game window is, so we can start in the middle
        screen_height   -- how tall the game window is, same reason
        """
        # Always call the parent Sprite setup first — Pygame needs this!
        super().__init__()

        self.character_class = character_class

        # --- Health ---
        # All characters start with the same HP, no matter which class they pick
        self.health     = START_HEALTH
        self.max_health = START_HEALTH

        # --- Class-specific stats (Strength, Magic, Endurance) ---
        # Look up this class's starting numbers from the CLASS_STATS table above
        stats = CLASS_STATS[character_class]
        self.strength       = stats["strength"]
        self.magic          = stats["magic"]
        self.max_endurance  = stats["max_endurance"]
        self.endurance      = self.max_endurance   # Start with full endurance!

        # --- Weapon type ---
        self.weapon_type = CLASS_WEAPONS[character_class]

        # --- Leveling and shard collection ---
        # shards_collected is a running total — it never resets!
        # Every 5 shards = 1 level-up.
        self.shards_collected  = 0
        self.level             = 1
        self.level_up_pending  = False   # True when the player just earned a level-up

        # --- Portal key ---
        self.has_portal_key = False   # Becomes True when the player picks up the portal key

        # --- Position and speed ---
        # Start the player in the center of the screen
        self.x     = screen_width  // 2 - SPRITE_SIZE // 2
        self.y     = screen_height // 2 - SPRITE_SIZE // 2
        self.speed = WALK_SPEED

        # --- Animation state ---
        self.animations          = load_player_animations(character_class)
        self.current_animation   = "idle"
        self.current_frame_index = 0
        self.frame_tick          = 0

        # --- Attack state ---
        # self.attacking is only True for ONE frame — the exact frame the player presses Space.
        # main.py checks this flag to damage nearby enemies, then handle_input() resets it
        # back to False at the very start of the next frame.
        self.attacking = False

        # This timer counts DOWN from ATTACK_COOLDOWN to 0 after each attack.
        # The player cannot attack again until it reaches 0.
        self.attack_cooldown_ticks = 0

        # --- Endurance regen timer ---
        # Counts up every frame; when it hits ENDURANCE_REGEN_RATE we add 1 endurance
        self.endurance_regen_ticks = 0

        # --- Death and respawn ---
        self.is_dead_flag = False   # True while showing the "You died!" screen
        self.death_timer  = 0       # Counts down to 0, then we respawn

        # --- Font for drawing the character name below the sprite ---
        self.label_font = pygame.font.SysFont("Arial", 12)

    # -----------------------------------------------------------------------
    # Input handling — called every frame from main.py
    # -----------------------------------------------------------------------

    def handle_input(self, keys_pressed):
        """Read which keys are held down and move / animate the player.

        This is called once every frame (60 times per second).

        keys_pressed -- a dictionary from pygame that says which keys are held
        """
        # Reset the attack signal at the start of every frame.
        # It was set to True last frame (when Space was pressed); now we clear it
        # so main.py knows the "hit window" for that attack is over.
        self.attacking = False

        # Count down the attack cooldown each frame.
        # When it hits 0 the player is allowed to attack again.
        if self.attack_cooldown_ticks > 0:
            self.attack_cooldown_ticks -= 1

        # Check if the player wants to run (holding Shift)
        running = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]

        # --- Endurance cost for running ---
        # Running spends endurance every frame. When it runs out, the player
        # is forced back to a walk!
        if running:
            if self.endurance > 0:
                self.endurance = max(0, self.endurance - ENDURANCE_RUN_COST)
            else:
                running = False   # No endurance left — forced to walk

        # Set speed based on whether we're running or walking
        self.speed = RUN_SPEED if running else WALK_SPEED

        # Remember position before moving, so we know if the player actually moved
        old_x = self.x
        old_y = self.y

        # Move in four directions (arrow keys or WASD)
        if keys_pressed[pygame.K_UP]    or keys_pressed[pygame.K_w]: self.y -= self.speed
        if keys_pressed[pygame.K_DOWN]  or keys_pressed[pygame.K_s]: self.y += self.speed
        if keys_pressed[pygame.K_LEFT]  or keys_pressed[pygame.K_a]: self.x -= self.speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]: self.x += self.speed

        moved = (self.x != old_x) or (self.y != old_y)

        # --- Endurance regen when resting ---
        # Endurance refills by 1 every ENDURANCE_REGEN_RATE frames, but ONLY when:
        # - Not running (running costs endurance, can't regen at the same time)
        # - Not in an attack cooldown (attacking also pauses regen)
        if not running and self.attack_cooldown_ticks <= 0:
            self.endurance_regen_ticks += 1
            if self.endurance_regen_ticks >= ENDURANCE_REGEN_RATE:
                self.endurance_regen_ticks = 0
                self.restore_endurance(1)   # restore_endurance won't go over the max

        # Only switch to a movement animation when NOT currently attacking.
        # We wait for the cooldown to reach 0 before going back to idle/walk/run.
        if self.current_animation != "attack" or self.attack_cooldown_ticks <= 0:
            self._set_movement_animation(moved, running)

        self._advance_animation()

    def handle_attack(self, event):
        """Check if the player pressed Space to attack.

        This is called from main.py's KEYDOWN event handler — NOT every frame.
        Because it listens to KEYDOWN (not keys_pressed), it only fires once per
        key-press, which is exactly what we want for attacks.

        event -- the pygame KEYDOWN event that just happened
        """
        if event.key == pygame.K_SPACE and self.attack_cooldown_ticks <= 0:
            # Can't attack without any endurance!
            if self.endurance <= 0:
                return

            # Tell main.py "an attack happened THIS frame — check enemy hits!"
            self.attacking = True

            # Start the cooldown timer so the player has to wait before attacking again
            self.attack_cooldown_ticks = ATTACK_COOLDOWN

            # Spend some endurance for the attack
            self.use_endurance(ENDURANCE_ATTACK_COST)

            # Switch to the attack animation and restart it from the very first frame
            self.current_animation   = "attack"
            self.current_frame_index = 0
            self.frame_tick          = 0

    # -----------------------------------------------------------------------
    # Screen boundary — called every frame from main.py after handle_input
    # -----------------------------------------------------------------------

    def keep_on_screen(self, screen_width, screen_height):
        """Make sure the player can't walk off the edge of the screen.

        max() and min() clamp the value between two numbers — a handy trick!
        """
        self.x = max(0, min(self.x, screen_width  - SPRITE_SIZE))
        self.y = max(0, min(self.y, screen_height - SPRITE_SIZE))

    # -----------------------------------------------------------------------
    # Attack helpers — used by main.py
    # -----------------------------------------------------------------------

    def get_attack_rect(self):
        """Return a rectangle showing the area that the player's attack can reach.

        Any enemy whose rectangle overlaps this one takes damage when self.attacking is True.
        The rectangle is centered on the player and extends ATTACK_RANGE_PX in all directions.
        """
        center_x = self.x + SPRITE_SIZE // 2
        center_y = self.y + SPRITE_SIZE // 2

        return pygame.Rect(
            center_x - ATTACK_RANGE_PX,
            center_y - ATTACK_RANGE_PX,
            ATTACK_RANGE_PX * 2,
            ATTACK_RANGE_PX * 2,
        )

    def get_attack_damage(self):
        """Calculate how much damage this player deals per hit.

        Magic weapons (staff, laser) use the Magic stat.
        All other weapons (sword, daggers, pickaxe, shuriken) use Strength.

        Total damage = ATTACK_BASE_DAMAGE + the relevant stat.
        Example: Knight (STR=5) deals 1 + 5 = 6 damage per hit!
        """
        if self.weapon_type in WEAPON_USES_MAGIC:
            return ATTACK_BASE_DAMAGE + self.magic
        else:
            return ATTACK_BASE_DAMAGE + self.strength

    # -----------------------------------------------------------------------
    # Leveling up
    # -----------------------------------------------------------------------

    def collect_shard(self):
        """Called when the player picks up a magical shard.

        Adds one to the running total. Every 5 shards = one level-up!
        Sets level_up_pending = True so main.py knows to show the level-up screen.
        """
        self.shards_collected += 1
        # % is the "modulo" operator — it gives the remainder after dividing.
        # shards_collected % 5 == 0 is True when the total is exactly 5, 10, 15, 20...
        if self.shards_collected % 5 == 0:
            self.level_up_pending = True   # Time to level up!

    def apply_level_up(self, stat_choice):
        """Apply one level-up reward based on the player's choice.

        stat_choice can be: "health", "endurance", "strength", or "magic"

        Called by main.py after the player presses a key on the level-up screen.
        """
        self.level += 1

        if stat_choice == "health":
            self.max_health += 2                                       # Max HP goes up
            self.health = min(self.health + 2, self.max_health)        # Heal a little too
        elif stat_choice == "endurance":
            self.max_endurance += 2
            self.endurance = min(self.endurance + 2, self.max_endurance)
        elif stat_choice == "strength":
            self.strength += 1   # One more point of Strength!
        elif stat_choice == "magic":
            self.magic += 1      # One more point of Magic!

        self.level_up_pending = False   # Clear the flag — level-up is done

    # -----------------------------------------------------------------------
    # Death and respawn
    # -----------------------------------------------------------------------

    def trigger_death(self):
        """The player has been killed! Start the death display timer."""
        self.is_dead_flag = True
        self.death_timer  = DEATH_DISPLAY_TICKS

    def respawn(self, x, y):
        """Bring the player back to life at a respawn point.

        x, y -- the pixel coordinates of the respawn spot.
        The player comes back with 50% of their max health (at least 1 HP).
        Endurance is fully restored on respawn.
        """
        self.x = x
        self.y = y
        self.health     = max(1, self.max_health // 2)   # 50% health, never zero
        self.endurance  = self.max_endurance              # Full endurance!
        self.is_dead_flag = False
        self.death_timer  = 0

    def update_death_timer(self):
        """Count down the "You died!" display timer.

        Returns True when the timer reaches zero (meaning: time to respawn now!).
        main.py calls this every frame while is_dead_flag is True.
        """
        if self.death_timer > 0:
            self.death_timer -= 1
        return self.death_timer <= 0   # True = ready to respawn

    # -----------------------------------------------------------------------
    # Private animation helpers (only used inside this class — that's what the
    # underscore _ at the start of the name means)
    # -----------------------------------------------------------------------

    def _set_movement_animation(self, moved, running):
        """Pick the right animation for how the player is moving."""
        if not moved:
            target = "idle"
        else:
            target = "run" if running else "walk"

        # Only restart the animation if it changed — avoids a stuttering reset every frame
        if target != self.current_animation:
            self.current_animation   = target
            self.current_frame_index = 0
            self.frame_tick          = 0

    def _advance_animation(self):
        """Move to the next frame of the current animation when enough time has passed."""
        frames          = self.animations[self.current_animation]
        animation_speed = ANIMATION_SPEEDS[self.current_animation]

        self.frame_tick += 1
        if self.frame_tick >= animation_speed:
            self.frame_tick          = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)

    # -----------------------------------------------------------------------
    # Stat helpers — called by items, enemies, and UI code
    # -----------------------------------------------------------------------

    def take_damage(self, amount):
        """Reduce health by amount. Can't go below 0."""
        self.health = max(0, self.health - amount)

    def use_endurance(self, amount):
        """Spend endurance. Returns True if successful, False if not enough."""
        if self.endurance >= amount:
            self.endurance -= amount
            return True
        return False

    def restore_health(self, amount):
        """Heal the player, but never above max_health."""
        self.health = min(self.max_health, self.health + amount)

    def restore_endurance(self, amount):
        """Refill endurance, but never above max_endurance."""
        self.endurance = min(self.max_endurance, self.endurance + amount)

    def is_alive(self):
        """Return True if the player still has health left."""
        return self.health > 0

    def get_health_fraction(self):
        """Return health as a number between 0.0 and 1.0 — used by the HUD health bar."""
        return self.health / self.max_health

    def get_endurance_fraction(self):
        """Return endurance as a number between 0.0 and 1.0 — used by the HUD endurance bar."""
        if self.max_endurance == 0:
            return 0.0
        return self.endurance / self.max_endurance

    def get_strength_fraction(self):
        """Return strength as 0.0 to 1.0 for the HUD strength bar.
        We use 10 as the maximum — the bar is full at STR 10.
        """
        return min(self.strength / 10, 1.0)

    def get_magic_fraction(self):
        """Return magic as 0.0 to 1.0 for the HUD magic bar.
        We use 10 as the maximum — the bar is full at MAG 10.
        """
        return min(self.magic / 10, 1.0)

    # -----------------------------------------------------------------------
    # Drawing helpers
    # -----------------------------------------------------------------------

    def get_portrait_surface(self, size):
        """Return the first idle frame scaled to size x size pixels for the HUD portrait."""
        source = self.animations["idle"][0]
        return pygame.transform.scale(source, (size, size))

    def draw(self, screen):
        """Draw the player sprite and their name label on screen."""
        # Draw the current animation frame at the player's position
        frame = self.animations[self.current_animation][self.current_frame_index]
        screen.blit(frame, (self.x, self.y))

        # Draw the character class name just below the sprite (centred)
        label_surface = self.label_font.render(self.character_class, True, (255, 255, 255))
        label_x = self.x + SPRITE_SIZE // 2 - label_surface.get_width() // 2
        label_y = self.y + SPRITE_SIZE + 2   # 2 pixels below the bottom of the sprite
        screen.blit(label_surface, (label_x, label_y))
