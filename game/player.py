# ============================================================
# game/player.py — The Player Character
#
# This file defines everything about the player: how they move,
# how much health and energy they have, and how they look on screen.
# The player can be a Wizard, Knight, Assassin, Miner, Ninja, or Robot!
# ============================================================

import pygame

# ── Constants ──────────────────────────────────────────────
# These numbers never change — they describe how the player behaves.
# Using names instead of raw numbers makes the code easier to read and fix!

WALK_SPEED = 3       # How many pixels the player moves each frame when walking
RUN_SPEED  = 6       # How many pixels the player moves each frame when running (hold Shift)
START_HEALTH = 10    # How much health the player starts with
START_ENERGY = 10    # How much energy the player starts with
SPRITE_SIZE  = 48    # The player is drawn as a 48 x 48 pixel square

# Each character class gets its own bright color so you can tell them apart.
# These are (Red, Green, Blue) color values from 0 to 255.
CLASS_COLORS = {
    "Wizard":    (148,  0, 211),   # Purple — magical!
    "Knight":    ( 70, 130, 180),  # Steel blue — strong armor
    "Assassin":  ( 50,  50,  50),  # Dark grey — sneaky
    "Miner":     (139,  90,  43),  # Brown — earthy
    "Ninja":     ( 20, 180,  20),  # Bright green — fast
    "Robot":     (200, 200, 200),  # Silver — metallic
}

# If someone picks a class we don't know, use this color so the game doesn't crash.
FALLBACK_COLOR = (255, 165, 0)   # Orange

# The dark outline drawn around the player so they stand out from any background.
OUTLINE_COLOR = (26, 26, 26)   # #1A1A1A — very dark, almost black


# ── Player Class ───────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    """Represents the hero that the player controls on screen."""

    def __init__(self, character_class, screen_width, screen_height):
        """Set up a brand-new player with full health and energy, placed in the center of the screen."""
        # Always call the parent Sprite setup first — Pygame needs this!
        super().__init__()

        # Remember what kind of hero this player chose
        self.character_class = character_class

        # Health — when this hits 0 the hero is defeated
        self.health     = START_HEALTH
        self.max_health = START_HEALTH

        # Energy — used for special moves (we'll add those later!)
        self.energy     = START_ENERGY
        self.max_energy = START_ENERGY

        # Start the player right in the middle of the screen so they can see everything
        self.x = screen_width  // 2 - SPRITE_SIZE // 2   # Center horizontally
        self.y = screen_height // 2 - SPRITE_SIZE // 2   # Center vertically

        # Default speed is walking speed — changes to run speed when Shift is held
        self.speed = WALK_SPEED

        # Pick the color that matches this character class
        self.color = CLASS_COLORS.get(character_class, FALLBACK_COLOR)

        # We create the font here, not inside draw(), because loading a font every frame would be very slow
        self.label_font = pygame.font.SysFont("Arial", 12)

    # ── Movement ───────────────────────────────────────────

    def handle_input(self, keys_pressed):
        """Read the keyboard and move the player up, down, left, or right. Hold Shift to run."""

        # Check if Shift is held — if yes, the player runs instead of walks
        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
            self.speed = RUN_SPEED
        else:
            self.speed = WALK_SPEED

        # Move UP — arrow key up OR the W key
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.y -= self.speed   # Subtract because (0,0) is the TOP-LEFT corner

        # Move DOWN — arrow key down OR the S key
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.y += self.speed   # Add because going DOWN increases the Y value

        # Move LEFT — arrow key left OR the A key
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.x -= self.speed

        # Move RIGHT — arrow key right OR the D key
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.x += self.speed

    def keep_on_screen(self, screen_width, screen_height):
        """Make sure the player cannot walk off the edge of the screen."""

        # Clamp means "if the number is too small, make it the minimum; if too big, make it the maximum"
        self.x = max(0, min(self.x, screen_width  - SPRITE_SIZE))  # Stay within left/right edges
        self.y = max(0, min(self.y, screen_height - SPRITE_SIZE))  # Stay within top/bottom edges

    # ── Health & Energy ────────────────────────────────────

    def take_damage(self, amount):
        """Reduce the player's health by amount, but never let it go below 0."""

        # We subtract the damage, then make sure we don't drop below zero
        self.health = max(0, self.health - amount)

    def use_energy(self, amount):
        """Try to spend energy for a special move. Returns True if it worked, False if there wasn't enough."""

        # Check first — we don't want negative energy!
        if self.energy >= amount:
            self.energy -= amount
            return True   # Success! The move can happen
        else:
            return False  # Not enough energy, the move is blocked

    def restore_health(self, amount):
        """Heal the player by amount, but never go over their maximum health."""

        # max_health is the ceiling — healing can't go higher than that
        self.health = min(self.max_health, self.health + amount)

    def restore_energy(self, amount):
        """Recharge the player's energy by amount, but never go over their maximum energy."""

        # max_energy is the ceiling — recharging can't go higher than that
        self.energy = min(self.max_energy, self.energy + amount)

    # ── Status Checks ──────────────────────────────────────

    def is_alive(self):
        """Return True if the player still has health remaining, False if they have been defeated."""

        # The player is alive as long as health is above zero
        return self.health > 0

    def get_health_fraction(self):
        """Return health as a number between 0.0 (empty) and 1.0 (full) — useful for drawing the health bar."""

        # Dividing current health by max health gives a percentage as a decimal
        return self.health / self.max_health

    def get_energy_fraction(self):
        """Return energy as a number between 0.0 (empty) and 1.0 (full) — useful for drawing the energy bar."""

        return self.energy / self.max_energy

    # ── Drawing ────────────────────────────────────────────

    def draw(self, screen):
        """Draw the player on the screen as a colored rectangle with their class name underneath."""

        # Draw the main player body — a solid colored square
        player_rect = pygame.Rect(self.x, self.y, SPRITE_SIZE, SPRITE_SIZE)
        pygame.draw.rect(screen, self.color, player_rect)

        # Draw a dark outline around the player so they stand out from the background
        pygame.draw.rect(screen, OUTLINE_COLOR, player_rect, width=2)  # width=2 means only the border

        # Draw a small label below the player showing what class they are
        # This helps during development before we have real sprite art!
        label_surface = self.label_font.render(self.character_class, True, (255, 255, 255))  # White text

        # Center the label under the player sprite
        label_x = self.x + SPRITE_SIZE // 2 - label_surface.get_width() // 2
        label_y = self.y + SPRITE_SIZE + 2   # 2 pixels below the bottom of the sprite

        screen.blit(label_surface, (label_x, label_y))   # blit means "draw this image onto the screen"
