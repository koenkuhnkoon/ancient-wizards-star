"""Runtime sprite loading for player assets with placeholder fallback."""

from __future__ import annotations

from pathlib import Path

import pygame

from game.asset_manifest import PLAYER_SPRITES


ASSET_ROOT = Path("assets")
PLAYER_DIR = ASSET_ROOT / "sprites" / "players"
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
    """Load player animations from disk or generate placeholder frames."""
    spec = PLAYER_SPRITES[character_class]
    animations = {
        "idle": spec.idle_frames,
        "walk": spec.walk_frames,
        "attack": spec.attack_frames,
    }

    loaded: dict[str, list[pygame.Surface]] = {}
    for animation_name, expected_frames in animations.items():
        path = _sheet_path(spec.prefix, animation_name)
        if not path.exists():
            loaded[animation_name] = _placeholder_frames(
                character_class,
                spec.frame_width,
                spec.frame_height,
                expected_frames,
            )
            continue

        try:
            sheet = pygame.image.load(str(path)).convert_alpha()
            expected_size = (spec.frame_width * expected_frames, spec.frame_height)
            if sheet.get_size() != expected_size:
                raise ValueError(f"{path} has size {sheet.get_size()}, expected {expected_size}")
            loaded[animation_name] = _slice_sheet(
                sheet,
                spec.frame_width,
                spec.frame_height,
                expected_frames,
            )
        except Exception:
            loaded[animation_name] = _placeholder_frames(
                character_class,
                spec.frame_width,
                spec.frame_height,
                expected_frames,
            )

    loaded["run"] = loaded["walk"]
    return loaded

