"""Polish generated game art to feel smoother and more modern.

This pass keeps all original filename/size contracts intact while reducing
blocky edges and boosting color/readability for small sprites.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pygame


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ASSETS_DIR = ROOT / "assets"
PLAYER_DIR = ASSETS_DIR / "sprites" / "players"


def _blur_surface(surface: pygame.Surface, divisor: int = 2) -> pygame.Surface:
    """Fast blur via downscale/upscale."""
    w, h = surface.get_size()
    small_w = max(1, w // divisor)
    small_h = max(1, h // divisor)
    small = pygame.transform.smoothscale(surface, (small_w, small_h))
    return pygame.transform.smoothscale(small, (w, h))


def _enhance_surface(surface: pygame.Surface) -> pygame.Surface:
    """Apply anti-pixelation and color polish while preserving transparency."""
    w, h = surface.get_size()
    hi = pygame.transform.smoothscale(surface, (w * 4, h * 4))
    blur = _blur_surface(hi, divisor=2)

    rgb = pygame.surfarray.array3d(hi).astype(np.float32)
    alpha = pygame.surfarray.array_alpha(hi).astype(np.float32)
    blur_rgb = pygame.surfarray.array3d(blur).astype(np.float32)
    blur_alpha = pygame.surfarray.array_alpha(blur).astype(np.float32)

    # Unsharp mask for cleaner tiny details.
    rgb = np.clip(rgb * 1.28 - blur_rgb * 0.28, 0.0, 255.0)

    # Slight saturation + contrast lift for vibrant "hero" readability.
    lum = rgb.mean(axis=2, keepdims=True)
    rgb = lum + (rgb - lum) * 1.18
    rgb = np.clip((rgb - 128.0) * 1.05 + 128.0, 0.0, 255.0)

    # Soft outer rim light from alpha falloff.
    rim = np.clip(blur_alpha - alpha, 0.0, 90.0) / 90.0
    rgb[:, :, 0] = np.clip(rgb[:, :, 0] + rim * 30.0, 0.0, 255.0)
    rgb[:, :, 1] = np.clip(rgb[:, :, 1] + rim * 38.0, 0.0, 255.0)
    rgb[:, :, 2] = np.clip(rgb[:, :, 2] + rim * 46.0, 0.0, 255.0)

    out = pygame.Surface((w * 4, h * 4), pygame.SRCALPHA)
    pygame.surfarray.blit_array(out, rgb.astype(np.uint8))
    alpha_view = pygame.surfarray.pixels_alpha(out)
    alpha_view[:, :] = np.clip(alpha, 0.0, 255.0).astype(np.uint8)
    del alpha_view

    return pygame.transform.smoothscale(out, (w, h))


def _iter_png_paths() -> list[Path]:
    paths = list(ASSETS_DIR.glob("*.png")) + list(PLAYER_DIR.glob("*.png"))
    return sorted(p for p in paths if p.is_file())


def _draw_fancy_portal_key() -> pygame.Surface:
    """Draw a high-detail 20x20 portal key with glow and gem accents."""
    size = 240
    s = pygame.Surface((size, size), pygame.SRCALPHA)

    center = (92, 100)

    # Aura glow layers.
    pygame.draw.circle(s, (80, 220, 255, 26), center, 86)
    pygame.draw.circle(s, (255, 220, 120, 32), center, 70)

    # Bow ring + core.
    pygame.draw.circle(s, (122, 77, 16, 255), center, 56)
    pygame.draw.circle(s, (245, 191, 64, 255), center, 50)
    pygame.draw.circle(s, (86, 158, 220, 255), center, 21)
    pygame.draw.circle(s, (179, 240, 255, 255), center, 10)
    pygame.draw.circle(s, (255, 245, 205, 180), (86, 89), 7)

    # Shaft.
    pygame.draw.rect(s, (122, 77, 16, 255), pygame.Rect(102, 90, 108, 34), border_radius=17)
    pygame.draw.rect(s, (245, 191, 64, 255), pygame.Rect(108, 95, 96, 24), border_radius=12)
    pygame.draw.line(s, (255, 230, 150, 210), (112, 100), (198, 100), 4)

    # Teeth.
    pygame.draw.polygon(s, (122, 77, 16, 255), [(174, 124), (174, 175), (193, 175), (193, 124)])
    pygame.draw.polygon(s, (245, 191, 64, 255), [(178, 126), (178, 169), (189, 169), (189, 126)])
    pygame.draw.polygon(s, (122, 77, 16, 255), [(198, 124), (198, 156), (218, 156), (218, 124)])
    pygame.draw.polygon(s, (245, 191, 64, 255), [(202, 126), (202, 150), (214, 150), (214, 126)])

    # Sparkles for "important drop" readability.
    for x, y, r in ((66, 42, 11), (126, 54, 9), (226, 92, 8), (212, 178, 9)):
        pygame.draw.line(s, (205, 250, 255, 220), (x - r, y), (x + r, y), 4)
        pygame.draw.line(s, (205, 250, 255, 220), (x, y - r), (x, y + r), 4)

    # Thin dark outline pass helps legibility on bright backgrounds.
    outline = pygame.Surface((size, size), pygame.SRCALPHA)
    alpha = pygame.surfarray.array_alpha(s)
    out_a = pygame.surfarray.pixels_alpha(outline)
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        shifted = np.zeros_like(alpha)
        src_x0 = max(0, -ox)
        src_x1 = min(alpha.shape[0], alpha.shape[0] - ox)
        src_y0 = max(0, -oy)
        src_y1 = min(alpha.shape[1], alpha.shape[1] - oy)
        dst_x0 = max(0, ox)
        dst_x1 = min(alpha.shape[0], alpha.shape[0] + ox)
        dst_y0 = max(0, oy)
        dst_y1 = min(alpha.shape[1], alpha.shape[1] + oy)
        shifted[dst_x0:dst_x1, dst_y0:dst_y1] = alpha[src_x0:src_x1, src_y0:src_y1]
        out_a[:, :] = np.maximum(out_a, (shifted > 0).astype(np.uint8) * 150)
    del out_a
    outline.fill((23, 20, 15, 0), special_flags=pygame.BLEND_RGBA_MULT)
    outline.fill((23, 20, 15, 145), special_flags=pygame.BLEND_RGBA_ADD)
    s.blit(outline, (0, 0))

    return pygame.transform.smoothscale(s, (20, 20))


def _draw_big_health_potion() -> pygame.Surface:
    """Draw a dedicated 20x20 big heal potion used for mini-boss rewards."""
    size = 200
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    pygame.draw.circle(s, (255, 220, 100, 35), (cx, cy + 20), 72)
    pygame.draw.ellipse(s, (92, 173, 218, 200), pygame.Rect(cx - 46, cy - 44, 92, 108))
    pygame.draw.ellipse(s, (173, 229, 255, 210), pygame.Rect(cx - 40, cy - 38, 80, 96), 6)
    pygame.draw.rect(s, (130, 96, 32, 255), pygame.Rect(cx - 18, cy - 60, 36, 16), border_radius=6)
    pygame.draw.rect(s, (245, 191, 64, 255), pygame.Rect(cx - 14, cy - 57, 28, 10), border_radius=4)
    pygame.draw.ellipse(s, (255, 191, 70, 220), pygame.Rect(cx - 34, cy - 6, 68, 54))
    pygame.draw.ellipse(s, (255, 230, 150, 160), pygame.Rect(cx - 24, cy + 2, 48, 36))
    pygame.draw.line(s, (255, 248, 210, 220), (cx - 18, cy - 4), (cx - 4, cy + 20), 6)

    for x, y, r in ((cx - 50, cy - 10, 8), (cx + 48, cy - 4, 7), (cx + 8, cy + 64, 6)):
        pygame.draw.line(s, (255, 245, 210, 210), (x - r, y), (x + r, y), 3)
        pygame.draw.line(s, (255, 245, 210, 210), (x, y - r), (x, y + r), 3)

    return pygame.transform.smoothscale(s, (20, 20))


def main() -> int:
    pygame.init()
    pygame.display.set_mode((1, 1))

    paths = _iter_png_paths()
    for path in paths:
        src = pygame.image.load(str(path)).convert_alpha()
        polished = _enhance_surface(src)
        pygame.image.save(polished, str(path))

    portal_key = _draw_fancy_portal_key()
    pygame.image.save(portal_key, str(ASSETS_DIR / "item_portal_key.png"))

    big_potion = _draw_big_health_potion()
    pygame.image.save(big_potion, str(ASSETS_DIR / "item_big_health_potion.png"))

    print(f"Polished {len(paths)} images and generated item_portal_key.png + item_big_health_potion.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
