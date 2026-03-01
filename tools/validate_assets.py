"""Validate asset files against the design manifest."""

from __future__ import annotations

from pathlib import Path
import sys

import pygame


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.asset_manifest import ANIMATED_SHEETS, PLAYER_SPRITES, STATIC_ASSETS
ASSETS_DIR = ROOT / "assets"
PLAYER_DIR = ASSETS_DIR / "sprites" / "players"


def _check_image_size(path: Path, expected_width: int, expected_height: int) -> str | None:
    if not path.exists():
        return f"missing: {path.relative_to(ROOT)} (expected {expected_width}x{expected_height})"
    try:
        image = pygame.image.load(str(path))
        actual_size = image.get_size()
    except Exception as exc:
        return f"unreadable: {path.relative_to(ROOT)} ({exc})"
    if actual_size != (expected_width, expected_height):
        return (
            f"wrong size: {path.relative_to(ROOT)} "
            f"(got {actual_size[0]}x{actual_size[1]}, expected {expected_width}x{expected_height})"
        )
    return None


def main() -> int:
    pygame.init()
    failures: list[str] = []

    for spec in PLAYER_SPRITES.values():
        failures.append(
            _check_image_size(
                PLAYER_DIR / f"{spec.prefix}_idle.png",
                spec.frame_width * spec.idle_frames,
                spec.frame_height,
            )
        )
        failures.append(
            _check_image_size(
                PLAYER_DIR / f"{spec.prefix}_walk.png",
                spec.frame_width * spec.walk_frames,
                spec.frame_height,
            )
        )
        failures.append(
            _check_image_size(
                PLAYER_DIR / f"{spec.prefix}_attack.png",
                spec.frame_width * spec.attack_frames,
                spec.frame_height,
            )
        )

    for spec in STATIC_ASSETS:
        failures.append(_check_image_size(ASSETS_DIR / spec.filename, spec.width, spec.height))

    for spec in ANIMATED_SHEETS:
        expected_width = spec.sheet_width_override or (spec.frame_width * spec.frames)
        failures.append(
            _check_image_size(
                ASSETS_DIR / spec.filename,
                expected_width,
                spec.frame_height,
            )
        )

    failures = [entry for entry in failures if entry]
    if failures:
        print("Asset validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("All assets are present and correctly sized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
