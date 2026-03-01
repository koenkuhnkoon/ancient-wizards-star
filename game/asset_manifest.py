"""Asset manifest derived from the character and visual design spec.

This file defines naming and sizing contracts so art can be dropped in
without touching gameplay code.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerSpriteSpec:
    prefix: str
    frame_width: int
    frame_height: int
    idle_frames: int
    walk_frames: int
    attack_frames: int


PLAYER_SPRITES: dict[str, PlayerSpriteSpec] = {
    "Wizard": PlayerSpriteSpec("player_wizard", 48, 48, 4, 6, 4),
    "Knight": PlayerSpriteSpec("player_knight", 48, 48, 4, 6, 4),
    "Assassin": PlayerSpriteSpec("player_assassin", 48, 48, 4, 6, 4),
    "Miner": PlayerSpriteSpec("player_miner", 48, 48, 4, 6, 4),
    "Ninja": PlayerSpriteSpec("player_ninja", 48, 48, 4, 6, 4),
    "Robot": PlayerSpriteSpec("player_robot", 48, 48, 4, 6, 4),
}


@dataclass(frozen=True)
class StaticAssetSpec:
    filename: str
    width: int
    height: int
    notes: str = ""


STATIC_ASSETS: tuple[StaticAssetSpec, ...] = (
    StaticAssetSpec("enemy_evil_ninja.png", 44, 44),
    StaticAssetSpec("enemy_sewage_creature.png", 52, 44),
    StaticAssetSpec("enemy_zombie.png", 44, 48),
    StaticAssetSpec("enemy_land_octopus.png", 56, 44),
    StaticAssetSpec("enemy_little_devil.png", 40, 44),
    StaticAssetSpec("enemy_skeleton.png", 44, 48),
    StaticAssetSpec("enemy_poisonous_mushroom.png", 40, 40),
    StaticAssetSpec("enemy_stonehead_turtle.png", 56, 48),
    StaticAssetSpec("boss_grimrak.png", 80, 80),
    StaticAssetSpec("boss_zara.png", 64, 64),
    StaticAssetSpec("boss_ninja_land_eel.png", 128, 64),
    StaticAssetSpec("tile_grass.png", 32, 32),
    StaticAssetSpec("tile_grass_alt.png", 32, 32, "Optional variation"),
    StaticAssetSpec("tile_dirt.png", 32, 32),
    StaticAssetSpec("tile_magic_glow.png", 32, 32),
    StaticAssetSpec("tile_wall.png", 32, 32),
    StaticAssetSpec("tile_tree_top.png", 32, 32),
    StaticAssetSpec("tile_tree_trunk.png", 32, 32),
    StaticAssetSpec("tile_bridge.png", 32, 32),
    StaticAssetSpec("item_health_potion.png", 16, 16),
    StaticAssetSpec("item_energy_potion.png", 16, 16),
    StaticAssetSpec("item_sword.png", 24, 24),
    StaticAssetSpec("item_armor_shield.png", 24, 24),
    StaticAssetSpec("npc_villager.png", 44, 44),
    StaticAssetSpec("npc_shopkeeper.png", 44, 44),
    StaticAssetSpec("npc_companion_knight.png", 48, 48),
    StaticAssetSpec("npc_companion_wizard.png", 48, 48),
)


@dataclass(frozen=True)
class AnimatedSheetSpec:
    filename: str
    frame_width: int
    frame_height: int
    frames: int
    sheet_width_override: int | None = None


ANIMATED_SHEETS: tuple[AnimatedSheetSpec, ...] = (
    AnimatedSheetSpec("tile_water.png", 32, 32, 4),
    AnimatedSheetSpec("world_respawn_point.png", 32, 32, 4),
    AnimatedSheetSpec("world_portal_gate.png", 96, 128, 8, 1024),
    AnimatedSheetSpec("item_magical_shard.png", 16, 16, 4),
)
