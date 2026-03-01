# Art Asset Drop Zone

This folder is the implementation target for the character and visual design spec.

## Player spritesheets (required for in-game player rendering)

Put files in `assets/sprites/players/` using this convention:

- `{prefix}_idle.png` -> `4` frames, horizontal sheet
- `{prefix}_walk.png` -> `6` frames, horizontal sheet
- `{prefix}_attack.png` -> `4` frames, horizontal sheet

All player frames are `48x48`.

Player prefixes:

- `player_wizard`
- `player_knight`
- `player_assassin`
- `player_miner`
- `player_ninja`
- `player_robot`

Example:

- `assets/sprites/players/player_wizard_idle.png` size must be `192x48`.

## Other game assets

The full filename/size contract is tracked in:

- `game/asset_manifest.py`

Run validation after dropping art:

```bash
python tools/validate_assets.py
```
