"""Runtime sprite loading for player assets with placeholder fallback."""

from __future__ import annotations

from pathlib import Path

import pygame

from game.asset_manifest import PLAYER_SPRITES


ASSET_ROOT = Path("assets")
PLAYER_DIR = ASSET_ROOT   # All sprite sheets live directly in assets/
OUTLINE_COLOR = (26, 26, 26)


CLASS_FALLBACK_COLORS: dict[str, tuple[int, int, int]] = {
    "Wizard": (155, 89, 182),
    "Knight": (127, 140, 141),
    "Assassin": (26, 58, 58),
    "Miner": (46, 74, 122),
    "Ninja": (27, 42, 74),
    "Robot": (93, 122, 138),
}


def _sheet_path(prefix: str, animation: str) -> Path:
    return PLAYER_DIR / f"{prefix}_{animation}.png"


def _slice_sheet(sheet: pygame.Surface, frame_width: int, frame_height: int, frame_count: int) -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []
    for index in range(frame_count):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), area=pygame.Rect(index * frame_width, 0, frame_width, frame_height))
        frames.append(frame.convert_alpha())
    return frames


def _placeholder_frame(character_class: str, width: int, height: int) -> pygame.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    color = CLASS_FALLBACK_COLORS.get(character_class, (255, 165, 0))
    surface.fill(color)
    pygame.draw.rect(surface, OUTLINE_COLOR, surface.get_rect(), width=2)
    return surface


def _placeholder_frames(character_class: str, width: int, height: int, frame_count: int) -> list[pygame.Surface]:
    return [_placeholder_frame(character_class, width, height) for _ in range(frame_count)]


def load_player_animations(character_class: str) -> dict[str, list[pygame.Surface]]:
    """Load player animations from disk or generate placeholder frames.

    If idle/walk sheets are missing but the attack sheet loaded, we reuse the
    first attack frame so the character always looks like their illustrated self,
    not a coloured square.
    """
    spec = PLAYER_SPRITES[character_class]

    def _try_load(animation_name: str, expected_frames: int) -> list[pygame.Surface] | None:
        """Try to load one sprite sheet. Returns sliced frames or None on failure."""
        path = _sheet_path(spec.prefix, animation_name)
        if not path.exists():
            return None
        try:
            sheet = pygame.image.load(str(path)).convert_alpha()
            expected_size = (spec.frame_width * expected_frames, spec.frame_height)
            if sheet.get_size() != expected_size:
                return None
            return _slice_sheet(sheet, spec.frame_width, spec.frame_height, expected_frames)
        except Exception:
            return None

    attack_frames = _try_load("attack", spec.attack_frames)
    idle_frames   = _try_load("idle",   spec.idle_frames)
    walk_frames   = _try_load("walk",   spec.walk_frames)

    # If idle/walk sheets don't exist yet, repeat the first attack frame so the
    # character looks like their illustrated self instead of a coloured square.
    if attack_frames:
        if not idle_frames:
            idle_frames = [attack_frames[0]] * spec.idle_frames
        if not walk_frames:
            walk_frames = [attack_frames[0]] * spec.walk_frames

    def _placeholder(n: int) -> list[pygame.Surface]:
        return _placeholder_frames(character_class, spec.frame_width, spec.frame_height, n)

    loaded = {
        "attack": attack_frames or _placeholder(spec.attack_frames),
        "idle":   idle_frames   or _placeholder(spec.idle_frames),
        "walk":   walk_frames   or _placeholder(spec.walk_frames),
    }
    loaded["run"] = loaded["walk"]
    return loaded

