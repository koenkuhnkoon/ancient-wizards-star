"""Player entity and animation runtime.

This file controls everything about the player character:
- Moving around the world (arrow keys or WASD)
- Running (hold Shift)
- Attacking (press Space)
- Health and energy stats
- Drawing the player sprite and name label on screen

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
# Starting stats — the player begins every game with these values
# ---------------------------------------------------------------------------
START_HEALTH = 10
START_ENERGY = 10

# ---------------------------------------------------------------------------
# Sprite size — every character sheet frame is 48 × 48 pixels
# ---------------------------------------------------------------------------
SPRITE_SIZE = 48

# ---------------------------------------------------------------------------
# Attack constants — these control how the Space-bar attack works
#
# ATTACK_COOLDOWN: after attacking, the player must wait this many frames
#   before they can attack again.  30 frames at 60 FPS = 0.5 seconds.
#   Without a cooldown, the player could attack 60 times a second — way too strong!
#
# ATTACK_RANGE_PX: the attack hits enemies within this many pixels of the
#   player's center in every direction.  Think of it like swinging a sword
#   in a circle around the hero.
#
# ATTACK_DAMAGE: how much health an enemy loses from a single hit.
# ---------------------------------------------------------------------------
ATTACK_COOLDOWN = 30   # Frames to wait between attacks (30 = 0.5 s at 60 FPS)
ATTACK_RANGE_PX = 50   # Pixels from player center — enemies inside this square get hit
ATTACK_DAMAGE   =  2   # Health points an enemy loses per hit

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

        character_class -- which hero type was chosen (e.g. "wizard", "knight")
        screen_width    -- how wide the game window is, so we can start in the middle
        screen_height   -- how tall the game window is, same reason
        """
        # Always call the parent Sprite setup first — Pygame needs this!
        super().__init__()

        self.character_class = character_class

        # --- Health and Energy ---
        self.health     = START_HEALTH
        self.max_health = START_HEALTH
        self.energy     = START_ENERGY
        self.max_energy = START_ENERGY

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
        # Why only one frame?  If it stayed True for longer, the same key-press would
        # hit enemies over and over — that wouldn't be fair!
        self.attacking = False

        # This timer counts DOWN from ATTACK_COOLDOWN to 0 after each attack.
        # The player cannot attack again until it reaches 0.
        self.attack_cooldown_ticks = 0

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

        # Speed: walk normally, run if Shift is held
        running    = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]
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

        # Only switch to a movement animation when NOT currently attacking.
        # We wait for the cooldown to reach 0 before going back to idle/walk/run.
        # Why?  Switching to a different animation mid-swing would look glitchy,
        # and it gives the attack animation time to play all the way through!
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
            # Tell main.py "an attack happened THIS frame — check enemy hits!"
            self.attacking = True

            # Start the cooldown timer so the player has to wait before attacking again
            self.attack_cooldown_ticks = ATTACK_COOLDOWN

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
    # Attack helper — used by main.py to check which enemies get hit
    # -----------------------------------------------------------------------

    def get_attack_rect(self):
        """Return a rectangle showing the area that the player's attack can reach.

        Any enemy whose rectangle overlaps this one takes damage when self.attacking is True.
        The rectangle is centered on the player and extends ATTACK_RANGE_PX in all directions.

        Think of it like the player swinging a sword in a circle around them!
        """
        # Find the center of the player sprite
        center_x = self.x + SPRITE_SIZE // 2
        center_y = self.y + SPRITE_SIZE // 2

        # Build a square hit area centered on the player
        return pygame.Rect(
            center_x - ATTACK_RANGE_PX,   # left edge
            center_y - ATTACK_RANGE_PX,   # top edge
            ATTACK_RANGE_PX * 2,          # width  (left arm + right arm of the swing)
            ATTACK_RANGE_PX * 2,          # height (above + below)
        )

    # -----------------------------------------------------------------------
    # Private animation helpers (only used inside this class — that's what the
    # underscore _ at the start of the name means)
    # -----------------------------------------------------------------------

    def _set_movement_animation(self, moved, running):
        """Pick the right animation for how the player is moving.

        moved   -- True if the player pressed a direction key this frame
        running -- True if Shift is held
        """
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
            # % len(frames) wraps back to 0 when we reach the last frame — it loops!
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)

    # -----------------------------------------------------------------------
    # Stat helpers — called by items, enemies, and UI code
    # -----------------------------------------------------------------------

    def take_damage(self, amount):
        """Reduce health by amount.  Can't go below 0."""
        self.health = max(0, self.health - amount)

    def use_energy(self, amount):
        """Spend energy if there's enough.  Returns True if successful, False if not."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def restore_health(self, amount):
        """Heal the player, but never above max_health."""
        self.health = min(self.max_health, self.health + amount)

    def restore_energy(self, amount):
        """Refill energy, but never above max_energy."""
        self.energy = min(self.max_energy, self.energy + amount)

    def is_alive(self):
        """Return True if the player still has health left."""
        return self.health > 0

    def get_health_fraction(self):
        """Return health as a number between 0.0 and 1.0 — used by the HUD health bar."""
        return self.health / self.max_health

    def get_energy_fraction(self):
        """Return energy as a number between 0.0 and 1.0 — used by the HUD energy bar."""
        return self.energy / self.max_energy

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
