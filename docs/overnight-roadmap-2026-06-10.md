# High Frontier overnight roadmap — 2026-06-10

This roadmap was produced from a read-through and smoke-test pass over the current `master` branch (`788f746`).  It is intended as an executable wishlist for future agents/contributors, with safe work separated from risky gameplay changes.

## Ground rules

- Preserve the grainy/retro Pygame graphics and controls unless a branch is explicitly a frontend experiment.
- Do not rewrite or repackage the whole game before save compatibility, CI, and core simulation tests are stronger.
- Keep raw-pickle save compatibility while staging a versioned format behind it.
- Prefer focused branches/PRs over broad rewrites.

## Current architecture map

- `intro.py` — intro/menu flow; currently starts `IntroGui()` at import time.
- `main.py` — main Pygame loop, event dispatch, creates `solarsystem`, `gui.gui`, and `SimThread`.
- `solarsystem.py` — global state, planet/company initialization, monthly/yearly world tick, save/load, solar-system drawing.
- `planet.py` — planet data, atmosphere/water/topography/resource maps, projections, base/station rendering.
- `company.py` — companies, bases, firms, markets, base construction, merchants, research firms.
- `market_decisions.py` — AI strategy tables for bidding, firm startup, trade, research, asset/tech markets.
- `technology.py` — XML-backed dynamic technology tree generation and drawing.
- `gui.py` — large Pygame GUI/window controller.
- `gui_components.py` — custom retro widgets: buttons, toggles, scrollbars, entries, lists.
- `data/economy/*.txt`, `data/technology/technology.txt`, `data/planets.txt`, `data/base_data/*.txt` — data-driven simulation definitions.
- `tests/` — current pytest coverage for initialization, save/load, projection math, planet/resource behavior.

## Track findings and recommended work

### 1. Architecture modernization

Findings:

- Python 3.10+ is now required because `main.py` and `gui.py` use `match/case`.
- `setup.py` is a legacy `py2exe` script and is not a usable modern package entry point.
- Runtime asset/data paths are mostly relative to the current working directory (`global_variables.py`, `intro.py`, `main.py`, `planet.py`, `solarsystem.py`, `technology.py`).
- `intro.py` starts the game at import time, which blocks ordinary import tests/tooling.
- Ocempgui is no longer an active dependency, but stale/commented remnants remain in `gui_components.py`, `planet.py`, `primitives.py`, and dead GUI code paths.

Safe PRs:

1. Guard `intro.py` with `if __name__ == "__main__":` while preserving `python intro.py` behavior.
2. Add an `asset_path()`/`data_path()` helper and convert the highest-risk paths first.
3. Add `pyproject.toml` metadata only after deciding what to do with legacy `setup.py`.
4. Remove dead Ocempgui comments/code only after reference searches show it is unused.

### 2. UI/code polish

Findings:

- The retro UI is mostly custom Pygame widgets, not Ocempgui.
- `gui.py` is monolithic and contains repeated panel drawing, hard-coded layout constants, and several likely layout bugs.
- `gui_components.fast_list` contains Python-2-style comparison sorting that can fail when clicking sortable table headers.
- `global_variables.py` loads fonts at import time from relative paths.

Safe PRs:

1. Add smoke tests for `gui_components` widgets using dummy SDL.
2. Extract panel colors/layout constants without changing pixels.
3. Fix `fast_list` sorting with regression tests.
4. Add a top-level FPS cap/debug flag only after measuring current behavior.

Longer-term:

- Keep Pygame as canonical frontend.
- Separate simulation commands/view models from renderer before considering a web/canvas/app frontend.

### 3. Save-game reliability

Findings:

- `solarsystem.save_solar_system()` pickles the live object graph and mutates PIL image attributes before pickling.
- Old code used removed Pillow APIs (`Image.tostring`, `Image.fromstring`) for topography/water images.
- Existing save writes directly to the target file, so interruption can destroy the only good save.
- `load_solar_system()` copied attributes from `dir()`, which can copy bound methods and internals.
- Planet back-reference reset had a typo: `solars_system_object_link` vs `solar_system_object_link`.
- `savegames/emptyfile` is listed as loadable by simple `os.listdir` UI paths.

Safe PRs:

1. Modernize PIL byte conversion and add regression tests for loaded topography/resource maps.
2. Write saves to a temp file and atomically replace the final save.
3. Reject empty/path-traversal save names in GUI helper code.
4. Add save metadata/version wrapper while continuing to load raw legacy pickles.
5. Add corrupt/empty save tests and exclude `savegames/emptyfile` from load menus.

### 4. Crash/error logging

Findings:

- Most failures currently surface only as console tracebacks or `print()` calls.
- `main.py` and `intro.py` event loops lack a top-level crash wrapper.
- `SimThread.run()` has no exception capture; a daemon-thread crash can silently stop simulation while the UI continues.
- `gui.py` sets global `logging.basicConfig(level=logging.DEBUG)` at import time but does not configure file logs.

Safe PRs:

1. Add `crashlog.py` with rotating file logging in a user state/log directory, overridable by `HIGHFRONTIER_LOG_DIR`.
2. Install `sys.excepthook` and `threading.excepthook` at startup.
3. Add `solarsystem.add_message(text, type=...)` to bridge in-game messages and stdlib logging.
4. Wrap the outer event loop and central widget activation points with contextual logging.

Suggested log fields:

- timestamp, level, thread name, module
- full traceback
- display mode, current date, current planet/base/company if available
- active GUI window and pygame event repr
- save/load filename where relevant

### 5. Company AI and initial world state

Findings:

- `company_database` is a genome-like bag of 1–100 behavioral genes.
- Only Denmark, Sweden, and USA have explicit country genomes in `data/economy/companies.txt`; most countries inherit USA behavior.
- New yearly companies clone rich-company genomes without mutation.
- Base starting stocks are roughly one 30-day consumption round, making early stockpiles hit zero quickly.
- Initial company/firms are very noisy: about 500 companies × 15 basic technologies = 7,500 non-base firms in a fresh world.
- `solarsystem.initialize_companies()` appears to size initial firms using a stale `home_city` variable rather than the target location.
- `market_decisions.evaluate_intercity_trade_market_01()` likely has an inverted profit margin sign.
- Research ratio comparisons appear inconsistent (`0..1` ratio compared with `1..100` gene).

Safe PRs:

1. Add deterministic initialization snapshot tests with a fixed seed.
2. Add tests for gene bounds and strategy-selector mapping.
3. Fix stale `home_city` firm-sizing bug with a focused regression test.
4. Add telemetry counters for stockouts, firm starts/closes, bankruptcies, transaction count, and zero-stock bases.

Medium-risk PRs:

1. Add configurable bootstrap constants for initial stock months, firm input/output stock, and live market offers.
2. Add mutation/crossover when creating offspring companies, preserving the evolutionary spirit.
3. Make firm-start decisions price/input/capital aware.
4. Fix intercity trade profitability only with regression tests.

### 6. Economics/product areas

Findings:

- `data/economy/trade resources.txt` has 18 resources.
- Base-demand goods are currently: `food`, `housing`, `health care`, `education`, `consumer goods`.
- `ice` and `silicium` are declared but unused by current technology processes.
- `oxygen` and `nitrogen` are consumed by terraforming but not produced.
- `terraforming` is produced by a technology but is not declared as a trade resource.
- Nuclear byproduct code checks for `fission source`, while the data uses `nuclear fuel`.

Safe data/test PRs:

1. Add a data validation test: every technology input/output must exist in `trade resources.txt`.
2. Either declare `terraforming` or convert terraforming to a non-stockpiled planet effect later.
3. Add initial resource chains that use existing unused resources:
   - `ice + power + labor -> water` or `oxygen`
   - `power + labor -> nitrogen` via atmospheric separation
   - `silicium + power + labor -> electronics`
4. Fix nuclear byproduct naming with tests.

Medium-risk design:

- Add terrain-conditioned demand so Earth cities do not immediately demand life-support goods, but space/Moon/Mars settlements do.
- Add `water`, `life support`, `habitat modules`, `medical supplies`, and `radiation shielding` in stages.

### 7. Space/base/trade routes

Findings:

- Space bases already exist as `position_coordinate == (None, None)` and `terrain_type == "Space"` in `company.base`.
- Base construction can already create orbit bases and interplanetary bases via `gui.construct_base_menu` and `company.base_construction`.
- Trade routes are dicts embedded in bases, not first-class assets.
- There is no route graph/pathfinding; merchants only use direct `base.trade_routes`.
- Space routes are mostly economic, not well visualized: `planet.draw_trade_network()` skips space endpoints.
- Orbital bases have no persistent metadata for LEO/GEO/LLO/LMO/Lagrange/station class.

Safe PRs:

1. Add tests for existing space-base behavior: `(None, None)` -> `Space`, no mining, station clickable areas.
2. Add optional route metadata fields without changing old route consumers.
3. Extract base-construction route/cost calculation from `gui.py` into a pure helper with tests that preserve current outputs.
4. Add orbital-route drawing tests/fixtures before changing visualization.

Medium-risk roadmap:

1. Formalize orbital stations while treating old `Space` bases as legacy generic orbit.
2. Add route classes: surface-to-surface, surface-to-orbit, orbit-to-orbit, orbit-to-surface, interplanetary.
3. Add orbital gateway chains: Earth surface → LEO → lunar/Martian orbit → surface.
4. Add route graph/pathfinding and route construction as pending assets.
5. Teach AI to build space-transport production, stations, and staged settlements.

### 8. CI/tests

Findings:

- `.github/workflows/pytest_runs.yml` exists, but only tests Python 3.10 and uses older GitHub Actions.
- Existing workflow sets `PYTHONPATH`, which is currently necessary for flat imports.
- Headless SDL env vars are not set in CI.
- `setup.py` imports `py2exe`, so do not use `pip install -e .` until packaging is modernized.

Safe PRs:

1. Expand CI to Python 3.10/3.11/3.12 on Linux/macOS/Windows.
2. Add `python -m compileall` as a syntax smoke check.
3. Add `pytest.ini` and `tests/conftest.py` for headless pygame defaults.
4. Add `.gitignore` entries for `.venv/`, `.pytest_cache/`, `__pycache__/`.

## Recommended inspection order

1. CI/test hygiene branch — safest and establishes the test floor.
2. Save/load image compatibility branch — directly addresses finicky saves with a regression test.
3. This roadmap/spec branch — use it to plan future focused work.
4. Next safe code PRs: `intro.py` import guard, asset path helper, crashlog module.
5. Then gameplay PRs: initial-world stock/sizing tests, trade profitability test, data validation/economics resources, orbital station metadata.

## Acceptance checks for future PRs

Baseline:

```bash
python -m pip install -r requirements.txt
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 python -m pytest -q
python -m compileall -q -x "(.git|__pycache__)" .
```

Add/maintain tests for:

- save/load after topography/resource maps are loaded
- corrupt/empty save handling
- transaction conservation and no negative stock/capital
- deterministic initialization snapshots
- intercity trade profitability sign
- base construction and reciprocal routes
- space-base metadata/rendering
- data schema consistency for resources/technology

## Known limitations from this pass

- The game is still a flat-module Pygame application; packaging/import modernization should be staged carefully because pickle saves encode module paths.
- Raw pickle saves remain trusted-only and fragile across refactors.
- The current test suite is valuable but still light relative to the simulation surface area.
- Runtime UI smoke beyond headless initialization was not automated.
