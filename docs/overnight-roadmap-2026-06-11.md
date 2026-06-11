# High Frontier overnight roadmap — 2026-06-11

This document records the Stage 03 review-gate outcome for branch `wave/2026-06-11-save-path-sim-foundation` and turns the 2026-06-10 roadmap into an ordered follow-up plan. It is intentionally conservative: preserve old saves, keep the retro Pygame application as canonical, and keep gameplay expansion out of this wave.

## Completed in this wave

### Save/load hardening

- Added `savegame.py` as the central save wrapper/name-validation module.
- New saves are pickled dictionaries with explicit metadata:
  - `format = highfrontier-save`
  - `version = 1`
  - `payload_type = solarsystem-pickle`
  - `payload = <legacy solarsystem object graph>`
- Legacy raw-pickle loads are still accepted by `unwrap_save_payload()`.
- Empty, corrupt, unsupported-version, unsupported-payload, and invalid-payload saves now fail before mutating the currently running `solarsystem` instance.
- Save writes continue to use the existing temporary-file plus atomic-replace path, now wrapping the payload before pickling.
- GUI-adjacent save/load edits stayed narrow:
  - save names are validated before saving/loading;
  - invalid/temp/reserved save entries are filtered from the load menu;
  - rejected names print a short error and do not attempt to load or save.

### Runtime paths and packaging metadata

- Added/used repository-relative path helpers for high-risk asset/data callers so selected modules can run from a non-repository current working directory.
- Added `pyproject.toml` with build metadata and runtime/dev dependencies only.
- No console scripts or forced entry points were added.

### Ocempgui cleanup

- Removed stale commented Ocempgui import remnants from active code files.
- Did not rewrite functioning widgets or perform broad GUI decomposition.
- Historical roadmap/docs may keep Ocempgui mentions as context.

### Simulation test floor and telemetry skeleton

- Added deterministic/full-initialization coverage without fixed-count snapshots: the test now compares stable aggregates across two same-seed initializations and separately checks broad core-economy invariants.
- Added xfail intended-behavior tests that document known bugs without changing behavior:
  - intercity trade profit sign;
  - research desired-ratio comparison.
- Added a telemetry skeleton on `solarsystem` with zeroed keys for stockouts, zero-stock bases, transactions, firm starts/closes, and bankruptcies.
- Instrumented only two low-risk central counters in this wave:
  - `firm_starts`;
  - `transactions`.

### Review-gate cleanup

- Reviewed diff against `origin/master` for scope compliance.
- Confirmed no browser/frontend/Pygame-in-browser/HTML work.
- Confirmed no broad `gui.py` decomposition.
- Confirmed no sections 6/7 gameplay expansion.
- Confirmed no production fix for the intercity trade profit sign.
- Reworked the initial broad exact-count snapshot into less brittle determinism/invariant tests.

## Partially completed / not completed

- Save compatibility is preserved as much as practical for raw pickle payloads, but raw pickle remains trusted-only and fragile across module/class refactors.
- Save/load errors are safer, but player-facing UX is still just console output in the narrow GUI call sites touched here.
- Path modernization is partial. Several modules still contain relative paths or import-time side effects that should be handled in focused branches.
- Telemetry currently stores counters only. There is no telemetry UI, export, persistence policy, or complete instrumentation for all declared keys.
- Crash logging, CI workflow upgrades, linting, and richer headless GUI smoke tests were not part of this wave.
- No `main()`/entry-point cleanup was attempted because clean startup boundaries are not yet proven safe.
- No gameplay economics/resource-chain changes were implemented.

## Explicitly postponed GUI/frontend section — options only, no action in this wave

The retro Pygame frontend remains the canonical UI. Do not start browser/web/frontend/Pygame-in-browser/HTML work from this branch.

Future options, in safe order:

1. `gui-save-load-ux` branch
   - Keep scope limited to save/load dialogs.
   - Convert current console-only invalid-save messages into in-game messages or a small modal using existing widgets.
   - Add dummy-SDL tests around filename validation and load-list filtering.

2. `gui-component-smoke-tests` branch
   - Add focused tests for `gui_components.fast_list`, buttons, toggles, and entry widgets.
   - Avoid pixel-perfect snapshots unless there is a small stable surface and a clear reason.
   - Fix obvious widget bugs only when a test reproduces them first.

3. `gui-pure-helper-extraction` branch
   - Extract small pure calculations from `gui.py` only when tests can pin current behavior.
   - Good candidates: base-construction cost/route calculations, list filtering, layout constants.
   - Do not split `gui.py` broadly or rename large classes in one pass.

4. Future frontend experiment branch, much later
   - Only after simulation commands/view models are separated from rendering.
   - Keep it explicitly experimental and separate from core save/simulation PRs.
   - Do not replace the Pygame UI until save compatibility and core tests are strong.

## Explicitly postponed sections 6/7 gameplay section

No sections 6/7 gameplay expansion was implemented in this wave. Specifically postponed:

- no new resource chains;
- no new base-demand goods;
- no orbital-route redesign;
- no first-class route graph/pathfinding;
- no orbital settlement/station AI;
- no space-settlement automation.

Future section 6 economics options, after the current safe-foundation work lands:

1. `data-validation-resources` branch
   - Add tests that every technology input/output/byproduct exists as a declared trade resource or documented non-stockpiled effect.
   - Document current mismatches such as terraforming and nuclear byproduct naming before changing data.

2. `economy-naming-fixes` branch
   - Fix narrow data/name mismatches with tests.
   - Avoid adding new chains in the same PR.

3. `resource-chain-prototypes` branch
   - Only after validation is green.
   - Add one small resource chain at a time, with initialization and market tests.

Future section 7 space/base/route options, after GUI and simulation seams are safer:

1. `space-base-current-behavior-tests` branch
   - Test existing `(None, None)` space-base behavior, mining restrictions, and clickable station areas.

2. `route-metadata-compat` branch
   - Add optional route metadata fields without changing existing consumers.
   - Preserve old save payloads by defaulting missing metadata on load/use.

3. `route-graph-spike` branch
   - Throwaway or draft-only spike for pathfinding/route graph design.
   - Do not merge until old route behavior has compatibility tests.

4. `orbital-visualization-tests` branch
   - Add fixtures/tests before changing how orbital routes are drawn.

## Next recommended branch order

1. Open a PR for `wave/2026-06-11-save-path-sim-foundation` after final local checks are green.
2. `ci-headless-compileall` — add/adjust CI to run dummy-SDL pytest and compileall on supported Python versions.
3. `crashlog-thread-hooks` — add top-level crash/thread logging without changing gameplay.
4. `intro-main-guard-and-paths` — make import/startup boundaries safer and continue path modernization in small slices.
5. `save-load-ux` — improve player-facing save/load error messages using existing widgets only.
6. `simulation-bug-regressions` — convert the current strict xfail tests into fixes one bug at a time, starting with intercity trade sign or research ratio, each with TDD.
7. `data-validation-resources` — add section 6 validation tests before any resource-chain changes.
8. `space-base-current-behavior-tests` — add section 7 tests before any route/orbital redesign.

## Acceptance checks for this branch

Required before final handoff:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m pytest -q
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m compileall -q -x '(.git|__pycache__|.venv|venv)' .
```

Expected status: pytest passes with the known strict xfails for intentionally documented-but-unfixed behavior; compileall exits 0.
