"""Generate weapons/effects and HD attack sheets from art_brief_weapons.md."""

from __future__ import annotations

from pathlib import Path
import math

import pygame


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PLAYER_DIR = ASSETS / "sprites" / "players"

OUTLINE = (20, 20, 20, 255)
WHITE = (255, 255, 255, 255)


def save_png(surface: pygame.Surface, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(ASSETS / name))


def add_outline(surface: pygame.Surface, passes: int = 1) -> None:
    for _ in range(passes):
        src = surface.copy()
        w, h = surface.get_size()
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if src.get_at((x, y)).a != 0:
                    continue
                if any(
                    src.get_at((nx, ny)).a > 0
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                ):
                    surface.set_at((x, y), OUTLINE)


def draw_star4(surface: pygame.Surface, cx: int, cy: int, r: int, angle_deg: float, fill: tuple[int, int, int, int]) -> None:
    points = []
    for i in range(8):
        a = math.radians(angle_deg + i * 45.0)
        rr = r if i % 2 == 0 else max(2, int(r * 0.42))
        points.append((cx + int(math.cos(a) * rr), cy + int(math.sin(a) * rr)))
    pygame.draw.polygon(surface, fill, points)
    pygame.draw.polygon(surface, OUTLINE, points, 2)


def attack_staff() -> pygame.Surface:
    sheet = pygame.Surface((400, 100), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        cx, cy = 50, 50
        orb_r = 10 + i * 8
        glow_r = 20 + i * 12
        pygame.draw.circle(frame, (170, 90, 255, 120), (cx, cy), glow_r)
        pygame.draw.circle(frame, (215, 150, 255, 170), (cx, cy), orb_r + 6)
        pygame.draw.circle(frame, (236, 208, 255, 255), (cx, cy), orb_r)
        for k in range(8 + i * 3):
            ang = (k / max(1, 8 + i * 3)) * math.tau + i * 0.2
            rr = orb_r + 10 + i * 9
            x = cx + int(math.cos(ang) * rr)
            y = cy + int(math.sin(ang) * rr)
            pygame.draw.circle(frame, (190, 130, 255, 230), (x, y), 2 if i < 2 else 3)
        add_outline(frame, 1)
        sheet.blit(frame, (i * 100, 0))
    return sheet


def attack_sword() -> pygame.Surface:
    sheet = pygame.Surface((320, 50), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((80, 50), pygame.SRCALPHA)
        cx, cy = 24 + i * 7, 26
        arc_rect = pygame.Rect(cx - 28, cy - 20, 56, 40)
        pygame.draw.arc(frame, (255, 235, 80, 240), arc_rect, math.radians(210), math.radians(340), 8)
        pygame.draw.arc(frame, (255, 255, 230, 255), arc_rect, math.radians(215), math.radians(335), 3)
        for t in range(3):
            pygame.draw.line(
                frame,
                (255, 230, 120, 130 - t * 25),
                (max(0, cx - 24 - t * 3), cy + 12 + t * 3),
                (max(0, cx - 40 - t * 4), cy + 20 + t * 3),
                2,
            )
        add_outline(frame, 1)
        sheet.blit(frame, (i * 80, 0))
    return sheet


def attack_daggers() -> pygame.Surface:
    sheet = pygame.Surface((80, 32), pygame.SRCALPHA)
    for i in range(2):
        frame = pygame.Surface((40, 32), pygame.SRCALPHA)
        y = 16
        length = 22 + i * 6
        pygame.draw.line(frame, (210, 220, 235, 240), (6, y), (6 + length, y), 4)
        pygame.draw.line(frame, (255, 255, 255, 255), (8, y - 1), (8 + length - 2, y - 1), 1)
        pygame.draw.polygon(frame, (255, 120, 120, 230), [(6 + length, y), (6 + length - 5, y - 3), (6 + length - 5, y + 3)])
        for t in range(3):
            pygame.draw.line(frame, (220, 230, 255, 130 - t * 30), (4 - t, y - 3 + t), (8, y - 2 + t), 1)
        add_outline(frame, 1)
        sheet.blit(frame, (i * 40, 0))
    return sheet


def attack_pickaxe() -> pygame.Surface:
    sheet = pygame.Surface((440, 40), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((110, 40), pygame.SRCALPHA)
        cx, cy = 34 + i * 14, 24
        arc_rect = pygame.Rect(cx - 36, cy - 14, 72, 28)
        pygame.draw.arc(frame, (219, 128, 47, 230), arc_rect, math.radians(190), math.radians(350), 9)
        pygame.draw.arc(frame, (255, 186, 82, 250), arc_rect, math.radians(197), math.radians(343), 4)
        for k in range(6):
            px = min(106, cx + 16 + k * 8)
            py = 26 + (k % 2) * 5
            pygame.draw.circle(frame, (145, 96, 70, 200), (px, py), 2)
        for k in range(4):
            px = min(106, cx + 24 + k * 10)
            py = 10 + (k % 2) * 5
            pygame.draw.polygon(frame, (196, 160, 120, 210), [(px, py), (px + 3, py + 1), (px + 1, py + 4)])
        add_outline(frame, 1)
        sheet.blit(frame, (i * 110, 0))
    return sheet


def projectile_shuriken() -> pygame.Surface:
    sheet = pygame.Surface((56, 14), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((14, 14), pygame.SRCALPHA)
        draw_star4(frame, 7, 7, 6, i * 22.5, (177, 215, 255, 255))
        pygame.draw.circle(frame, (240, 248, 255, 255), (7, 7), 2)
        pygame.draw.circle(frame, (114, 179, 255, 160), (7, 7), 5, 1)
        sheet.blit(frame, (i * 14, 0))
    return sheet


def projectile_laser() -> pygame.Surface:
    sheet = pygame.Surface((48, 8), pygame.SRCALPHA)
    for i in range(2):
        frame = pygame.Surface((24, 8), pygame.SRCALPHA)
        alpha = 230 if i == 0 else 170
        core_alpha = 255 if i == 0 else 220
        pygame.draw.ellipse(frame, (60, 240, 255, alpha), pygame.Rect(2, 1, 20, 6))
        pygame.draw.ellipse(frame, (220, 255, 255, core_alpha), pygame.Rect(5, 2, 14, 4))
        add_outline(frame, 1)
        sheet.blit(frame, (i * 24, 0))
    return sheet


def draw_character_base(frame: pygame.Surface, char: str, phase: float) -> None:
    cx = 24
    bob = int(math.sin(phase * math.tau) * 1.0)
    skin = (244, 198, 160, 255)

    if char == "wizard":
        pygame.draw.polygon(frame, (114, 54, 164, 255), [(cx, 12 + bob), (cx - 14, 41 + bob), (cx + 14, 41 + bob)])
        pygame.draw.polygon(frame, (80, 36, 123, 255), [(cx, 5 + bob), (cx - 9, 21 + bob), (cx + 9, 21 + bob)])
        pygame.draw.circle(frame, skin, (cx, 22 + bob), 6)
    elif char == "knight":
        pygame.draw.rect(frame, (132, 146, 160, 255), pygame.Rect(cx - 12, 12 + bob, 24, 26), border_radius=5)
        pygame.draw.rect(frame, (178, 188, 198, 255), pygame.Rect(cx - 10, 14 + bob, 20, 10), border_radius=3)
        pygame.draw.rect(frame, (125, 141, 156, 255), pygame.Rect(cx - 8, 8 + bob, 16, 8), border_radius=3)
    elif char == "assassin":
        pygame.draw.polygon(frame, (31, 52, 58, 255), [(cx, 13 + bob), (cx - 12, 39 + bob), (cx + 12, 39 + bob)])
        pygame.draw.rect(frame, (47, 77, 84, 255), pygame.Rect(cx - 8, 16 + bob, 16, 13), border_radius=4)
        pygame.draw.circle(frame, skin, (cx, 22 + bob), 5)
        pygame.draw.rect(frame, (31, 52, 58, 255), pygame.Rect(cx - 8, 20 + bob, 16, 4), border_radius=2)
    elif char == "miner":
        pygame.draw.rect(frame, (191, 103, 43, 255), pygame.Rect(cx - 12, 14 + bob, 24, 22), border_radius=6)
        pygame.draw.rect(frame, (49, 82, 132, 255), pygame.Rect(cx - 12, 20 + bob, 24, 16), border_radius=4)
        pygame.draw.rect(frame, (244, 200, 78, 255), pygame.Rect(cx - 12, 8 + bob, 24, 9), border_radius=4)
        pygame.draw.circle(frame, skin, (cx, 19 + bob), 6)
    elif char == "ninja":
        pygame.draw.rect(frame, (29, 42, 75, 255), pygame.Rect(cx - 11, 12 + bob, 22, 24), border_radius=5)
        pygame.draw.circle(frame, skin, (cx, 18 + bob), 6)
        pygame.draw.rect(frame, (243, 197, 61, 255), pygame.Rect(cx - 9, 12 + bob, 18, 3), border_radius=1)
    elif char == "robot":
        pygame.draw.rect(frame, (93, 123, 139, 255), pygame.Rect(cx - 11, 10 + bob, 22, 26), border_radius=3)
        pygame.draw.rect(frame, (43, 60, 76, 255), pygame.Rect(cx - 8, 13 + bob, 16, 6), border_radius=2)
        pygame.draw.circle(frame, (95, 227, 255, 255), (cx - 3, 16 + bob), 2)
        pygame.draw.circle(frame, (95, 227, 255, 255), (cx + 3, 16 + bob), 2)


def attack_sheet(character: str, weapon: str) -> pygame.Surface:
    sheet = pygame.Surface((192, 48), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((48, 48), pygame.SRCALPHA)
        phase = i / 4.0
        draw_character_base(frame, character, phase)
        cx = 24
        bob = int(math.sin(phase * math.tau) * 1.0)

        if weapon == "staff":
            tip = (34 + i * 2, 14 + bob - i)
            pygame.draw.line(frame, (121, 85, 72, 255), (30, 24 + bob), tip, 3)
            pygame.draw.circle(frame, (177, 113, 255, 220), tip, 4 + i)
            pygame.draw.circle(frame, (240, 225, 255, 255), tip, 2)
        elif weapon == "sword":
            if i == 0:
                p0, p1 = (24, 10 + bob), (31, 0 + bob)
            elif i == 1:
                p0, p1 = (27, 13 + bob), (37, 6 + bob)
            elif i == 2:
                p0, p1 = (29, 18 + bob), (42, 17 + bob)
            else:
                p0, p1 = (30, 22 + bob), (43, 28 + bob)
            pygame.draw.line(frame, (185, 152, 46, 255), (25, 25 + bob), p0, 4)
            pygame.draw.line(frame, (186, 194, 205, 255), p0, p1, 4)
            pygame.draw.line(frame, WHITE, (p0[0] + 1, p0[1]), (p1[0], p1[1]), 1)
        elif weapon == "dagger":
            arm_y = 24 + bob + (1 if i == 0 else 0)
            tip_x = 30 + i * 4
            pygame.draw.line(frame, (95, 95, 105, 255), (24, arm_y), (tip_x, arm_y - 2), 3)
            pygame.draw.line(frame, WHITE, (26, arm_y - 2), (tip_x, arm_y - 2), 1)
        elif weapon == "pickaxe":
            head_pts = [
                [(27, 6 + bob), (34, 10 + bob), (26, 13 + bob)],
                [(31, 8 + bob), (38, 14 + bob), (30, 16 + bob)],
                [(34, 14 + bob), (42, 20 + bob), (34, 22 + bob)],
                [(36, 18 + bob), (44, 26 + bob), (35, 28 + bob)],
            ][i]
            pygame.draw.line(frame, (121, 85, 72, 255), (24, 25 + bob), (head_pts[1][0] - 2, head_pts[1][1] - 1), 3)
            pygame.draw.polygon(frame, (162, 171, 178, 255), head_pts)
        elif weapon == "shuriken":
            pygame.draw.line(frame, (29, 42, 75, 255), (26, 24 + bob), (31 + i, 18 + bob), 3)
            if i >= 2:
                draw_star4(frame, 38, 16 + bob, 4 if i == 2 else 3, i * 18, (180, 216, 255, 255))
        elif weapon == "laser":
            if i == 0:
                pygame.draw.rect(frame, (75, 104, 122, 255), pygame.Rect(30, 20 + bob, 8, 8), border_radius=2)
            elif i in (1, 2):
                pygame.draw.rect(frame, (75, 104, 122, 255), pygame.Rect(30, 20 + bob, 10, 8), border_radius=2)
                pygame.draw.circle(frame, (90, 235, 255, 180), (41, 24 + bob), 3 + (i - 1))
            else:
                pygame.draw.rect(frame, (75, 104, 122, 255), pygame.Rect(30, 20 + bob, 10, 8), border_radius=2)
                pygame.draw.ellipse(frame, (70, 240, 255, 220), pygame.Rect(38, 22 + bob, 12, 4))
                pygame.draw.ellipse(frame, (220, 255, 255, 255), pygame.Rect(41, 23 + bob, 8, 2))

        add_outline(frame, 1)
        sheet.blit(frame, (i * 48, 0))
    return sheet


def main() -> int:
    pygame.init()
    pygame.display.set_mode((1, 1))

    save_png(attack_staff(), "fx_attack_staff.png")
    save_png(attack_sword(), "fx_attack_sword.png")
    save_png(attack_daggers(), "fx_attack_daggers.png")
    save_png(attack_pickaxe(), "fx_attack_pickaxe.png")
    save_png(projectile_shuriken(), "fx_projectile_shuriken.png")
    save_png(projectile_laser(), "fx_projectile_laser.png")

    save_png(attack_sheet("wizard", "staff"), "player_wizard_attack.png")
    save_png(attack_sheet("knight", "sword"), "player_knight_attack.png")
    save_png(attack_sheet("assassin", "dagger"), "player_assassin_attack.png")
    save_png(attack_sheet("miner", "pickaxe"), "player_miner_attack.png")
    save_png(attack_sheet("ninja", "shuriken"), "player_ninja_attack.png")
    save_png(attack_sheet("robot", "laser"), "player_robot_attack.png")

    # Keep runtime player attack sheets in sync with the delivered flat files.
    PLAYER_DIR.mkdir(parents=True, exist_ok=True)
    for name in (
        "player_wizard_attack.png",
        "player_knight_attack.png",
        "player_assassin_attack.png",
        "player_miner_attack.png",
        "player_ninja_attack.png",
        "player_robot_attack.png",
    ):
        src = ASSETS / name
        dst = PLAYER_DIR / name
        img = pygame.image.load(str(src)).convert_alpha()
        pygame.image.save(img, str(dst))

    print("Generated weapon/effect art sheets in assets/ and synced player attack sheets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
