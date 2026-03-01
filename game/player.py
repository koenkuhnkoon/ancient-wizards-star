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
# Per-class stats — each character class starts with different HP, Strength,
# Magic, and Endurance values to make each class feel unique!
#
# max_health    (how many hit points you start with — different for each class!)
# STR = Strength   (used for physical weapons like swords and pickaxes)
# MAG = Magic      (used for magic weapons like staffs and laser beams)
# max_endurance    (how much endurance you start with)
# ---------------------------------------------------------------------------
CLASS_STATS = {
    # Wizard: glass cannon — low HP and endurance, but super high magic power
    "Wizard":   {"max_health":  8, "strength": 1, "magic": 6, "max_endurance": 2},
    # Knight: tank — lots of HP and strength, not much magic
    "Knight":   {"max_health": 14, "strength": 5, "magic": 1, "max_endurance": 4},
    # Assassin: speedy — lots of endurance to run and dodge, good strength
    "Assassin": {"max_health":  9, "strength": 4, "magic": 1, "max_endurance": 6},
    # Miner: tough brawler — good HP and strength, slow but hits hard
    "Miner":    {"max_health": 12, "strength": 5, "magic": 1, "max_endurance": 3},
    # Ninja: balanced — medium everything, good speed and technique
    "Ninja":    {"max_health": 10, "strength": 3, "magic": 3, "max_endurance": 5},
    # Robot: tech hybrid — mix of physical strength and magic lasers
    "Robot":    {"max_health": 11, "strength": 4, "magic": 3, "max_endurance": 3},
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
ATTACK_COOLDOWN    = 30   # Default frames to wait between attacks (30 = 0.5 s at 60 FPS)
ATTACK_RANGE_PX    = 50   # Pixels from player center — enemies inside this square get hit
ATTACK_BASE_DAMAGE =  1   # Base hit damage before adding the player's stat

# ---------------------------------------------------------------------------
# Per-weapon cooldowns — melee weapons can swing more frequently than ranged.
# Ranged weapons are longer cooldown to balance their "safe distance" advantage.
# ---------------------------------------------------------------------------
WEAPON_COOLDOWNS = {
    "staff":    30,   # 0.5 s — snappy area blast
    "sword":    30,   # 0.5 s — standard sword swing
    "daggers":  20,   # 0.33 s — fast stabber, but short range
    "pickaxe":  45,   # 0.75 s — heavy and slow, but wide arc
    "shuriken": 50,   # 0.83 s — reach back for another throwing star
    "laser":    60,   # 1.0 s — recharge the energy cell between blasts
}

# ---------------------------------------------------------------------------
# Assassin daggers: special damage rules!
# Daggers are SO sharp that they one-shot any regular enemy.
# Mini-bosses survive longer — it takes 3 hits to bring them down.
# ---------------------------------------------------------------------------
ASSASSIN_REGULAR_MULTIPLIER   = 999   # Effectively one-shots any normal enemy
ASSASSIN_MINIBOSS_MULTIPLIER  = 0.34  # Fraction of max HP per hit (3 hits to kill)

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

        # --- Class-specific stats (HP, Strength, Magic, Endurance) ---
        # Look up this class's starting numbers from the CLASS_STATS table above
        stats = CLASS_STATS[character_class]

        # --- Health ---
        # Each class has its own starting HP — set by CLASS_STATS above!
        self.max_health = stats["max_health"]   # Each class has its own starting HP!
        self.health     = self.max_health

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

        # --- Facing direction ---
        # Which way is the player looking? Used to aim weapon attacks!
        # "right", "left", "up", or "down"
        self.facing = "right"

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

        # --- Sprite dimensions (used by attack zone calculations) ---
        self.sprite_width  = SPRITE_SIZE
        self.sprite_height = SPRITE_SIZE

        # --- Font for drawing the character name below the sprite ---
        self.label_font = pygame.font.SysFont("Arial", 12)

    # -----------------------------------------------------------------------
    # Input handling — called every frame from main.py
    # -----------------------------------------------------------------------

    def handle_input(self, keys_pressed, touch_input=None):
        """Read which keys are held down and move / animate the player.

        This is called once every frame (60 times per second).

        keys_pressed -- a dictionary from pygame that says which keys are held
        touch_input  -- optional virtual-control state from main.py
        """
        # Reset the attack signal at the start of every frame.
        # It was set to True last frame (when Space was pressed); now we clear it
        # so main.py knows the "hit window" for that attack is over.
        self.attacking = False

        # Count down the attack cooldown each frame.
        # When it hits 0 the player is allowed to attack again.
        if self.attack_cooldown_ticks > 0:
            self.attack_cooldown_ticks -= 1

        touch_input = touch_input or {}

        # Check if the player wants to run (holding Shift or pushing joystick far)
        running = (
            keys_pressed[pygame.K_LSHIFT]
            or keys_pressed[pygame.K_RSHIFT]
            or touch_input.get("run", False)
        )

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

        # Calculate how far to move in each direction this frame
        dx = 0
        dy = 0

        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a] or touch_input.get("left", False):
            dx -= self.speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d] or touch_input.get("right", False):
            dx += self.speed
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w] or touch_input.get("up", False):
            dy -= self.speed
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s] or touch_input.get("down", False):
            dy += self.speed

        self.x += dx
        self.y += dy

        # --- Update facing direction ---
        # Only change facing when actually moving — standing still keeps the last direction.
        # We check horizontal first so left/right takes priority when moving diagonally.
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

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

    def try_attack(self):
        """Try to start an attack and return True when successful."""
        if self.attack_cooldown_ticks > 0:
            return False

        # Can't attack without any endurance!
        if self.endurance <= 0:
            return False

        # Tell main.py "an attack happened THIS frame — check enemy hits!"
        self.attacking = True

        # Start the cooldown timer — each weapon has its own wait time!
        self.attack_cooldown_ticks = WEAPON_COOLDOWNS.get(self.weapon_type, ATTACK_COOLDOWN)

        # Spend some endurance for the attack
        self.use_endurance(ENDURANCE_ATTACK_COST)

        # Switch to the attack animation and restart it from the very first frame
        self.current_animation   = "attack"
        self.current_frame_index = 0
        self.frame_tick          = 0
        return True

    def handle_attack(self, event):
        """Check if the player pressed Space to attack.

        This is called from main.py's KEYDOWN event handler — NOT every frame.
        Because it listens to KEYDOWN (not keys_pressed), it only fires once per
        key-press, which is exactly what we want for attacks.

        event -- the pygame KEYDOWN event that just happened
        """
        if event.key == pygame.K_SPACE:
            self.try_attack()

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

    def get_attack_zones(self):
        """Return a list of rectangles showing the areas this weapon can hit.

        Different weapons hit different shapes and directions:
        - Staff (Wizard): big burst in all directions around the player
        - Sword (Knight): forward slash — medium rect in the direction you're facing
        - Daggers (Assassin): short close thrust — very close range in front
        - Pickaxe (Miner): wide heavy swing — wider than the sword
        - Shuriken (Ninja): ranged projectile — no melee zone, returns empty list!
        - Laser (Robot): ranged beam — no melee zone, returns empty list!

        We use the player's CENTER point to build the zones so the hit area
        is always centered on the character, no matter which direction they face.
        """
        # Player center point — our reference for all hit zones
        cx = self.x + self.sprite_width  // 2
        cy = self.y + self.sprite_height // 2

        if self.weapon_type == "staff":
            # Wizard staff: big magic burst centered on the player!
            # 100x100 px circle (well, square) of pure magical energy.
            return [pygame.Rect(cx - 50, cy - 50, 100, 100)]

        elif self.weapon_type == "sword":
            # Knight sword: a forward slash — 80px wide, 50px deep.
            # The rect extends OUT from the player in the direction they're facing.
            w, h = 80, 50
            if self.facing == "right":
                return [pygame.Rect(cx + 4,     cy - h // 2, w, h)]
            elif self.facing == "left":
                return [pygame.Rect(cx - 4 - w, cy - h // 2, w, h)]
            elif self.facing == "down":
                return [pygame.Rect(cx - w // 2, cy + 4,     h, w)]
            else:  # up
                return [pygame.Rect(cx - w // 2, cy - 4 - w, h, w)]

        elif self.weapon_type == "daggers":
            # Assassin daggers: a short close thrust — 40px wide, 32px deep.
            # Very close range but super deadly!
            w, h = 40, 32
            if self.facing == "right":
                return [pygame.Rect(cx + 4,     cy - h // 2, w, h)]
            elif self.facing == "left":
                return [pygame.Rect(cx - 4 - w, cy - h // 2, w, h)]
            elif self.facing == "down":
                return [pygame.Rect(cx - w // 2, cy + 4,     h, w)]
            else:  # up
                return [pygame.Rect(cx - w // 2, cy - 4 - w, h, w)]

        elif self.weapon_type == "pickaxe":
            # Miner pickaxe: wide heavy arc — 110px wide, 40px deep.
            # Slower weapon but hits a BIG area!
            w, h = 110, 40
            if self.facing == "right":
                return [pygame.Rect(cx + 4,     cy - h // 2, w, h)]
            elif self.facing == "left":
                return [pygame.Rect(cx - 4 - w, cy - h // 2, w, h)]
            elif self.facing == "down":
                return [pygame.Rect(cx - w // 2, cy + 4,     h, w)]
            else:  # up
                return [pygame.Rect(cx - w // 2, cy - 4 - w, h, w)]

        elif self.weapon_type == "laser":
            # Robot laser: instant beam — long and thin in the facing direction.
            # 400 px long, 12 px thick. Hits ALL enemies along the beam in one frame!
            beam_len   = 400
            beam_thick = 12
            if self.facing == "right":
                return [pygame.Rect(cx + 4,            cy - beam_thick // 2, beam_len,   beam_thick)]
            elif self.facing == "left":
                return [pygame.Rect(cx - 4 - beam_len, cy - beam_thick // 2, beam_len,   beam_thick)]
            elif self.facing == "down":
                return [pygame.Rect(cx - beam_thick // 2, cy + 4,            beam_thick, beam_len)]
            else:  # up
                return [pygame.Rect(cx - beam_thick // 2, cy - 4 - beam_len, beam_thick, beam_len)]

        elif self.weapon_type == "shuriken":
            # Shuriken is a flying projectile — NO melee zone here.
            # main.py spawns a Projectile when the Ninja attacks.
            return []

        # Default fallback (shouldn't happen, but just in case!)
        return []

    def is_ranged_weapon(self):
        """Returns True if this weapon fires a flying projectile.

        Only the Ninja's shuriken is a true projectile now.
        The Robot's laser is an instant beam handled as a wide attack zone,
        so it returns False here — get_attack_zones() gives it its long thin rect.
        """
        return self.weapon_type == "shuriken"

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

    def get_assassin_damage(self, target_max_hp, is_miniboss):
        """Special dagger damage — one-shots normal enemies, needs 3 hits for mini-bosses.

        Daggers are amazing against regular monsters — one strike and they're gone!
        Mini-bosses are tough though, so even daggers need 3 hits to take them down.

        target_max_hp -- the maximum health of the enemy being hit
        is_miniboss   -- True if the target is a mini-boss (Grimrak, Zara, etc.)
        """
        if is_miniboss:
            # Deal 1/3 of the boss's max HP each hit — so it takes exactly 3 hits
            return max(1, int(target_max_hp * ASSASSIN_MINIBOSS_MULTIPLIER))
        else:
            # Daggers are deadly — one shot for any regular enemy!
            return target_max_hp + 1

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
        The player comes back with FULL health — you're back!
        Endurance is fully restored on respawn.
        """
        self.x = x
        self.y = y
        self.health     = self.max_health   # Full health — you're back!
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
