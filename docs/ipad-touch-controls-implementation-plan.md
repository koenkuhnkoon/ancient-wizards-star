# iPad Browser Touch Controls Plan (Full Touch Parity, Joystick, Landscape+Portrait)

## Summary

Implement a complete touch input/UI layer so the game is playable on iPad Safari without a keyboard, including:

1. In-game movement/attack/interact/pause touch controls.
2. Touch-enabled character selection, story continue, pause/options, summon interaction, portal interaction, and victory/game-over exits.
3. Responsive layout for both landscape and portrait iPad orientations.
4. Keyboard controls remain fully supported.

This plan targets `main.py` first (single-loop input architecture), with minimal gameplay logic changes and clear separation between input state and game actions.

## Scope and Success Criteria

### In scope

1. Virtual joystick for movement.
2. Touch buttons for `Attack`, `Interact`, and `Pause`.
3. Context-sensitive `Interact` behavior for Summoner and Portal.
4. Tap support on character select, story intro continue, pause/options actions, victory/game-over exit.
5. Responsive control placement for landscape + portrait.
6. Coexistence with keyboard input.

### Out of scope (for this implementation)

1. Major UI art redesign.
2. Engine migration or DOM-over-canvas UI.
3. Advanced gesture controls (swipe combos, pinch zoom).

### Success criteria

1. iPad user can complete full flow: choose character -> play -> summon helper -> open portal -> enter arena -> finish run, all via touch.
2. No keyboard required on iPad.
3. Existing desktop keyboard behavior unchanged.
4. 60 FPS target preserved (no per-frame heavy allocations).

## Implementation Design

## 1) Add Touch Input Layer in `main.py`

Create a small touch controller subsystem near helper classes/functions.

### New data structures

1. `TouchButton` (rect, label, action_id, visible/enabled).
2. `TouchJoystick` (center, radius, knob pos, active finger id, vector output).
3. `TouchUIState` (active touch ids, button pressed flags, joystick vector, orientation, layout metrics).

### New helper functions

1. `get_orientation(screen_w, screen_h) -> "landscape" | "portrait"`.
2. `build_touch_layout(screen_w, screen_h, orientation) -> dict`  
   Returns precomputed `pygame.Rect`/centers for joystick + buttons.
3. `draw_touch_controls(screen, touch_state, fonts)`  
   Draw joystick base/knob + buttons with press feedback.
4. `handle_touch_event(event, touch_state, layout)`  
   Handles `FINGERDOWN`, `FINGERMOTION`, `FINGERUP`, and optional `MOUSEBUTTON*` debug mapping.
5. `consume_touch_actions(touch_state) -> dict`  
   Returns one-frame actions: `attack_pressed`, `interact_pressed`, `pause_pressed`, and movement vector.

### Input mapping rules

1. Joystick controls move direction continuously.
2. Attack button triggers same action path as `Space` key.
3. Interact button triggers same path as `E` key (summoner/portal context).
4. Pause button toggles same as `P`.
5. Touch actions are edge-triggered where keyboard is edge-triggered (attack/interact/pause).

## 2) Integrate Touch Movement into Player Update

Current movement uses `keys_pressed = pygame.key.get_pressed()` and `player.handle_input(keys_pressed)`.

### Integration strategy

1. Keep keyboard path unchanged.
2. Add a new helper to synthesize movement intent from keyboard + joystick:
   - `dx`, `dy`, `running` resolved each frame.
3. Implement one of:
   - `player.handle_input_with_vector(dx, dy, running)` (preferred small extension in `game/player.py`), or
   - lightweight compatibility adapter in `main.py` if avoiding player API change.
4. Running behavior for joystick:
   - Default walk speed.
   - Optional "outer ring" threshold (e.g., >80% joystick displacement) sets running.

### Chosen default

Use joystick magnitude threshold to trigger running automatically.

## 3) Full Touch Parity for Menus and Overlay Flows

Add tappable UI hit-zones in the same render loops already used for text screens.

### Character selection (`run_character_selection`)

1. Render six large tap cards/rows.
2. Tap card selects class.
3. Add explicit tappable `Quit` area.

### Story intro (`run_story_intro`)

1. Full-screen tap advances to next panel (same as Enter/Space).

### Pause/options (`draw_pause_overlay` + event logic)

1. Add tappable rows/buttons:
   - `Resume`
   - `Audio ON/OFF`
   - `Main Menu`
2. Keep keyboard up/down/enter path.

### Victory/Game over screens

1. Add full-width tappable button: `Return to Menu`.
2. Keep Space/ESC.

## 4) Context-Sensitive Interact UX

Replace keyboard-only discoverability with touch-context prompts.

### Runtime behavior

1. If near Summoner: show `Summon` or `Activate` interact button text.
2. If near portal with key: show `Enter Portal`.
3. If both valid simultaneously (rare), priority:
   - Summoner first if within range and not exhausted.
   - Else portal.
4. `Interact` touch button hidden/disabled when no valid target.

### Prompt rendering

1. Keep existing text hints.
2. Add touch label near button (`Summon`, `Activate`, `Enter`).

## 5) Responsive Layout (Landscape + Portrait)

Build two layout presets in `build_touch_layout`.

### Landscape preset

1. Joystick bottom-left.
2. Attack bottom-right (largest button).
3. Interact above/right of attack.
4. Pause top-right small button.

### Portrait preset

1. Joystick lower-left, slightly higher to avoid browser bars.
2. Attack lower-right.
3. Interact above attack.
4. Pause top-right.

### Safe margins

1. Use relative sizing from `SCREEN_WIDTH/SCREEN_HEIGHT`.
2. Keep at least 16 px edge padding.
3. Minimum touch target size: 72 px.

## 6) Performance and Stability Constraints

1. Precreate static button surfaces where possible.
2. Avoid creating new `Surface` objects inside per-frame draw loops.
3. Maintain keyboard behavior exactly.
4. Touch and keyboard can coexist without double-triggering.

## Files and Interface Changes

## `main.py` (primary)

1. Add touch controller classes/state/helpers.
2. Add finger/mouse-touch event handling in event loop.
3. Add touch action dispatch mapped to existing keyboard action code paths.
4. Add touch-aware movement integration.
5. Add menu tap hit testing for character select/story/pause/victory/game-over.
6. Add contextual interact button logic and rendering.
7. Add `draw_touch_controls(...)` call during gameplay draw pass.

## `game/player.py` (small extension)

1. Add optional vector-based movement method or equivalent extension for joystick input.
2. Preserve existing `handle_input(keys_pressed)` behavior.
3. Keep animation state transitions aligned with movement intent.

No breaking API changes expected for other modules.

## Testing Plan

## A) Manual functional tests (desktop emulator + iPad Safari)

1. Character select: tap each class; starts correct class.
2. Story intro: tap to advance panels.
3. Overworld movement: joystick moves in 8 directions; run threshold works.
4. Attack: tap attack button triggers cooldown/hit effects exactly once per press.
5. Summoner: approach and tap interact; summon/activate flow works.
6. Portal: with key and in range, tap interact enters arena.
7. Pause: pause button opens menu; tap resume/audio/menu works.
8. Victory/Game over: tap return works.
9. Orientation change: portrait/landscape controls reposition and remain usable.
10. Keyboard regression: all existing key controls still work.

## B) Edge-case scenarios

1. Multi-touch: hold joystick + tap attack simultaneously.
2. Finger leaves screen abruptly: joystick resets safely.
3. Interact spam near summoner/portal: no duplicate invalid state transitions.
4. Pause while moving with joystick: movement halts correctly.
5. Touch + keyboard mixed input: no double actions.

## C) Acceptance criteria checklist

1. No keyboard required on iPad.
2. Full touch parity across requested screens/features.
3. No crashes from touch events.
4. Playable at target FPS.

## Rollout / Deployment Notes

1. After code changes, rebuild pygbag bundle and publish updated `docs/` artifacts.
2. Verify deployed GitHub Pages build reflects new bundle (hard refresh and service worker cache check).
3. Add release note: "Touch controls enabled for iPad."

## Assumptions and Defaults

1. Keep game logic single-threaded and event-driven in current `main.py`.
2. Use virtual joystick (chosen).
3. Support both landscape and portrait in first release (chosen).
4. Implement full touch parity for key menus/interactions (chosen).
5. Running is joystick-magnitude based (default).
6. Touch UI visual style uses existing color language; no new art dependency required.
