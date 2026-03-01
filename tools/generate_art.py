"""Generate stylized pixel-art draft assets from the project manifest.

Goal: produce art that is much closer to the design brief while keeping strict
filename and size contracts.
"""

from __future__ import annotations

from pathlib import Path
import math
import sys

import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.asset_manifest import ANIMATED_SHEETS, PLAYER_SPRITES, STATIC_ASSETS


ASSETS = ROOT / "assets"
PLAYER_DIR = ASSETS / "sprites" / "players"
OUTLINE = (26, 26, 26)
WHITE = (250, 250, 250)
SKIN = (244, 198, 160)
GOLD = (245, 200, 66)
CYAN = (0, 229, 255)
RED = (231, 76, 60)


def ensure_dirs() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    PLAYER_DIR.mkdir(parents=True, exist_ok=True)


def in_rect(x: int, y: int, rect: pygame.Rect) -> bool:
    return rect.left <= x < rect.right and rect.top <= y < rect.bottom


def add_pixel_outline(surface: pygame.Surface) -> None:
    w, h = surface.get_size()
    source = surface.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if source.get_at((x, y)).a != 0:
                continue
            neighbors = [
                source.get_at((x - 1, y)).a,
                source.get_at((x + 1, y)).a,
                source.get_at((x, y - 1)).a,
                source.get_at((x, y + 1)).a,
            ]
            if any(a != 0 for a in neighbors):
                surface.set_at((x, y), OUTLINE)


def add_global_outline(surface: pygame.Surface, passes: int = 2) -> None:
    for _ in range(passes):
        add_pixel_outline(surface)


def draw_eyes(surface: pygame.Surface, cx: int, cy: int, color: tuple[int, int, int], spread: int = 5) -> None:
    pygame.draw.circle(surface, color, (cx - spread, cy), 2)
    pygame.draw.circle(surface, color, (cx + spread, cy), 2)


def draw_star(surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int]) -> None:
    pygame.draw.line(surface, color, (x - 1, y), (x + 1, y), 1)
    pygame.draw.line(surface, color, (x, y - 1), (x, y + 1), 1)


def draw_player_frame(surface: pygame.Surface, prefix: str, anim: str, frame_idx: int, frame_count: int) -> None:
    w, h = surface.get_size()
    cx = w // 2
    bob = int(math.sin((frame_idx / max(frame_count, 1)) * math.tau) * (2 if anim != "idle" else 1))
    if anim == "attack":
        bob -= 1

    if prefix == "player_wizard":
        robe = (155, 89, 182)
        shadow = (108, 52, 131)
        hat = pygame.Rect(cx - 10, 8 + bob, 20, 16)
        body = [(cx, 14 + bob), (cx - 13, 38 + bob), (cx + 13, 38 + bob)]
        pygame.draw.polygon(surface, robe, body)
        pygame.draw.polygon(surface, shadow, [(cx, 16 + bob), (cx - 9, 37 + bob), (cx + 9, 37 + bob)])
        pygame.draw.polygon(surface, shadow, [(cx, 3 + bob), (cx - 8, 20 + bob), (cx + 8, 20 + bob)])
        pygame.draw.rect(surface, shadow, hat)
        draw_star(surface, cx, 14 + bob, GOLD)
        pygame.draw.rect(surface, (121, 85, 72), pygame.Rect(cx + 11, 16 + bob, 3, 22), border_radius=1)
        pygame.draw.circle(surface, CYAN if frame_idx % 2 == 0 else (0, 170, 190), (cx + 12, 15 + bob), 3)
        pygame.draw.circle(surface, SKIN, (cx, 22 + bob), 6)
        pygame.draw.circle(surface, GOLD, (cx - 3, 22 + bob), 1)
        pygame.draw.circle(surface, GOLD, (cx + 3, 22 + bob), 1)
    elif prefix == "player_knight":
        steel = (127, 140, 141)
        silver = (189, 195, 199)
        plume = RED
        pygame.draw.rect(surface, steel, pygame.Rect(cx - 14, 14 + bob, 28, 22), border_radius=4)
        pygame.draw.rect(surface, silver, pygame.Rect(cx - 12, 16 + bob, 24, 8), border_radius=3)
        pygame.draw.rect(surface, steel, pygame.Rect(cx - 9, 8 + bob, 18, 10), border_radius=4)
        pygame.draw.rect(surface, plume, pygame.Rect(cx - 2, 3 + bob, 4, 8), border_radius=2)
        pygame.draw.circle(surface, silver, (cx - 13, 27 + bob), 9)
        draw_star(surface, cx - 13, 27 + bob, GOLD)
        pygame.draw.rect(surface, plume, pygame.Rect(cx - 11, 30 + bob, 22, 6), border_radius=2)
        if anim == "attack" and frame_idx >= frame_count // 2:
            pygame.draw.circle(surface, WHITE, (cx - 20, 27 + bob), 4)
    elif prefix == "player_assassin":
        dark = (26, 58, 58)
        mid = (44, 95, 95)
        pygame.draw.polygon(surface, dark, [(cx, 13 + bob), (cx - 10, 36 + bob), (cx + 10, 36 + bob)])
        pygame.draw.rect(surface, mid, pygame.Rect(cx - 7, 15 + bob, 14, 14), border_radius=5)
        draw_eyes(surface, cx, 21 + bob, CYAN, 3)
        pygame.draw.line(surface, (189, 195, 199), (cx - 8, 10 + bob), (cx + 6, 20 + bob), 2)
        pygame.draw.line(surface, (189, 195, 199), (cx + 8, 10 + bob), (cx - 6, 20 + bob), 2)
        if anim == "attack":
            pygame.draw.line(surface, CYAN, (cx - 14, 24 + bob), (cx - 21, 20 + bob), 2)
            pygame.draw.line(surface, CYAN, (cx + 14, 24 + bob), (cx + 21, 20 + bob), 2)
    elif prefix == "player_miner":
        overalls = (46, 74, 122)
        shirt = (192, 103, 42)
        helmet = GOLD
        pygame.draw.rect(surface, shirt, pygame.Rect(cx - 12, 16 + bob, 24, 18), border_radius=6)
        pygame.draw.rect(surface, overalls, pygame.Rect(cx - 12, 20 + bob, 24, 16), border_radius=5)
        pygame.draw.rect(surface, helmet, pygame.Rect(cx - 11, 8 + bob, 22, 10), border_radius=5)
        pygame.draw.circle(surface, WHITE, (cx, 12 + bob), 2)
        pygame.draw.circle(surface, SKIN, (cx, 18 + bob), 6)
        pygame.draw.line(surface, (121, 85, 72), (cx + 10, 10 + bob), (cx + 20, 2 + bob), 3)
        pygame.draw.line(surface, (139, 157, 168), (cx + 18, 3 + bob), (cx + 24, 7 + bob), 3)
        pygame.draw.circle(surface, (231, 76, 60), (cx - 4, 20 + bob), 1)
        pygame.draw.circle(surface, (231, 76, 60), (cx + 4, 20 + bob), 1)
    elif prefix == "player_ninja":
        navy = (27, 42, 74)
        pygame.draw.rect(surface, navy, pygame.Rect(cx - 11, 13 + bob, 22, 23), border_radius=5)
        pygame.draw.circle(surface, SKIN, (cx, 18 + bob), 6)
        pygame.draw.rect(surface, GOLD, pygame.Rect(cx - 8, 12 + bob, 16, 3), border_radius=1)
        pygame.draw.rect(surface, GOLD, pygame.Rect(cx - 9, 27 + bob, 18, 3), border_radius=1)
        draw_eyes(surface, cx, 18 + bob, (60, 60, 80), 3)
        pygame.draw.circle(surface, WHITE, (cx + 14, 20 + bob), 3)
        draw_star(surface, cx + 14, 20 + bob, GOLD)
        pygame.draw.line(surface, (121, 85, 72), (cx + 6, 12 + bob), (cx + 10, 8 + bob), 2)
    elif prefix == "player_robot":
        blue = (93, 122, 138)
        dark = (44, 62, 80)
        pygame.draw.rect(surface, blue, pygame.Rect(cx - 11, 10 + bob, 22, 26), border_radius=3)
        pygame.draw.rect(surface, dark, pygame.Rect(cx - 8, 13 + bob, 16, 6), border_radius=2)
        draw_eyes(surface, cx, 16 + bob, CYAN, 3)
        pygame.draw.circle(surface, CYAN if frame_idx % 2 == 0 else (0, 170, 190), (cx, 25 + bob), 4)
        pygame.draw.rect(surface, blue, pygame.Rect(cx - 18, 20 + bob, 6, 10), border_radius=2)
        pygame.draw.rect(surface, blue, pygame.Rect(cx + 12, 20 + bob, 6, 10), border_radius=2)
        pygame.draw.line(surface, dark, (cx + 5, 8 + bob), (cx + 8, 3 + bob), 2)
        pygame.draw.circle(surface, RED if frame_idx % 2 == 0 else (160, 50, 45), (cx + 8, 3 + bob), 2)
        if anim == "attack":
            pygame.draw.circle(surface, WHITE, (cx + 20, 24 + bob), 4)

    add_global_outline(surface, 2)


def make_player_sheet(prefix: str, frame_w: int, frame_h: int, frames: int, anim: str) -> pygame.Surface:
    sheet = pygame.Surface((frame_w * frames, frame_h), pygame.SRCALPHA)
    for i in range(frames):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        draw_player_frame(frame, prefix, anim, i, frames)
        sheet.blit(frame, (i * frame_w, 0))
    return sheet


def generate_player_assets() -> None:
    for spec in PLAYER_SPRITES.values():
        for anim, count in (("idle", spec.idle_frames), ("walk", spec.walk_frames), ("attack", spec.attack_frames)):
            sheet = make_player_sheet(spec.prefix, spec.frame_width, spec.frame_height, count, anim)
            pygame.image.save(sheet, str(PLAYER_DIR / f"{spec.prefix}_{anim}.png"))


def draw_actor_frame(surface: pygame.Surface, filename: str) -> None:
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2

    if filename == "enemy_evil_ninja.png":
        pygame.draw.polygon(surface, (44, 44, 44), [(cx, 8), (cx - 12, h - 6), (cx + 12, h - 6)])
        pygame.draw.rect(surface, (90, 26, 26), pygame.Rect(cx - 9, 10, 18, 16), border_radius=4)
        draw_eyes(surface, cx, 17, (168, 255, 0), 4)
        pygame.draw.rect(surface, RED, pygame.Rect(cx - 10, 8, 20, 3))
    elif filename == "enemy_sewage_creature.png":
        pygame.draw.ellipse(surface, (107, 142, 35), pygame.Rect(3, h // 3, w - 6, h // 2))
        pygame.draw.ellipse(surface, (74, 96, 16), pygame.Rect(8, h // 2 - 3, w - 16, h // 3))
        draw_eyes(surface, cx, h // 2 - 4, (212, 224, 72), 8)
        pygame.draw.rect(surface, (60, 30, 12), pygame.Rect(cx - 9, h // 2 + 4, 18, 4), border_radius=1)
    elif filename == "enemy_zombie.png":
        pygame.draw.rect(surface, (122, 171, 138), pygame.Rect(cx - 10, 10, 20, 26), border_radius=5)
        pygame.draw.rect(surface, (141, 110, 74), pygame.Rect(cx - 9, 22, 18, 13), border_radius=3)
        draw_eyes(surface, cx, 16, (232, 224, 90), 3)
        pygame.draw.rect(surface, (122, 171, 138), pygame.Rect(cx - 16, 20, 8, 7), border_radius=2)
        pygame.draw.rect(surface, (122, 171, 138), pygame.Rect(cx + 8, 20, 8, 7), border_radius=2)
    elif filename == "enemy_land_octopus.png":
        pygame.draw.ellipse(surface, (232, 114, 58), pygame.Rect(cx - 13, 6, 26, 18))
        for i in range(6):
            x = 4 + i * 9
            pygame.draw.ellipse(surface, (232, 114, 58), pygame.Rect(x, 20 + (i % 2), 9, 18))
            pygame.draw.circle(surface, (244, 160, 184), (x + 4, 33), 2)
        pygame.draw.circle(surface, (245, 230, 66), (cx - 7, 14), 4)
        pygame.draw.circle(surface, (245, 230, 66), (cx + 7, 14), 4)
    elif filename == "enemy_little_devil.png":
        pygame.draw.circle(surface, RED, (cx, cy), min(w, h) // 3)
        pygame.draw.polygon(surface, (107, 26, 26), [(cx - 7, 8), (cx - 3, 14), (cx - 10, 14)])
        pygame.draw.polygon(surface, (107, 26, 26), [(cx + 7, 8), (cx + 3, 14), (cx + 10, 14)])
        draw_eyes(surface, cx, cy - 2, (243, 156, 18), 4)
        pygame.draw.polygon(surface, (192, 57, 43), [(cx - 13, cy), (cx - 20, cy - 5), (cx - 19, cy + 6)])
        pygame.draw.polygon(surface, (192, 57, 43), [(cx + 13, cy), (cx + 20, cy - 5), (cx + 19, cy + 6)])
    elif filename == "enemy_skeleton.png":
        pygame.draw.circle(surface, (232, 220, 200), (cx, 11), 8)
        pygame.draw.rect(surface, (232, 220, 200), pygame.Rect(cx - 7, 18, 14, 18), border_radius=4)
        for i in range(4):
            pygame.draw.line(surface, (196, 168, 130), (cx - 5, 21 + i * 3), (cx + 5, 21 + i * 3), 1)
        draw_eyes(surface, cx, 11, (168, 216, 234), 3)
        pygame.draw.line(surface, (158, 74, 26), (cx + 7, 22), (cx + 16, 16), 3)
    elif filename == "enemy_poisonous_mushroom.png":
        pygame.draw.circle(surface, (169, 53, 96), (cx, 15), 14)
        pygame.draw.rect(surface, (250, 240, 220), pygame.Rect(cx - 8, 19, 16, 14), border_radius=4)
        for dx in (-7, -2, 4):
            pygame.draw.circle(surface, (215, 189, 226), (cx + dx, 13), 2)
        draw_eyes(surface, cx, 18, (62, 31, 0), 3)
    elif filename == "enemy_stonehead_turtle.png":
        pygame.draw.ellipse(surface, (139, 157, 168), pygame.Rect(3, 8, w - 6, h - 12))
        for r in range(6, w - 6, 10):
            pygame.draw.line(surface, (90, 107, 116), (r, 12), (r - 3, h - 10), 1)
        pygame.draw.circle(surface, (107, 142, 90), (cx, h - 9), 5)
        pygame.draw.line(surface, (26, 26, 26), (cx - 3, h - 10), (cx + 3, h - 10), 1)
    elif filename == "boss_grimrak.png":
        pygame.draw.rect(surface, (90, 107, 116), pygame.Rect(14, 10, w - 28, h - 14), border_radius=8)
        pygame.draw.rect(surface, (139, 157, 168), pygame.Rect(20, 18, w - 40, h - 20), border_radius=6)
        pygame.draw.rect(surface, (90, 107, 116), pygame.Rect(5, 30, 16, 30), border_radius=4)
        pygame.draw.rect(surface, (90, 107, 116), pygame.Rect(w - 21, 30, 16, 30), border_radius=4)
        pygame.draw.circle(surface, (26, 188, 156), (cx, cy), 8)
        pygame.draw.circle(surface, GOLD, (cx, cy), 4)
        draw_eyes(surface, cx, 22, RED, 9)
    elif filename == "boss_zara.png":
        pygame.draw.polygon(surface, (93, 109, 126), [(cx, 6), (cx - 16, 48), (cx + 16, 48)])
        pygame.draw.polygon(surface, (46, 64, 87), [(cx, 12), (cx - 10, 48), (cx + 10, 48)])
        pygame.draw.circle(surface, SKIN, (cx, 20), 7)
        draw_eyes(surface, cx, 20, GOLD, 3)
        pygame.draw.line(surface, (91, 200, 245), (cx + 10, 16), (cx + 19, 7), 3)
        pygame.draw.circle(surface, CYAN, (cx + 19, 7), 4)
    elif filename == "boss_ninja_land_eel.png":
        points = [(8, 42), (28, 34), (52, 30), (75, 33), (95, 26), (112, 18), (122, 13)]
        pygame.draw.lines(surface, (26, 58, 138), False, points, 14)
        pygame.draw.lines(surface, (58, 106, 191), False, points, 8)
        pygame.draw.rect(surface, OUTLINE, pygame.Rect(103, 10, 20, 9), border_radius=4)
        pygame.draw.line(surface, RED, (103, 14), (123, 14), 1)
        pygame.draw.circle(surface, GOLD, (117, 13), 3)
        pygame.draw.circle(surface, (26, 188, 156), (86, 28), 4)
        pygame.draw.line(surface, (93, 109, 126), (100, 24), (120, 30), 5)
        pygame.draw.line(surface, (255, 245, 157), (101, 24), (121, 30), 2)
    elif filename == "npc_villager.png":
        pygame.draw.rect(surface, (230, 126, 34), pygame.Rect(cx - 10, 14, 20, 22), border_radius=5)
        pygame.draw.circle(surface, SKIN, (cx, 16), 7)
        pygame.draw.rect(surface, (121, 85, 72), pygame.Rect(cx - 9, 26, 18, 3))
        pygame.draw.circle(surface, (123, 79, 46), (cx, 10), 6)
    elif filename == "npc_shopkeeper.png":
        pygame.draw.rect(surface, (250, 240, 220), pygame.Rect(cx - 10, 16, 20, 20), border_radius=5)
        pygame.draw.rect(surface, (121, 85, 72), pygame.Rect(cx - 7, 5, 14, 10), border_radius=2)
        pygame.draw.circle(surface, SKIN, (cx, 16), 6)
        pygame.draw.arc(surface, (78, 52, 46), pygame.Rect(cx - 5, 17, 10, 6), math.pi, 2 * math.pi, 2)
        pygame.draw.circle(surface, GOLD, (cx + 6, 28), 2)
    elif filename == "npc_companion_knight.png":
        pygame.draw.rect(surface, (183, 134, 11), pygame.Rect(cx - 12, 12, 24, 24), border_radius=4)
        pygame.draw.rect(surface, (123, 90, 8), pygame.Rect(cx - 8, 8, 16, 8), border_radius=3)
        pygame.draw.rect(surface, (91, 200, 245), pygame.Rect(cx - 2, 2, 4, 8), border_radius=2)
        pygame.draw.circle(surface, (183, 134, 11), (cx - 13, 25), 8)
        draw_star(surface, cx - 13, 25, (26, 188, 156))
    elif filename == "npc_companion_wizard.png":
        pygame.draw.polygon(surface, (91, 200, 245), [(cx, 12), (cx - 12, 38), (cx + 12, 38)])
        pygame.draw.polygon(surface, (21, 101, 192), [(cx, 4), (cx - 7, 20), (cx + 7, 20)])
        pygame.draw.circle(surface, SKIN, (cx, 19), 6)
        pygame.draw.line(surface, (21, 101, 192), (cx + 10, 16), (cx + 18, 8), 2)
        pygame.draw.circle(surface, (26, 188, 156), (cx + 18, 8), 3)
    elif filename == "item_health_potion.png":
        pygame.draw.ellipse(surface, (174, 229, 245), pygame.Rect(cx - 5, 3, 10, 12))
        pygame.draw.rect(surface, (121, 85, 72), pygame.Rect(cx - 2, 1, 4, 3))
        pygame.draw.rect(surface, RED, pygame.Rect(cx - 4, 8, 8, 5), border_radius=2)
        pygame.draw.circle(surface, WHITE, (cx + 2, 6), 1)
    elif filename == "item_energy_potion.png":
        pygame.draw.ellipse(surface, (174, 229, 245), pygame.Rect(cx - 5, 3, 10, 12))
        pygame.draw.rect(surface, (44, 62, 80), pygame.Rect(cx - 2, 1, 4, 3))
        pygame.draw.rect(surface, CYAN, pygame.Rect(cx - 4, 8, 8, 5), border_radius=2)
        pygame.draw.line(surface, WHITE, (cx - 1, 8), (cx + 2, 11), 1)
    elif filename == "item_sword.png":
        pygame.draw.line(surface, (189, 195, 199), (4, h - 6), (w - 5, 5), 3)
        pygame.draw.line(surface, WHITE, (5, h - 6), (w - 6, 5), 1)
        pygame.draw.line(surface, GOLD, (10, h - 9), (15, h - 4), 3)
    elif filename == "item_armor_shield.png":
        pygame.draw.circle(surface, (189, 195, 199), (cx, cy), min(w, h) // 2 - 3)
        pygame.draw.circle(surface, GOLD, (cx, cy), min(w, h) // 2 - 3, 2)
        draw_star(surface, cx, cy, RED)

    add_global_outline(surface, 2)


def draw_tile(surface: pygame.Surface, filename: str) -> None:
    w, h = surface.get_size()
    if filename == "tile_grass.png":
        surface.fill((76, 175, 80))
        for x in range(3, w, 7):
            pygame.draw.line(surface, (129, 199, 132), (x, 8 + (x % 3)), (x + 2, 4 + (x % 3)), 1)
            pygame.draw.line(surface, (56, 142, 60), (x, 9 + (x % 3)), (x - 2, 6 + (x % 3)), 1)
    elif filename == "tile_grass_alt.png":
        surface.fill((66, 165, 70))
        for x in range(4, w, 6):
            pygame.draw.line(surface, (129, 199, 132), (x, 10), (x + 2, 6), 1)
            pygame.draw.line(surface, (56, 142, 60), (x, 10), (x - 2, 7), 1)
    elif filename == "tile_dirt.png":
        surface.fill((123, 94, 58))
        for y in range(2, h, 7):
            pygame.draw.line(surface, (90, 62, 32), (0, y), (w, y + 1), 1)
        for x in range(2, w, 6):
            pygame.draw.circle(surface, (139, 157, 168), (x, (x * 5) % h), 1)
    elif filename == "tile_magic_glow.png":
        surface.fill((139, 157, 168))
        pygame.draw.circle(surface, (155, 89, 182), (w // 2, h // 2), 9)
        pygame.draw.circle(surface, CYAN, (w // 2, h // 2), 6, 1)
        pygame.draw.line(surface, (90, 107, 116), (5, 5), (w - 6, h - 6), 1)
    elif filename == "tile_wall.png":
        surface.fill((139, 157, 168))
        for y in range(0, h, 8):
            offset = 4 if (y // 8) % 2 else 0
            for x in range(-offset, w, 8):
                pygame.draw.rect(surface, (90, 107, 116), pygame.Rect(x, y, 8, 8), 1)
    elif filename == "tile_tree_top.png":
        surface.fill((0, 0, 0, 0))
        pygame.draw.circle(surface, (76, 175, 80), (w // 2, h // 2), 14)
        pygame.draw.circle(surface, (46, 125, 50), (w // 2 + 4, h // 2 + 3), 10)
    elif filename == "tile_tree_trunk.png":
        surface.fill((0, 0, 0, 0))
        pygame.draw.ellipse(surface, (121, 85, 72), pygame.Rect(w // 2 - 6, h // 2 - 6, 12, 12))
        pygame.draw.line(surface, (161, 136, 127), (w // 2, h // 2 - 5), (w // 2, h // 2 + 5), 1)
    elif filename == "tile_bridge.png":
        surface.fill((196, 160, 99))
        for y in range(0, h, 8):
            pygame.draw.rect(surface, (196, 160, 99), pygame.Rect(0, y, w, 7))
            pygame.draw.line(surface, (121, 85, 72), (0, y), (w, y), 1)
            pygame.draw.circle(surface, (44, 62, 80), (4, y + 3), 1)
            pygame.draw.circle(surface, (44, 62, 80), (w - 5, y + 3), 1)


def generate_static_assets() -> None:
    for spec in STATIC_ASSETS:
        surface = pygame.Surface((spec.width, spec.height), pygame.SRCALPHA)
        if spec.filename.startswith("tile_"):
            draw_tile(surface, spec.filename)
        else:
            draw_actor_frame(surface, spec.filename)
        if spec.filename.startswith("tile_"):
            add_global_outline(surface, 1)
        pygame.image.save(surface, str(ASSETS / spec.filename))


def draw_animated_frame(surface: pygame.Surface, filename: str, i: int, frames: int) -> None:
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2

    if filename == "tile_water.png":
        surface.fill((21, 101, 192))
        phase = i / max(frames, 1)
        pygame.draw.ellipse(surface, (91, 200, 245), pygame.Rect(3 + int(4 * math.sin(phase * math.tau)), 8, 16, 8), 1)
        pygame.draw.ellipse(surface, (129, 212, 250), pygame.Rect(14 + int(3 * math.cos(phase * math.tau)), 18, 12, 6), 1)
        pygame.draw.circle(surface, WHITE, (6 + i * 2, 6 + (i % 2)), 1)
    elif filename == "world_respawn_point.png":
        r = 8 + (i % 3)
        pygame.draw.circle(surface, (26, 188, 156), (cx, cy), r)
        pygame.draw.circle(surface, CYAN, (cx, cy), max(2, r - 4))
        draw_star(surface, cx, cy, WHITE)
    elif filename == "item_magical_shard.png":
        swing = (-1, 0, 1, 0)[i % 4]
        pts = [(cx, 2 + swing), (w - 4, cy), (cx, h - 3 - swing), (4, cy)]
        pygame.draw.polygon(surface, (26, 188, 156), pts)
        pygame.draw.polygon(surface, (0, 229, 255), [(cx, 3), (w - 5, cy), (cx, cy), (5, cy)], 1)
        pygame.draw.polygon(surface, OUTLINE, pts, 1)
        pygame.draw.circle(surface, WHITE, (cx + 3, 4), 1)
    elif filename == "world_portal_gate.png":
        frame = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(surface, (90, 107, 116), frame, border_radius=5)
        pygame.draw.rect(surface, GOLD, pygame.Rect(2, 2, w - 4, h - 4), 2, border_radius=5)
        portal = pygame.Rect(w // 2 - 24, 24, 48, 80)
        pygame.draw.ellipse(surface, (155, 89, 182), portal)
        ring = portal.inflate(-10 + (i % 4), -10 + (i % 4))
        pygame.draw.ellipse(surface, CYAN, ring, 3)
        pygame.draw.circle(surface, WHITE, (cx, cy + 2), 5 - (i % 2))
        pygame.draw.line(surface, RED, (10, 20 + i), (18, 30 + i), 1)
        pygame.draw.line(surface, RED, (w - 10, 36 + i), (w - 18, 44 + i), 1)


def generate_animated_sheets() -> None:
    for spec in ANIMATED_SHEETS:
        sheet_w = spec.sheet_width_override or (spec.frame_width * spec.frames)
        sheet = pygame.Surface((sheet_w, spec.frame_height), pygame.SRCALPHA)
        for i in range(spec.frames):
            frame = pygame.Surface((spec.frame_width, spec.frame_height), pygame.SRCALPHA)
            draw_animated_frame(frame, spec.filename, i, spec.frames)
            add_global_outline(frame, 1)
            sheet.blit(frame, (i * spec.frame_width, 0))
        pygame.image.save(sheet, str(ASSETS / spec.filename))


def main() -> int:
    pygame.init()
    ensure_dirs()
    generate_player_assets()
    generate_static_assets()
    generate_animated_sheets()
    print("Upgraded draft art generated in assets/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
