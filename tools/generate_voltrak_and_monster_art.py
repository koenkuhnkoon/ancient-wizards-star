"""Generate art from:
1) art_brief_voltrak_effects.md
2) art_brief_monster_attacks.md
"""

from __future__ import annotations

from pathlib import Path
import math

import pygame


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

OUTLINE = (20, 20, 20, 255)


def add_outline(surface: pygame.Surface, passes: int = 1) -> None:
    for _ in range(passes):
        src = surface.copy()
        w, h = surface.get_size()
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if src.get_at((x, y)).a != 0:
                    continue
                if any(src.get_at((nx, ny)).a > 0 for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
                    surface.set_at((x, y), OUTLINE)


def save(surface: pygame.Surface, filename: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(ASSETS / filename))


def draw_base_enemy(kind: str, w: int, h: int, phase: float, mode: str) -> pygame.Surface:
    """Draw one stylized frame for enemy/boss."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    bob = int(math.sin(phase * math.tau) * (1.5 if mode == "walk" else 0.8))

    if kind == "enemy_evil_ninja":
        pygame.draw.polygon(s, (26, 26, 46, 255), [(cx, 5 + bob), (cx - 12, h - 6 + bob), (cx + 12, h - 6 + bob)])
        pygame.draw.rect(s, (128, 34, 34, 255), pygame.Rect(cx - 10, 10 + bob, 20, 4), border_radius=1)
        pygame.draw.rect(s, (40, 42, 60, 255), pygame.Rect(cx - 8, 14 + bob, 16, 12), border_radius=3)
        pygame.draw.circle(s, (168, 255, 90, 255), (cx - 3, 18 + bob), 1)
        pygame.draw.circle(s, (168, 255, 90, 255), (cx + 3, 18 + bob), 1)
    elif kind == "enemy_skeleton":
        pygame.draw.circle(s, (245, 240, 220, 255), (cx, 12 + bob), 8)
        pygame.draw.rect(s, (245, 240, 220, 255), pygame.Rect(cx - 7, 20 + bob, 14, 18), border_radius=3)
        for i in range(4):
            pygame.draw.line(s, (200, 178, 148, 255), (cx - 5, 23 + i * 3 + bob), (cx + 5, 23 + i * 3 + bob), 1)
        pygame.draw.circle(s, (22, 22, 22, 255), (cx - 3, 11 + bob), 2)
        pygame.draw.circle(s, (22, 22, 22, 255), (cx + 3, 11 + bob), 2)
    elif kind == "enemy_zombie":
        pygame.draw.rect(s, (122, 156, 94, 255), pygame.Rect(cx - 10, 9 + bob, 20, 26), border_radius=5)
        pygame.draw.rect(s, (130, 88, 64, 255), pygame.Rect(cx - 9, 22 + bob, 18, 12), border_radius=3)
        pygame.draw.rect(s, (122, 156, 94, 255), pygame.Rect(cx - 16, 20 + bob, 8, 7), border_radius=2)
        pygame.draw.rect(s, (122, 156, 94, 255), pygame.Rect(cx + 8, 20 + bob, 8, 7), border_radius=2)
        pygame.draw.circle(s, (234, 214, 110, 255), (cx - 3, 16 + bob), 1)
        pygame.draw.circle(s, (234, 214, 110, 255), (cx + 3, 16 + bob), 1)
    elif kind == "enemy_sewage_creature":
        sway = int(math.sin(phase * math.tau) * 3)
        pygame.draw.ellipse(s, (92, 122, 62, 255), pygame.Rect(2 + sway, h // 3 + bob, w - 4, h // 2))
        pygame.draw.ellipse(s, (70, 95, 40, 255), pygame.Rect(7 + sway, h // 2 - 3 + bob, w - 14, h // 3))
        pygame.draw.circle(s, (212, 224, 98, 255), (cx - 7 + sway, h // 2 - 2 + bob), 2)
        pygame.draw.circle(s, (212, 224, 98, 255), (cx + 7 + sway, h // 2 - 2 + bob), 2)
    elif kind == "enemy_land_octopus":
        body_bob = int(abs(math.sin(phase * math.tau)) * 2)
        pygame.draw.ellipse(s, (204, 102, 0, 255), pygame.Rect(cx - 13, 6 + bob - body_bob, 26, 18))
        for i in range(6):
            x = 2 + i * 8
            ty = 19 + ((i + int(phase * 10)) % 2)
            pygame.draw.ellipse(s, (210, 118, 18, 255), pygame.Rect(x, ty + bob, 10, 18))
            pygame.draw.circle(s, (167, 86, 18, 255), (x + 4, 33 + bob), 1)
        pygame.draw.circle(s, (245, 230, 90, 255), (cx - 7, 13 + bob - body_bob), 3)
        pygame.draw.circle(s, (245, 230, 90, 255), (cx + 7, 13 + bob - body_bob), 3)
    elif kind == "enemy_little_devil":
        hop = int(max(0, math.sin(phase * math.tau)) * 3)
        c = (w // 2, h // 2 - hop)
        pygame.draw.circle(s, (204, 34, 0, 255), c, min(w, h) // 3)
        pygame.draw.polygon(s, (235, 184, 72, 255), [(c[0] - 6, c[1] - 12), (c[0] - 2, c[1] - 7), (c[0] - 9, c[1] - 7)])
        pygame.draw.polygon(s, (235, 184, 72, 255), [(c[0] + 6, c[1] - 12), (c[0] + 2, c[1] - 7), (c[0] + 9, c[1] - 7)])
        if int(phase * 4) % 2 == 0:
            pygame.draw.polygon(s, (190, 57, 43, 255), [(c[0] - 12, c[1]), (c[0] - 18, c[1] - 4), (c[0] - 17, c[1] + 5)])
            pygame.draw.polygon(s, (190, 57, 43, 255), [(c[0] + 12, c[1]), (c[0] + 18, c[1] - 4), (c[0] + 17, c[1] + 5)])
        pygame.draw.circle(s, (255, 220, 140, 255), (c[0] - 4, c[1] - 1), 1)
        pygame.draw.circle(s, (255, 220, 140, 255), (c[0] + 4, c[1] - 1), 1)
    elif kind == "enemy_poisonous_mushroom":
        cap_bob = int(abs(math.sin(phase * math.tau)) * 3)
        pygame.draw.circle(s, (102, 0, 204, 255), (cx, 15 + bob - cap_bob), 14)
        pygame.draw.rect(s, (240, 234, 214, 255), pygame.Rect(cx - 8, 20 + bob, 16, 14), border_radius=4)
        pygame.draw.circle(s, (207, 180, 225, 255), (cx - 7, 13 + bob - cap_bob), 2)
        pygame.draw.circle(s, (207, 180, 225, 255), (cx - 1, 11 + bob - cap_bob), 2)
        pygame.draw.circle(s, (207, 180, 225, 255), (cx + 5, 14 + bob - cap_bob), 2)
    elif kind == "enemy_stonehead_turtle":
        wob = int(math.sin(phase * math.tau) * 1)
        pygame.draw.ellipse(s, (136, 136, 128, 255), pygame.Rect(2, 7 + bob, w - 4, h - 11))
        pygame.draw.ellipse(s, (108, 108, 102, 255), pygame.Rect(8, 12 + bob, w - 16, h - 18), 2)
        neck = 6 + int(max(0, math.sin(phase * math.tau)) * 8) if mode == "attack" else 6 + wob
        pygame.draw.circle(s, (104, 104, 98, 255), (cx + 8 + neck, h - 12 + bob), 5)
    elif kind == "boss_grimrak":
        stomp = int(abs(math.sin(phase * math.tau)) * 4)
        pygame.draw.rect(s, (51, 51, 64, 255), pygame.Rect(13, 8 + bob, w - 26, h - 14), border_radius=10)
        pygame.draw.rect(s, (82, 82, 96, 255), pygame.Rect(20, 16 + bob, w - 40, h - 20), border_radius=8)
        pygame.draw.rect(s, (61, 61, 75, 255), pygame.Rect(5, 28 + bob + stomp, 17, 34), border_radius=4)
        pygame.draw.rect(s, (61, 61, 75, 255), pygame.Rect(w - 22, 28 + bob - stomp, 17, 34), border_radius=4)
        pygame.draw.circle(s, (255, 145, 50, 255), (cx, cy), 10)
    elif kind == "boss_zara":
        trail = int(math.sin(phase * math.tau) * 2)
        pygame.draw.polygon(s, (119, 34, 170, 255), [(cx, 6 + bob), (cx - 16, h - 14), (cx + 16, h - 14)])
        pygame.draw.polygon(s, (88, 24, 128, 255), [(cx + trail, 14 + bob), (cx - 10 + trail, h - 14), (cx + 10 + trail, h - 14)])
        pygame.draw.circle(s, (222, 218, 230, 255), (cx, 20 + bob), 7)
        pygame.draw.line(s, (58, 202, 205, 255), (cx + 10, 16 + bob), (cx + 22, 8 + bob), 3)
        pygame.draw.circle(s, (100, 240, 250, 255), (cx + 22, 8 + bob), 3)

    add_outline(s, 2 if kind.startswith("boss_") else 1)
    return s


def generate_monster_sheets() -> None:
    spec = [
        ("enemy_evil_ninja", 44, 44),
        ("enemy_skeleton", 44, 48),
        ("enemy_zombie", 44, 48),
        ("enemy_sewage_creature", 44, 44),
        ("enemy_land_octopus", 52, 44),
        ("enemy_little_devil", 36, 40),
        ("enemy_poisonous_mushroom", 40, 44),
        ("enemy_stonehead_turtle", 48, 40),
        ("boss_grimrak", 80, 80),
        ("boss_zara", 64, 64),
    ]

    for kind, fw, fh in spec:
        walk_sheet = pygame.Surface((fw * 4, fh), pygame.SRCALPHA)
        attack_sheet = pygame.Surface((fw * 4, fh), pygame.SRCALPHA)
        for i in range(4):
            phase = i / 4.0
            walk = draw_base_enemy(kind, fw, fh, phase, mode="walk")
            walk_sheet.blit(walk, (i * fw, 0))

            atk_phase = (i * 0.2) + (0.35 if i == 0 else 0.0)
            attack = draw_base_enemy(kind, fw, fh, atk_phase, mode="attack")

            # attack overlays
            if kind == "enemy_evil_ninja":
                y = 20 + int(math.sin(i * 0.8) * 2)
                pygame.draw.line(attack, (210, 220, 230, 255), (24, y), (40, y - 8 + i), 3)
                if i == 2:
                    pygame.draw.line(attack, (255, 255, 255, 200), (30, 12), (42, 5), 2)
            elif kind == "enemy_skeleton":
                pygame.draw.line(attack, (190, 170, 140, 255), (24, 24), (34 + i * 2, 10 + i * 2), 4)
                if i == 2:
                    pygame.draw.circle(attack, (255, 210, 120, 220), (36, 36), 3)
            elif kind == "enemy_zombie":
                reach = 10 + i * 3
                pygame.draw.rect(attack, (122, 156, 94, 255), pygame.Rect(24, 20, min(fw - 24, reach), 6), border_radius=2)
            elif kind == "enemy_sewage_creature":
                pygame.draw.line(attack, (75, 130, 75, 255), (20, 26), (30 + i * 3, 12 + (2 - i)), 4)
                if i == 2:
                    pygame.draw.circle(attack, (128, 182, 92, 220), (40, 18), 3)
            elif kind == "enemy_land_octopus":
                pygame.draw.line(attack, (214, 126, 42, 255), (24, 20), (30 + i * 3, 35 - i), 4)
                pygame.draw.line(attack, (214, 126, 42, 255), (28, 20), (36 + i * 3, 34 - i), 4)
            elif kind == "enemy_little_devil":
                pygame.draw.line(attack, (230, 142, 55, 255), (20, 20), (28 + i * 2, 12), 3)
                pygame.draw.line(attack, (255, 220, 170, 255), (28 + i * 2, 12), (31 + i * 2, 9), 1)
            elif kind == "enemy_poisonous_mushroom":
                if i >= 1:
                    pygame.draw.circle(attack, (120, 220, 120, 130), (30 + i * 2, 20), 3 + i)
            elif kind == "enemy_stonehead_turtle":
                if i == 2:
                    pygame.draw.circle(attack, (240, 200, 130, 220), (40, 21), 4)
            elif kind == "boss_grimrak":
                pygame.draw.rect(attack, (70, 70, 85, 255), pygame.Rect(6, 22, 20 + i * 6, 28), border_radius=4)
                if i in (2, 3):
                    for k in range(8):
                        pygame.draw.circle(attack, (126, 98, 70, 180), (25 + k * 5, 70 - (k % 3) * 2), 2)
            elif kind == "boss_zara":
                if i >= 1:
                    pygame.draw.circle(attack, (180, 80, 240, 210), (44, 18), 4 + i)
                    pygame.draw.circle(attack, (245, 220, 255, 240), (44, 18), 2)

            add_outline(attack, 1)
            attack_sheet.blit(attack, (i * fw, 0))

        save(walk_sheet, f"{kind}_walk.png")
        save(attack_sheet, f"{kind}_attack.png")


def generate_voltrak_brief_assets() -> None:
    # boss_voltrak.png
    v = pygame.Surface((128, 64), pygame.SRCALPHA)
    points = [(8, 44), (26, 35), (44, 29), (63, 33), (82, 25), (102, 18), (122, 14)]
    pygame.draw.lines(v, (20, 40, 78, 255), False, points, 16)
    pygame.draw.lines(v, (28, 62, 115, 255), False, points, 10)
    for x, y in ((26, 35), (44, 29), (63, 33), (82, 25), (102, 18)):
        pygame.draw.rect(v, (176, 133, 64, 255), pygame.Rect(x - 7, y - 7, 14, 10), border_radius=3)
    pygame.draw.line(v, (255, 224, 0, 255), (100, 26), (124, 30), 6)
    pygame.draw.line(v, (255, 255, 255, 255), (102, 26), (124, 30), 2)
    pygame.draw.arc(v, (88, 168, 255, 255), pygame.Rect(78, 8, 28, 18), 0.2, 2.5, 2)
    pygame.draw.arc(v, (88, 168, 255, 255), pygame.Rect(92, 5, 24, 16), 0.1, 2.6, 2)
    pygame.draw.circle(v, (255, 232, 0, 255), (114, 14), 3)
    add_outline(v, 2)
    save(v, "boss_voltrak.png")

    # fx_boss_slam.png 640x160 (4x160)
    slam = pygame.Surface((640, 160), pygame.SRCALPHA)
    for i, r in enumerate((20, 60, 100, 130)):
        f = pygame.Surface((160, 160), pygame.SRCALPHA)
        cx, cy = 80, 80
        alpha = max(60, 230 - i * 45)
        pygame.draw.circle(f, (255, 170, 58, alpha), (cx, cy), r, max(2, 8 - i * 2))
        pygame.draw.circle(f, (255, 185, 90, max(0, 180 - i * 45)), (cx, cy), max(4, r // 2))
        cracks = 6 + i * 2
        for k in range(cracks):
            ang = (k / cracks) * math.tau
            x1, y1 = cx + int(math.cos(ang) * (r - 6)), cy + int(math.sin(ang) * (r - 6))
            x2, y2 = cx + int(math.cos(ang) * (r + 16)), cy + int(math.sin(ang) * (r + 16))
            pygame.draw.line(f, (140, 98, 60, 220 - i * 40), (x1, y1), (x2, y2), 2)
        if i == 3:
            for k in range(12):
                pygame.draw.circle(f, (126, 98, 70, 140), (20 + k * 10, 120 + (k % 3) * 6), 2)
        add_outline(f, 1)
        slam.blit(f, (i * 160, 0))
    save(slam, "fx_boss_slam.png")

    # fx_zara_bolt.png 64x16 (4x16)
    zbolt = pygame.Surface((64, 16), pygame.SRCALPHA)
    for i in range(4):
        f = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(f, (180, 0, 255, 210), (8, 8), 4 + (1 if i == 2 else 0))
        pygame.draw.circle(f, (255, 200, 255, 240), (8, 8), 2)
        if i in (1, 2):
            pygame.draw.line(f, (255, 200, 245, 200), (4, 8), (1, 8), 2)
            pygame.draw.circle(f, (255, 230, 255, 170), (2, 7), 1)
        if i == 2:
            pygame.draw.circle(f, (255, 230, 255, 170), (12, 5), 1)
            pygame.draw.circle(f, (255, 230, 255, 170), (12, 11), 1)
        add_outline(f, 1)
        zbolt.blit(f, (i * 16, 0))
    save(zbolt, "fx_zara_bolt.png")

    # fx_voltrak_bolt.png 80x8 (4x20)
    vbolt = pygame.Surface((80, 8), pygame.SRCALPHA)
    for i in range(4):
        f = pygame.Surface((20, 8), pygame.SRCALPHA)
        pts = [(2, 4), (6, 2 + (i % 2)), (10, 4), (14, 3 + ((i + 1) % 2)), (18, 4), (14, 5), (10, 4), (6, 5)]
        pygame.draw.polygon(f, (255, 224, 0, 245), pts)
        pygame.draw.line(f, (255, 255, 255, 255), (5, 4), (15, 4), 1)
        if i == 1:
            pygame.draw.line(f, (120, 190, 255, 200), (7, 1), (11, 0), 1)
        if i == 3:
            pygame.draw.circle(f, (255, 255, 255, 200), (2, 4), 1)
        add_outline(f, 1)
        vbolt.blit(f, (i * 20, 0))
    save(vbolt, "fx_voltrak_bolt.png")

    # fx_voltrak_shockwave.png 1024x256 (4x256)
    shock = pygame.Surface((1024, 256), pygame.SRCALPHA)
    for i, r in enumerate((60, 120, 180, 220)):
        f = pygame.Surface((256, 256), pygame.SRCALPHA)
        cx, cy = 128, 128
        thickness = max(2, 8 - i * 2)
        if i < 2:
            pygame.draw.circle(f, (255, 224, 0, 220 - i * 30), (cx, cy), r, thickness)
            pygame.draw.circle(f, (255, 255, 255, 180 - i * 30), (cx, cy), r - 2, 2)
        else:
            segs = 10
            for k in range(segs):
                if (k + i) % 3 == 0:
                    continue
                a0 = (k / segs) * math.tau
                a1 = ((k + 0.6) / segs) * math.tau
                pygame.draw.arc(f, (255, 230, 120, 140 - (i - 2) * 55), pygame.Rect(cx - r, cy - r, r * 2, r * 2), a0, a1, thickness)
        pygame.draw.circle(f, (68, 170, 255, 130 - i * 20), (cx, cy), r + 3, 2)
        add_outline(f, 1)
        shock.blit(f, (i * 256, 0))
    save(shock, "fx_voltrak_shockwave.png")

    # npc_summoner.png
    n = pygame.Surface((44, 44), pygame.SRCALPHA)
    cx = 22
    pygame.draw.polygon(n, (30, 66, 140, 255), [(cx, 10), (cx - 13, 38), (cx + 13, 38)])
    pygame.draw.polygon(n, (20, 52, 112, 255), [(cx, 4), (cx - 9, 20), (cx + 9, 20)])
    for sx, sy in ((16, 22), (28, 18), (24, 30), (14, 30)):
        pygame.draw.circle(n, (245, 205, 70, 255), (sx, sy), 1)
    pygame.draw.circle(n, (245, 210, 170, 255), (cx, 20), 6)
    pygame.draw.arc(n, (225, 190, 165, 255), pygame.Rect(cx - 5, 20, 10, 6), math.pi, math.tau, 2)
    pygame.draw.circle(n, (235, 100, 100, 170), (18, 22), 2)
    pygame.draw.circle(n, (235, 100, 100, 170), (26, 22), 2)
    pygame.draw.circle(n, (250, 220, 120, 220), (33, 26), 5)
    pygame.draw.circle(n, (255, 250, 210, 240), (33, 26), 2)
    add_outline(n, 2)
    save(n, "npc_summoner.png")

    # fx_summon_appear.png 288x48 (6x48)
    summon = pygame.Surface((288, 48), pygame.SRCALPHA)
    radii = [4, 9, 13, 10, 6, 2]
    for i, r in enumerate(radii):
        f = pygame.Surface((48, 48), pygame.SRCALPHA)
        cx, cy = 24, 24
        if i == 0:
            pygame.draw.circle(f, (255, 215, 0, 210), (cx, cy), 4)
        elif i in (1, 2):
            rays = 4 if i == 1 else 8
            for k in range(rays):
                a = (k / rays) * math.tau
                x2, y2 = cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)
                pygame.draw.line(f, (255, 220, 80, 240), (cx, cy), (x2, y2), 2)
            pygame.draw.circle(f, (255, 255, 235, 255), (cx, cy), 3)
        else:
            for k in range(8 - i):
                x = 10 + (k * 5 + i * 3) % 28
                y = 16 + ((k + i) % 4) * 6
                pygame.draw.circle(f, (255, 220, 100, 190 - i * 30), (x, y), 2 if i < 4 else 1)
        add_outline(f, 1)
        summon.blit(f, (i * 48, 0))
    save(summon, "fx_summon_appear.png")

    # tile_electric.png 128x32 (4x32)
    te = pygame.Surface((128, 32), pygame.SRCALPHA)
    for i in range(4):
        f = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(f, (70, 72, 80, 255), pygame.Rect(0, 0, 32, 32))
        pygame.draw.rect(f, (20, 20, 24, 255), pygame.Rect(2, 2, 28, 28), 2)
        glow = [120, 180, 230, 140][i]
        pygame.draw.circle(f, (255, 176, 0, glow), (16, 16), 9)
        pygame.draw.circle(f, (255, 230, 120, 150 + i * 20 if i < 3 else 140), (16, 16), 5 + (1 if i == 2 else 0))
        if i in (1, 2, 3):
            pygame.draw.line(f, (255, 245, 180, 210), (9, 15), (14, 11), 1)
            pygame.draw.line(f, (255, 245, 180, 210), (18, 20), (24, 16), 1)
        add_outline(f, 1)
        te.blit(f, (i * 32, 0))
    save(te, "tile_electric.png")

    # tile_stone.png 32x32
    ts = pygame.Surface((32, 32), pygame.SRCALPHA)
    for y in range(32):
        c = 95 - int(y * 0.7)
        pygame.draw.line(ts, (c, c - 2, c + 8, 255), (0, y), (31, y), 1)
    for y in range(0, 32, 8):
        offset = 4 if (y // 8) % 2 else 0
        for x in range(-offset, 32, 8):
            pygame.draw.rect(ts, (62, 62, 72, 255), pygame.Rect(x, y, 8, 8), 1)
    pygame.draw.rect(ts, (20, 20, 24, 255), pygame.Rect(0, 0, 32, 32), 1)
    save(ts, "tile_stone.png")


def main() -> int:
    pygame.init()
    pygame.display.set_mode((1, 1))
    generate_voltrak_brief_assets()
    generate_monster_sheets()
    print("Generated 29 art assets for Voltrak/effects/tiles and monster walk/attack sheets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
