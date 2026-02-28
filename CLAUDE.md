# The Ancient Wizard's Star

A father-and-son open-world RPG built with Python + Pygame.

## Team
Built by a dad and his 8-year-old son. Keep code readable,
well-commented, and fun to work on together.

## Tech Stack
- Language: Python 3
- Framework: Pygame
- Browser: pygbag  →  pip install pygbag
  - Run locally:    python main.py
  - Run in browser: python -m pygbag main.py  (open http://localhost:8000)
- Dependencies tracked in requirements.txt

## Game Design

**Title:** The Ancient Wizard's Star
**Genre:** Open-world action RPG
**Setting:** A magical world with mythical creatures, monsters, and magic

### Core Loop
1. Explore the open world
2. Fight monsters → collect magical shards, weapons, armor
3. Level up → increase health and energy (start: Health 10 / Energy 10)
4. Find and defeat 3 bosses, each with:
   - 2 enemy mini-bosses to beat first
   - 2 player companions fighting alongside you
5. Light the Ancient Dimensional Portal Gate
6. Defeat the final big boss → complete Loop 1!

### Characters
Wizards, knights, assassins, miners, ninjas, robots, monsters

### Mechanics
- Walk or run through the open world
- Buy items from certain NPCs, move light objects
- Respawn points scattered around the world
- Voice NPC interaction: speak aloud to talk to NPCs (stretch goal)

### Progression
- Collect magical shards to level up
- Weapons and armor: found in the world or dropped by monsters
- Leveling up increases max health and max energy

## Project Structure
```
Bakuriani Game/
├── CLAUDE.md
├── Game Notes.md
├── requirements.txt
├── main.py              # Game entry point
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── game/
│   ├── player.py        # Player character, stats, movement
│   ├── world.py         # World map, respawn points, portal
│   ├── enemies.py       # Monsters, mini-bosses, final boss
│   ├── items.py         # Shards, weapons, armor, pickups
│   ├── npc.py           # Friendly NPCs, companions, shops
│   └── ui.py            # HUD, health/energy bars, menus
└── data/                # Level data, save files
```

## Coding Style
- Short, clearly named functions
- Comments explaining what AND why — an 8-year-old may be reading this!
- No cryptic variable names (no single letters except loop counters like `i`)
- Pygame coordinate system: (0,0) is top-left corner
- Target 60 FPS

## GitHub Setup
- Install GitHub CLI: https://cli.github.com/
- Authenticate: `gh auth login`
- Create the repo: `gh repo create`
- Push code: `git add . && git commit -m "message" && git push`
