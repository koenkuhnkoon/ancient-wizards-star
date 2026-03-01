"""Generate character idle/walk sheets matching existing attack sheet style."""

from __future__ import annotations

from pathlib import Path
import math
import sys

import pygame


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PLAYER_DIR = ASSETS / "sprites" / "players"

# Reuse the same base-character builder and outline from attack-sheet generator.
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import generate_weapon_fx_art as atk  # noqa: E402


def _save(surface: pygame.Surface, filename: str) -> None:
    pygame.image.save(surface, str(ASSETS / filename))
    PLAYER_DIR.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(PLAYER_DIR / filename))


def _staff(frame: pygame.Surface, bob: int, x_shift: int, glow: int = 0) -> None:
    tip = (33 + x_shift, 15 + bob)
    pygame.draw.line(frame, (121, 85, 72, 255), (28 + x_shift, 30 + bob), tip, 3)
    if glow > 0:
        pygame.draw.circle(frame, (177, 113, 255, 200), tip, glow)
        pygame.draw.circle(frame, (240, 225, 255, 255), tip, max(1, glow // 2))


def _sword(frame: pygame.Surface, bob: int, ang: float, x_shift: int) -> None:
    x0, y0 = 30 + x_shift, 22 + bob
    x1 = x0 + int(math.cos(ang) * 12)
    y1 = y0 - int(math.sin(ang) * 12)
    pygame.draw.line(frame, (185, 152, 46, 255), (27 + x_shift, 26 + bob), (x0, y0), 4)
    pygame.draw.line(frame, (186, 194, 205, 255), (x0, y0), (x1, y1), 4)
    pygame.draw.line(frame, (255, 255, 255, 255), (x0 + 1, y0), (x1, y1), 1)


def _dagger(frame: pygame.Surface, bob: int, reach: int) -> None:
    y = 24 + bob
    pygame.draw.line(frame, (95, 95, 105, 255), (24, y), (24 + reach, y - 2), 3)
    pygame.draw.line(frame, (255, 255, 255, 255), (26, y - 2), (24 + reach, y - 2), 1)


def _pickaxe(frame: pygame.Surface, bob: int, angle: float, x_shift: int) -> None:
    x0, y0 = 26 + x_shift, 23 + bob
    x1 = x0 + int(math.cos(angle) * 11)
    y1 = y0 - int(math.sin(angle) * 11)
    pygame.draw.line(frame, (121, 85, 72, 255), (24 + x_shift, 28 + bob), (x1, y1), 3)
    head = [(x1 - 3, y1 - 2), (x1 + 4, y1 + 1), (x1 - 1, y1 + 5)]
    pygame.draw.polygon(frame, (162, 171, 178, 255), head)


def _shuriken(frame: pygame.Surface, x: int, y: int, rot: float, r: int = 4) -> None:
    atk.draw_star4(frame, x, y, r, rot, (180, 216, 255, 255))


def _laser_cannon(frame: pygame.Surface, bob: int, charge: int) -> None:
    pygame.draw.rect(frame, (75, 104, 122, 255), pygame.Rect(30, 20 + bob, 10, 8), border_radius=2)
    if charge > 0:
        pygame.draw.circle(frame, (90, 235, 255, 170), (41, 24 + bob), charge)
        pygame.draw.circle(frame, (220, 255, 255, 220), (41, 24 + bob), max(1, charge // 2))


def make_idle(char: str, weapon: str) -> pygame.Surface:
    sheet = pygame.Surface((192, 48), pygame.SRCALPHA)
    for i in range(4):
        frame = pygame.Surface((48, 48), pygame.SRCALPHA)
        phase = i / 4.0
        bob = int(math.sin(phase * math.tau) * 1.2)
        atk.draw_character_base(frame, char, phase)

        if weapon == "staff":
            _staff(frame, bob, -1, glow=(1 if i % 2 == 0 else 2))
        elif weapon == "sword":
            _sword(frame, bob, ang=1.2 + math.sin(phase * math.tau) * 0.2, x_shift=-1)
        elif weapon == "dagger":
            _dagger(frame, bob, reach=8 + (i % 2))
            eye_x = 19 if i % 2 == 0 else 21
            pygame.draw.circle(frame, (130, 220, 255, 255), (eye_x, 18 + bob), 1)
        elif weapon == "pickaxe":
            _pickaxe(frame, bob, angle=1.0 + math.sin(phase * math.tau) * 0.25, x_shift=-1)
            if i % 2 == 0:
                pygame.draw.circle(frame, (255, 225, 180, 210), (20, 19 + bob), 1)
        elif weapon == "shuriken":
            _shuriken(frame, 34, 16 + bob, i * 25, r=3)
        elif weapon == "laser":
            _laser_cannon(frame, bob, charge=(1 + (i % 2)))
            if i in (1, 3):
                pygame.draw.rect(frame, (180, 245, 255, 220), pygame.Rect(19, 14 + bob, 10, 2), border_radius=1)

        atk.add_outline(frame, 1)
        sheet.blit(frame, (i * 48, 0))
    return sheet


def make_walk(char: str, weapon: str, style: str) -> pygame.Surface:
    sheet = pygame.Surface((288, 48), pygame.SRCALPHA)
    for i in range(6):
        frame = pygame.Surface((48, 48), pygame.SRCALPHA)
        phase = i / 6.0
        swing = math.sin(phase * math.tau)
        bob_mul = {
            "wizard": 1.4,
            "knight": 2.1,
            "assassin": 0.8,
            "miner": 2.2,
            "ninja": 1.0,
            "robot": 1.7,
        }[style]
        bob = int(swing * bob_mul)
        atk.draw_character_base(frame, char, phase)

        leg_y = 36 + bob
        foot_a = int(swing * 4)
        foot_b = -foot_a

        # Tiny cartoon feet to sell walk cycle.
        pygame.draw.ellipse(frame, (32, 32, 32, 220), pygame.Rect(16 + foot_a, leg_y, 7, 3))
        pygame.draw.ellipse(frame, (32, 32, 32, 220), pygame.Rect(25 + foot_b, leg_y, 7, 3))

        if weapon == "staff":
            _staff(frame, bob, x_shift=-2 + int(swing * 1.5), glow=1)
            pygame.draw.line(frame, (150, 90, 195, 140), (20, 34 + bob), (24, 30 + bob), 1)
        elif weapon == "sword":
            _sword(frame, bob, ang=1.0 + swing * 0.3, x_shift=-2)
        elif weapon == "dagger":
            _dagger(frame, bob, reach=10 + int(max(0, swing) * 4))
        elif weapon == "pickaxe":
            _pickaxe(frame, bob, angle=0.8 + swing * 0.5, x_shift=-2)
        elif weapon == "shuriken":
            arm_x = 30 + int(swing * 2)
            pygame.draw.line(frame, (29, 42, 75, 255), (25, 24 + bob), (arm_x, 19 + bob), 3)
            if i in (2, 5):
                _shuriken(frame, 39, 16 + bob, i * 22, r=3)
        elif weapon == "laser":
            _laser_cannon(frame, bob, charge=1 + (1 if i % 3 == 0 else 0))
            if i == 4:
                pygame.draw.ellipse(frame, (70, 240, 255, 190), pygame.Rect(38, 22 + bob, 10, 3))

        atk.add_outline(frame, 1)
        sheet.blit(frame, (i * 48, 0))
    return sheet


def main() -> int:
    pygame.init()
    pygame.display.set_mode((1, 1))

    mapping = [
        ("wizard", "staff", "wizard", "player_wizard"),
        ("knight", "sword", "knight", "player_knight"),
        ("assassin", "dagger", "assassin", "player_assassin"),
        ("miner", "pickaxe", "miner", "player_miner"),
        ("ninja", "shuriken", "ninja", "player_ninja"),
        ("robot", "laser", "robot", "player_robot"),
    ]

    for char, weapon, style, prefix in mapping:
        _save(make_idle(char, weapon), f"{prefix}_idle.png")
        _save(make_walk(char, weapon, style), f"{prefix}_walk.png")

    print("Generated 12 idle/walk sheets in assets/ and synced to assets/sprites/players/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
