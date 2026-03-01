"""Second-pass stylization for game art.

Applies stronger, category-specific polish:
- Characters/enemies/bosses/items: readability, rim light, punchier colors
- Environment tiles/world sheets: cleaner gradients, soft glow, less harsh pixels

All files are edited in place and keep original dimensions.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pygame


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.asset_manifest import ANIMATED_SHEETS, PLAYER_SPRITES, STATIC_ASSETS

ASSETS_DIR = ROOT / "assets"
PLAYER_DIR = ASSETS_DIR / "sprites" / "players"


def _to_arrays(surface: pygame.Surface) -> tuple[np.ndarray, np.ndarray]:
    rgb = pygame.surfarray.array3d(surface).astype(np.float32)
    alpha = pygame.surfarray.array_alpha(surface).astype(np.float32)
    return rgb, alpha


def _from_arrays(rgb: np.ndarray, alpha: np.ndarray) -> pygame.Surface:
    w, h = rgb.shape[:2]
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(out, np.clip(rgb, 0.0, 255.0).astype(np.uint8))
    a = pygame.surfarray.pixels_alpha(out)
    a[:, :] = np.clip(alpha, 0.0, 255.0).astype(np.uint8)
    del a
    return out


def _blur(surface: pygame.Surface, scale: int = 2) -> pygame.Surface:
    w, h = surface.get_size()
    sw, sh = max(1, w // scale), max(1, h // scale)
    down = pygame.transform.smoothscale(surface, (sw, sh))
    return pygame.transform.smoothscale(down, (w, h))


def _rim_from_alpha(alpha: np.ndarray, intensity: float = 45.0) -> np.ndarray:
    # Alpha-space rim approximation: blur alpha and subtract original.
    arr = alpha / 255.0
    pad = np.pad(arr, ((1, 1), (1, 1)), mode="edge")
    # 3x3 blur kernel.
    blur = (
        pad[:-2, :-2] + pad[:-2, 1:-1] + pad[:-2, 2:]
        + pad[1:-1, :-2] + pad[1:-1, 1:-1] + pad[1:-1, 2:]
        + pad[2:, :-2] + pad[2:, 1:-1] + pad[2:, 2:]
    ) / 9.0
    rim = np.clip(blur - arr, 0.0, 1.0) * intensity
    return rim


def _grade_sprite(surface: pygame.Surface, saturation: float, contrast: float, bloom: float, rim: float) -> pygame.Surface:
    w, h = surface.get_size()
    hi = pygame.transform.smoothscale(surface, (w * 4, h * 4))
    hi_blur = _blur(hi, scale=2)

    rgb, alpha = _to_arrays(hi)
    blur_rgb, _ = _to_arrays(hi_blur)

    # Local contrast (unsharp style)
    rgb = np.clip(rgb * (1.0 + contrast) - blur_rgb * contrast, 0.0, 255.0)

    # Saturation
    lum = rgb.mean(axis=2, keepdims=True)
    rgb = lum + (rgb - lum) * saturation

    # Bloom from bright colors
    bright = np.maximum(np.maximum(rgb[:, :, 0], rgb[:, :, 1]), rgb[:, :, 2])
    glow_mask = np.clip((bright - 150.0) / 105.0, 0.0, 1.0) * bloom
    rgb[:, :, 0] = np.clip(rgb[:, :, 0] + glow_mask * 15.0, 0.0, 255.0)
    rgb[:, :, 1] = np.clip(rgb[:, :, 1] + glow_mask * 22.0, 0.0, 255.0)
    rgb[:, :, 2] = np.clip(rgb[:, :, 2] + glow_mask * 30.0, 0.0, 255.0)

    # Rim light for silhouette readability.
    rim_mask = _rim_from_alpha(alpha, intensity=rim)
    rgb[:, :, 0] = np.clip(rgb[:, :, 0] + rim_mask * 0.7, 0.0, 255.0)
    rgb[:, :, 1] = np.clip(rgb[:, :, 1] + rim_mask * 0.9, 0.0, 255.0)
    rgb[:, :, 2] = np.clip(rgb[:, :, 2] + rim_mask * 1.1, 0.0, 255.0)

    # Gentle global contrast
    rgb = np.clip((rgb - 128.0) * 1.04 + 128.0, 0.0, 255.0)

    out_hi = _from_arrays(rgb, alpha)
    out = pygame.transform.smoothscale(out_hi, (w, h))
    return out


def _slice_sheet(sheet: pygame.Surface, frame_w: int, frame_h: int, frames: int) -> list[pygame.Surface]:
    out: list[pygame.Surface] = []
    for i in range(frames):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(i * frame_w, 0, frame_w, frame_h))
        out.append(frame)
    return out


def _assemble_sheet(frames: list[pygame.Surface], frame_w: int, frame_h: int) -> pygame.Surface:
    sheet = pygame.Surface((frame_w * len(frames), frame_h), pygame.SRCALPHA)
    for i, f in enumerate(frames):
        sheet.blit(f, (i * frame_w, 0))
    return sheet


def _process_player_sheets() -> int:
    count = 0
    for spec in PLAYER_SPRITES.values():
        for anim, frames in (("idle", spec.idle_frames), ("walk", spec.walk_frames), ("attack", spec.attack_frames)):
            path = PLAYER_DIR / f"{spec.prefix}_{anim}.png"
            sheet = pygame.image.load(str(path)).convert_alpha()
            split = _slice_sheet(sheet, spec.frame_width, spec.frame_height, frames)
            polished = [
                _grade_sprite(f, saturation=1.22, contrast=0.24, bloom=0.28, rim=46.0)
                for f in split
            ]
            merged = _assemble_sheet(polished, spec.frame_width, spec.frame_height)
            pygame.image.save(merged, str(path))
            count += 1
    return count


def _process_static_assets() -> int:
    count = 0
    for spec in STATIC_ASSETS:
        path = ASSETS_DIR / spec.filename
        img = pygame.image.load(str(path)).convert_alpha()
        if spec.filename.startswith("tile_"):
            out = _grade_sprite(img, saturation=1.12, contrast=0.14, bloom=0.16, rim=26.0)
        elif spec.filename.startswith("boss_"):
            out = _grade_sprite(img, saturation=1.25, contrast=0.26, bloom=0.34, rim=52.0)
        elif spec.filename.startswith("enemy_"):
            out = _grade_sprite(img, saturation=1.20, contrast=0.22, bloom=0.26, rim=44.0)
        elif spec.filename.startswith("npc_"):
            out = _grade_sprite(img, saturation=1.18, contrast=0.20, bloom=0.24, rim=40.0)
        elif spec.filename.startswith("item_"):
            out = _grade_sprite(img, saturation=1.28, contrast=0.24, bloom=0.36, rim=54.0)
        else:
            out = _grade_sprite(img, saturation=1.16, contrast=0.18, bloom=0.20, rim=34.0)
        pygame.image.save(out, str(path))
        count += 1
    return count


def _process_animated_sheets() -> int:
    count = 0
    for spec in ANIMATED_SHEETS:
        path = ASSETS_DIR / spec.filename
        sheet = pygame.image.load(str(path)).convert_alpha()
        frames = _slice_sheet(sheet, spec.frame_width, spec.frame_height, spec.frames)

        if spec.filename == "world_portal_gate.png":
            tuned = [_grade_sprite(f, saturation=1.26, contrast=0.25, bloom=0.40, rim=50.0) for f in frames]
        elif spec.filename == "item_magical_shard.png":
            tuned = [_grade_sprite(f, saturation=1.30, contrast=0.23, bloom=0.44, rim=60.0) for f in frames]
        elif spec.filename == "tile_water.png":
            tuned = [_grade_sprite(f, saturation=1.18, contrast=0.18, bloom=0.30, rim=28.0) for f in frames]
        else:
            tuned = [_grade_sprite(f, saturation=1.16, contrast=0.18, bloom=0.26, rim=34.0) for f in frames]

        merged = _assemble_sheet(tuned, spec.frame_width, spec.frame_height)
        pygame.image.save(merged, str(path))
        count += 1
    return count


def _refresh_key_and_big_potion() -> int:
    # Re-run the premium generated versions so these remain visually important.
    enhancer = ROOT / "tools" / "enhance_art.py"
    if enhancer.exists():
        # Import lazily to reuse drawing routines without shelling out.
        import importlib.util

        mod_spec = importlib.util.spec_from_file_location("enhance_art", str(enhancer))
        assert mod_spec is not None and mod_spec.loader is not None
        mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mod)

        key_img = mod._draw_fancy_portal_key()
        key_img = _grade_sprite(key_img, saturation=1.32, contrast=0.24, bloom=0.48, rim=62.0)
        pygame.image.save(key_img, str(ASSETS_DIR / "item_portal_key.png"))

        potion_img = mod._draw_big_health_potion()
        potion_img = _grade_sprite(potion_img, saturation=1.24, contrast=0.20, bloom=0.40, rim=56.0)
        pygame.image.save(potion_img, str(ASSETS_DIR / "item_big_health_potion.png"))
        return 2

    return 0


def main() -> int:
    pygame.init()
    pygame.display.set_mode((1, 1))

    player_count = _process_player_sheets()
    static_count = _process_static_assets()
    animated_count = _process_animated_sheets()
    item_count = _refresh_key_and_big_potion()

    total = player_count + static_count + animated_count + item_count
    print(
        f"Pass-2 stylization complete: {total} files "
        f"({player_count} player sheets, {static_count} static assets, "
        f"{animated_count} animated sheets, {item_count} key/potion specials)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
