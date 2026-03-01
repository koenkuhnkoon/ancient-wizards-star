# Visual Upgrade Production Plan

Goal: keep gameplay 2D, but upgrade visuals to high-resolution, near-3D quality with a production pipeline that scales.

## 1. Strategy Decision (Week 0)

1. Choose engine path first.
2. Path A: Stay in `pygame` for faster short-term progress, moderate visual ceiling.
3. Path B: Migrate to Godot for long-term high-end visuals (recommended for realistic/2.5D look).
4. Decision gate output: one-page tech decision with budget, timeline, and risk.

## 2. Visual Direction Lock (Week 1)

1. Create an art bible:
   - Character style, anatomy, materials, line/outline rules.
   - Lighting setup (key/fill/rim), shadows, color grading LUT.
   - FX style (magic, impacts, portal, UI).
2. Make 6-10 reference boards and 3 target quality mockups.
3. Approval gate: team agrees on one look before producing assets.

## 3. Pipeline Build (Weeks 2-3)

1. Set target resolutions:
   - Characters: source `512x512` per pose/frame (downsample at runtime if needed).
   - Bosses: `768x768` source.
   - Items: `256x256` source.
2. Build asset pipeline scripts:
   - Exporter from Blender/Spine to sprite sheets.
   - Auto-trim, atlas packing, naming validation.
   - Optional normal-map generation for lighting.
3. Update manifest/contracts:
   - Extend `game/asset_manifest.py` for HD variants and frame metadata.
4. Add CI validation:
   - Dimension checks, alpha checks, naming checks, missing frame checks.

## 4. Runtime Rendering Upgrade (Weeks 3-5)

1. Add camera system improvements:
   - Smooth camera follow, parallax layers, screen-space shake.
2. Add lighting/post:
   - Rim lights, glow/bloom approximation, shadow blobs.
   - In Godot path: real 2D lights + shaders + normal maps.
3. Animation quality:
   - Move from tiny frame strips to larger frame sets or skeletal animation.
4. Keep gameplay unchanged while swapping visual layer APIs.

## 5. Vertical Slice (Weeks 5-6)

1. Fully polish one gameplay slice:
   - Player (Wizard), Zara, one boss arena, portal gate, portal key drop.
2. Include final-quality:
   - Character rendering, hit VFX, pickup VFX, UI polish, sound sync.
3. Approval gate:
   - If this slice looks "next-gen enough," proceed to full production.

## 6. Full Asset Production (Weeks 6-10)

1. Characters first:
   - All player classes idle/walk/attack/hurt/death.
2. Enemies and bosses second:
   - Prioritize high-frequency enemies, then bosses.
3. World tiles and props third:
   - Terrain, portal zone, interactables.
4. UI and icons last:
   - Match the same quality tier.

## 7. Optimization and Integration (Weeks 9-11)

1. Texture atlas packing and memory budget pass.
2. Load-time optimization and streaming where needed.
3. FPS and frame pacing tests on low and mid hardware.
4. Add LOD-like fallbacks if required (HD and medium variants).

## 8. QA, Polish, and Release Prep (Weeks 11-12)

1. Visual QA checklist:
   - Silhouette readability, hit clarity, animation readability.
2. Gameplay QA:
   - No collisions/offsets broken by new sprite sizes.
3. Final pass:
   - Color grading consistency scene-to-scene.
4. Release candidate sign-off.

## Milestones

1. M0: Engine/path decision approved.
2. M1: Art bible approved.
3. M2: Pipeline tools and validation working.
4. M3: Vertical slice approved.
5. M4: Full HD assets integrated.
6. M5: Performance and QA sign-off.

## Team Roles

1. Art Director: style lock and quality bar.
2. Technical Artist: Blender/Spine pipeline, export tooling.
3. Gameplay Engineer: runtime integration.
4. VFX/Lighting Artist: effects and polish.
5. QA: visual and gameplay regression checks.

## Major Risks and Mitigations

1. Risk: trying to "upscale pixel art" into realism.
   - Mitigation: create new high-res source assets, no reliance on upscaling.
2. Risk: pygame ceiling blocks desired visuals.
   - Mitigation: early decision gate for Godot migration.
3. Risk: style drift across artists.
   - Mitigation: strict art bible + weekly review.
4. Risk: performance drops with HD art.
   - Mitigation: atlases, compression, budget enforcement from week 3.

## Immediate Next 5 Actions

1. Run a 2-hour decision workshop: `pygame` vs `Godot`.
2. Freeze target art quality with 3 approved benchmark images.
3. Build and test one export toolchain (Blender -> sprite sheet).
4. Upgrade only Wizard + Zara + portal key as proof of quality.
5. Review vertical slice before committing full production.

## Execution Checklist

- [ ] Confirm engine direction (`pygame` or `Godot`) with owner and date.
- [ ] Create and approve art bible.
- [ ] Implement exporter + atlas + validation scripts.
- [ ] Build vertical slice and run review.
- [ ] Greenlight full asset production.
- [ ] Complete optimization pass and QA sign-off.
