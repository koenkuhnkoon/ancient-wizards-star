# The Ancient Wizard's Star — AI Development Team

This folder contains five AI agents that help build the game. Dad runs them and reviews
everything before it goes into the actual game files.

## The Five Agents

| Agent | What it does | Output file |
|---|---|---|
| **Story & Design Lead** | Writes the game's story, characters, quests, and NPC dialogues | `output/story_design.md` |
| **Graphic Designer** | Writes the art style guide, color palettes, and sprite size specs | `output/art_guide.md` |
| **Programmer** | Writes Python/Pygame code for each game file | `output/game_<filename>.md` |
| **QA Reviewer** | Reviews code for quality and gives git commands to commit | `output/code_review.md` |
| **Sound Designer** | Plans every music track and sound effect, with filenames and trigger conditions | `output/sound_design.md` |

## Setup (one-time)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get an Anthropic API key

- Go to https://console.anthropic.com and sign up or log in
- Create an API key
- Create a file called `.env` in the **project root** (the `Bakuriani Game/` folder):

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

The `.gitignore` already excludes `.env` so your key will never be committed to GitHub.

### 3. Test the setup

```bash
python agents/orchestrator.py --phase design
```

If it works, you will see the agents running and two files will appear in `agents/output/`.

---

## How to Use the Agents

### Step 1: Design Phase (run once at the start)

Runs the Story Lead and Graphic Designer together to create the game's design foundation.

```bash
python agents/orchestrator.py --phase design
```

Review `agents/output/story_design.md` and `agents/output/art_guide.md`.
When you are happy with them, copy them to `docs/`:

```bash
# On Windows (in Git Bash or PowerShell):
cp agents/output/story_design.md docs/story_design.md
cp agents/output/art_guide.md docs/art_guide.md
```

### Step 2: Code Phase (run for each game file)

Tells the Programmer which file to write. It will read the story and art docs automatically.

```bash
python agents/orchestrator.py --phase code --file main.py
python agents/orchestrator.py --phase code --file game/player.py
python agents/orchestrator.py --phase code --file game/enemies.py
python agents/orchestrator.py --phase code --file game/world.py
python agents/orchestrator.py --phase code --file game/items.py
python agents/orchestrator.py --phase code --file game/npc.py
python agents/orchestrator.py --phase code --file game/ui.py
```

The code will appear in `agents/output/` as a `.md` file with Python code inside.
Copy the Python code from the markdown into the actual game file when you are ready.

You can also give the Programmer extra instructions with `--task`:

```bash
python agents/orchestrator.py --phase code --file game/player.py \
  --task "Focus on the movement system. The player should walk and run."
```

### Step 3: Review Phase (run after each code file)

The QA Reviewer checks the most recently generated code file.

```bash
python agents/orchestrator.py --phase review
```

Or review a specific file:

```bash
python agents/orchestrator.py --phase review --file game/player.py
```

The review will appear in `agents/output/code_review.md`. It includes:
- A pass/fail summary
- Any bugs or style issues found
- A kid-readability score (1–10)
- The exact git commands to commit the code

### Step 4: Sound Phase (run once the story is ready)

The Sound Designer reads the story design doc and produces a complete sound plan —
every music track and sound effect the game needs, with filenames, style notes, and
trigger conditions.

```bash
python agents/orchestrator.py --phase sound
```

Creates `agents/output/sound_design.md` — full plan for music tracks and sound effects.

Review the file and copy it to `docs/` when you are happy with it:

```bash
cp agents/output/sound_design.md docs/sound_design.md
```

### Step 5: Commit (after reviewing the report)

Copy the git commands from the review report and run them. Example:

```bash
git status
git add game/player.py
git commit -m "feat(player): add movement and health system"
git push origin master
```

---

## Full Pipeline (quick start)

To run everything at once (design + write main.py + review):

```bash
python agents/orchestrator.py --phase all
```

---

## Folder Structure

```
agents/
├── orchestrator.py      ← The main script — run this
├── README.md            ← This file
├── prompts/
│   ├── story_lead.md       ← Instructions for the Story & Design Lead
│   ├── graphic_designer.md ← Instructions for the Graphic Designer
│   ├── programmer.md       ← Instructions for the Programmer
│   ├── qa_reviewer.md      ← Instructions for the QA Reviewer
│   └── sound_designer.md   ← Instructions for the Sound Designer
└── output/
    └── (agent output files appear here — reviewed by dad before use)

docs/
    └── (approved design docs live here — copy from output/ after reviewing)
```

## Tips for Koen and Dad

- Always **review before copying** — the AI is helpful but not perfect!
- The Programmer writes code that Koen can understand — if something is confusing, ask the QA Reviewer to improve it using the `--task` flag
- You can edit the files in `agents/prompts/` to change how each agent behaves
- Re-run any phase as many times as you like — each run creates a fresh output file
