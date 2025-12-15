# NBA Floor-Core Prop Lab (Phase 1)

This is a minimal but **fully rule-based** NBA player prop engine built around **conservative alt-line floors**, not hype.

It encodes this philosophy:

- **Minutes drive everything.** If minutes are unstable, we don’t treat any line as a floor.
- Only **veterans** with **25+ games in the same role** and **stable minutes** qualify for conservative floor plays.
- One **primary role stat** per player:
  - Bigs → rebounds
  - Primary ball-handlers → assists (or RA/PRA)
  - Stable volume scorers → points (or PRA)
- Floor ≈ **20th percentile**:
  - A line they clear in roughly **80%+ of normal-minute games**.

The detailed framework lives here:

> `docs/game_research_framework.md`

---

## What Phase 1 does

- Reads a game config + prop lines from `src/data_files/lines_input.json`
- Uses (hard-coded) projections + your rules to:
  - Compute a **Scout Safe Alt Line**:
    - REB / RA: main − 2.0
    - AST: main − 1.5
    - PRA: main − 4.0
    - PTS: main − 5.0
  - Check:
    - Veteran / role / injury filters
    - How the alt line compares to season / last-10 averages
    - Crash rate (games where they land way under the alt line)

- Tags props as:
  - `core_floor` – conservative core
  - `tier2_floor` – secondary floor
  - `ceiling_only` – upside only (fails floor filters)

Phase 2 (later) can add:
- Automated stat scraping (`nba_api`)
- A small database
- ML models for projections

---

## How to run (Phase 1)

From a terminal (Replit / Codespaces), in the repo root:

```bash
python -m src.cli.run_game_analysis --game-key NYK_ORL_CUP_SEMI
python -m src.cli.run_game_analysis --game-key NYK_ORL_CUP_SEMI --core-only

python -m src.cli.run_game_analysis --game-key SAS_OKC_CUP_SEMI
python -m src.cli.run_game_analysis --game-key SAS_OKC_CUP_SEMI --core-only
```

- Without `--core-only` → shows all props & tiers.
- With `--core-only` → shows only props tagged as `core_floor`.

You can edit `src/data_files/lines_input.json` to plug in new games and lines.
