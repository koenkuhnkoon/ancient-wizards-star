"""game/sound.py — Sound Manager for The Ancient Wizard's Star.

This module handles ALL audio for the game:
  - Background music (looping tracks for menus, exploration, and boss fights)
  - Sound effects (SFX) for player actions, items, enemies, and UI

All sound files live in assets/sounds/.
If a file is missing the game still runs — and now it plays a little beep
placeholder so you can actually HEAR that the sound hook is working!
That means you can add real sounds one at a time as you find or make them.

Koen & Luca: to add a new sound, drop the .wav or .ogg file into
assets/sounds/ and it will be picked up automatically next time you run!
The placeholder beep will disappear as soon as the real file is there.
"""

import pygame
from pathlib import Path

# ---------------------------------------------------------------------------
# Where to find all the sound files
# ---------------------------------------------------------------------------
SOUNDS_DIR = Path("assets") / "sounds"

# ---------------------------------------------------------------------------
# Channel layout — each TYPE of sound gets its own channel so they don't
# cut each other off.
#
# pygame.mixer.music handles background music separately (channel 0 style).
# Channels 1-7 are for sound effects.
# ---------------------------------------------------------------------------
CHANNEL_PLAYER  = 1   # Player actions: footsteps, attacks, hurt, death, respawn
CHANNEL_ITEMS   = 2   # Item pickups: shards, potions, portal key
CHANNEL_ENEMIES = 3   # Enemy sounds: attacks, deaths
CHANNEL_UI      = 4   # Menu clicks, stat selection, level-up chime
CHANNEL_AMBIENT = 5   # World ambient: portal gate hum

# ---------------------------------------------------------------------------
# Footstep timing — play a footstep sound every N game frames while moving
# ---------------------------------------------------------------------------
WALK_STEP_FRAMES = 18   # One footstep sound every 18 frames while walking
RUN_STEP_FRAMES  = 10   # One footstep sound every 10 frames while running

# ---------------------------------------------------------------------------
# Hurt cooldown — don't spam the hurt sound when taking rapid hits
# ---------------------------------------------------------------------------
HURT_COOLDOWN_FRAMES = 30   # 30 frames = 0.5 seconds at 60 FPS


class SoundManager:
    """Loads and plays all game audio.

    How to use in main.py:
        sounds = SoundManager()
        sounds.play_menu_music()         # start the menu music
        sounds.play("collect_shard")     # play a one-shot SFX
        sounds.set_enabled(False)        # mute everything
        sounds.tick()                    # call once per frame!
    """

    def __init__(self):
        # NOTE: pygame.mixer.pre_init() was already called in main.py BEFORE
        # pygame.init(), which is the correct order on Windows. Here we just
        # set the number of channels — we do NOT call pygame.mixer.init() again
        # because pre_init + pygame.init() already handled that for us!
        pygame.mixer.set_num_channels(8)

        self.enabled = True

        # All loaded SFX: name -> {"sound": Sound object, "channel": int}
        self.sfx = {}

        # Which music filename is currently active (so we don't restart it)
        self._current_music_file = None

        # Hurt cooldown — counts down each frame; play_hurt() waits until 0
        self._hurt_cooldown = 0

        # Footstep timer — counts up; resets when a step sound plays
        self._footstep_tick = 0

        # Load everything
        self._load_all()

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _make_placeholder_beep(self, frequency_hz, duration_s):
        """Generate a simple beep sound programmatically (no audio file needed).

        This is a temporary placeholder — replace with real sound files later!
        Each SFX gets a different frequency so you can tell them apart by ear.
        Returns a pygame.mixer.Sound object, or None if numpy is not available.

        Koen & Luca: numpy is a maths library that lets us draw a sine wave
        (the same wiggly shape as a real sound wave!) as numbers. Pygame can
        turn those numbers into audio. Pretty cool, right?
        """
        try:
            import numpy as np
            sample_rate = 44100                                # Samples per second (CD quality)
            num_samples = int(sample_rate * duration_s)       # Total number of samples
            t = np.linspace(0, duration_s, num_samples, endpoint=False)
            # Sine wave — 16383 is the max volume for 16-bit audio (half of 32767)
            wave = (np.sin(2 * np.pi * frequency_hz * t) * 16383).astype(np.int16)
            # pygame stereo needs shape (samples, 2) — one column per ear
            stereo = np.column_stack([wave, wave])
            return pygame.sndarray.make_sound(stereo)
        except Exception:
            # numpy not installed, or something else went wrong — stay silent
            return None

    def _load_sfx(self, name, filename, channel, volume, beep_hz=440, beep_dur=0.15):
        """Try to load one SFX file. Falls back to a placeholder beep if missing.

        name     — the short name used in play(), e.g. "collect_shard"
        filename — the actual file in assets/sounds/, e.g. "sfx_collect_shard.wav"
        channel  — which mixer channel to use (see CHANNEL_* constants above)
        volume   — loudness from 0.0 (silent) to 1.0 (full volume)
        beep_hz  — frequency of the placeholder beep (each SFX has its own!)
        beep_dur — how long the placeholder beep plays (in seconds)
        """
        path = SOUNDS_DIR / filename
        if path.exists():
            try:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(volume)
                self.sfx[name] = {"sound": sound, "channel": channel}
                return
            except Exception:
                pass   # Broken file — fall through to placeholder below

        # File missing or broken — use a placeholder beep so the hook is audible
        # during development. The beep is quieter so it's not too annoying!
        sound = self._make_placeholder_beep(beep_hz, beep_dur)
        if sound:
            sound.set_volume(volume * 0.4)   # Quieter than real SFX (placeholder mode)
            self.sfx[name] = {"sound": sound, "channel": channel}

    def _music_path(self, filename):
        """Return the full path string for a music file, or None if missing."""
        path = SOUNDS_DIR / filename
        return str(path) if path.exists() else None

    def _play_music_file(self, filename, loop=True):
        """Load and start a background music track. Loops by default."""
        if not self.enabled:
            return
        path = self._music_path(filename)
        if path is None:
            return   # File not there yet — stay silent until real music is added
        self._current_music_file = filename
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1 if loop else 0)   # -1 = loop forever
        except Exception:
            pass

    def _load_all(self):
        """Load every sound effect defined in the Sound Design Plan.

        Each SFX gets its own placeholder beep frequency (beep_hz) so you can
        tell them apart by ear during development. Higher number = higher pitch!
        """

        # -- Player Actions --
        # Walk: low rumble (200 Hz), very short (0.08 s)
        self._load_sfx("walk",          "sfx_player_walk.wav",          CHANNEL_PLAYER,  0.30, beep_hz=200, beep_dur=0.08)
        # Run: slightly higher (250 Hz), a touch faster
        self._load_sfx("run",           "sfx_player_run.wav",           CHANNEL_PLAYER,  0.45, beep_hz=250, beep_dur=0.07)
        # Swing: mid-range whoosh (350 Hz)
        self._load_sfx("attack_swing",  "sfx_player_attack_swing.wav",  CHANNEL_PLAYER,  0.70, beep_hz=350, beep_dur=0.15)
        # Hit: thuddy low (150 Hz) — sounds more impactful
        self._load_sfx("attack_hit",    "sfx_player_attack_hit.wav",    CHANNEL_PLAYER,  0.80, beep_hz=150, beep_dur=0.20)

        # -- Player State --
        # Hurt: low groan (180 Hz), quarter second
        self._load_sfx("player_hurt",   "sfx_player_hurt.wav",          CHANNEL_PLAYER,  0.80, beep_hz=180, beep_dur=0.25)
        # Die: the lowest, longest beep — very sad! (120 Hz, 0.5 s)
        self._load_sfx("player_die",    "sfx_player_die.wav",           CHANNEL_PLAYER,  0.90, beep_hz=120, beep_dur=0.50)
        # Respawn: bright and hopeful (520 Hz)
        self._load_sfx("respawn",       "sfx_player_respawn.wav",       CHANNEL_PLAYER,  0.80, beep_hz=520, beep_dur=0.40)
        # Level-up: high joyful chime (660 Hz)
        self._load_sfx("level_up",      "sfx_level_up_chime.wav",       CHANNEL_UI,      0.85, beep_hz=660, beep_dur=0.50)

        # -- Item Pickups --
        # Shard: sparkly high ping (880 Hz) — like a magic tinkle!
        self._load_sfx("collect_shard",      "sfx_collect_shard.wav",      CHANNEL_ITEMS,   0.75, beep_hz=880,  beep_dur=0.20)
        # Health potion: warm medium tone (740 Hz)
        self._load_sfx("collect_health",     "sfx_collect_health.wav",     CHANNEL_ITEMS,   0.70, beep_hz=740,  beep_dur=0.30)
        # Portal key: the highest, longest beep — this one is IMPORTANT! (1000 Hz)
        self._load_sfx("collect_portal_key", "sfx_collect_portal_key.wav", CHANNEL_ITEMS,   0.85, beep_hz=1000, beep_dur=0.60)

        # -- Enemy Sounds --
        # Hurt: medium growl (300 Hz)
        self._load_sfx("enemy_hurt",    "sfx_enemy_hurt.wav",           CHANNEL_ENEMIES, 0.70, beep_hz=300, beep_dur=0.12)
        # Die: slightly lower, longer (220 Hz)
        self._load_sfx("enemy_die",     "sfx_enemy_die.wav",            CHANNEL_ENEMIES, 0.80, beep_hz=220, beep_dur=0.30)
        # Attack: low menacing rumble (160 Hz)
        self._load_sfx("enemy_attack",  "sfx_enemy_attack.wav",         CHANNEL_ENEMIES, 0.65, beep_hz=160, beep_dur=0.15)

        # -- UI --
        # Menu click: clean mid-high tick (600 Hz)
        self._load_sfx("menu_click",    "sfx_menu_click.wav",           CHANNEL_UI,      0.70, beep_hz=600, beep_dur=0.08)
        # Stat select: slightly higher confirm (700 Hz)
        self._load_sfx("stat_select",   "sfx_stat_select.wav",          CHANNEL_UI,      0.75, beep_hz=700, beep_dur=0.10)
        # Pause open: classic 440 Hz A note
        self._load_sfx("pause_open",    "sfx_pause_open.wav",           CHANNEL_UI,      0.60, beep_hz=440, beep_dur=0.12)

        # -- World / Environment --
        # Portal hum: very low drone (130 Hz) — eerie and magical
        self._load_sfx("portal_hum",    "sfx_portal_hum.wav",           CHANNEL_AMBIENT, 0.40, beep_hz=130, beep_dur=0.50)

    # -----------------------------------------------------------------------
    # Public API — call these from main.py
    # -----------------------------------------------------------------------

    def set_enabled(self, enabled):
        """Mute or unmute all audio. Called when the player toggles Audio in the pause menu."""
        self.enabled = enabled
        if not enabled:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        else:
            # Resume the music track that was playing before muting.
            # If _current_music_file is None (e.g. game over just played),
            # we stay silent until respawn restarts the exploration music.
            if self._current_music_file:
                self._play_music_file(self._current_music_file)

    def tick(self):
        """Call this once per game frame to update internal timers.

        Must be called every frame even when paused, so timers stay correct!
        """
        if self._hurt_cooldown > 0:
            self._hurt_cooldown -= 1
        if self._footstep_tick > 0:
            self._footstep_tick -= 1

    def play(self, sfx_name):
        """Play a sound effect by name.

        Does nothing if audio is disabled or the file hasn't been added yet.
        """
        if not self.enabled:
            return
        entry = self.sfx.get(sfx_name)
        if entry:
            channel = pygame.mixer.Channel(entry["channel"])
            channel.play(entry["sound"])

    def play_hurt(self):
        """Play the player-hurt sound — but no more than once every 0.5 seconds.

        Without the cooldown, rapid enemy hits would spam the sound annoyingly!
        """
        if self._hurt_cooldown > 0:
            return
        self.play("player_hurt")
        self._hurt_cooldown = HURT_COOLDOWN_FRAMES

    def play_footstep(self, running):
        """Play walk or run footstep on a timed interval.

        running -- True if the player is sprinting (Shift held), False for walking
        Call this every frame while the player is moving.
        """
        if not self.enabled:
            return
        if self._footstep_tick > 0:
            return   # Not time for a step yet
        # Time for a footstep!
        sfx_name    = "run"  if running else "walk"
        step_frames = RUN_STEP_FRAMES if running else WALK_STEP_FRAMES
        self.play(sfx_name)
        self._footstep_tick = step_frames

    def reset_footstep(self):
        """Call when the player stops moving, so the next step fires right away."""
        self._footstep_tick = 0

    # -----------------------------------------------------------------------
    # Music transitions — switch tracks as the game state changes
    # -----------------------------------------------------------------------

    def play_menu_music(self):
        """Start the main menu / character select theme."""
        self._play_music_file("music_main_menu.ogg")

    def play_exploration_music(self):
        """Switch to the open-world exploration theme (only if not already playing)."""
        if self._current_music_file != "music_world_exploration.ogg":
            self._play_music_file("music_world_exploration.ogg")

    def play_grimrak_music(self):
        """Switch to Grimrak the Stone Golem's boss fight music."""
        self._play_music_file("music_boss_grimrak.ogg")

    def play_zara_music(self):
        """Switch to Zara the Storm Witch's boss fight music."""
        self._play_music_file("music_boss_zara.ogg")

    def play_game_over(self):
        """Play the death / game-over music sting once (does not loop).

        After this plays, _current_music_file is set to None.
        That means if the player toggles audio OFF then ON during the death screen,
        set_enabled(True) won't try to restart any music — it just stays quiet
        until respawn calls play_exploration_music() again.
        """
        pygame.mixer.music.stop()
        self._current_music_file = None   # Clear so audio-toggle doesn't restart music
        path = self._music_path("music_game_over.ogg")
        if path:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(0)   # 0 = play once, do not loop
            except Exception:
                pass

    def play_level_up_fanfare(self):
        """Play the short triumphant level-up fanfare."""
        self.play("level_up")
