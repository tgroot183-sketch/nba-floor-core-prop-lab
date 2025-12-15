import json
from pathlib import Path

from src.external_adapters.prop_model_adapter import (
    get_external_projections_for_game,
    PlayerProjection,
)
from src.core.player_filters import PlayerContext, CrashStats
from src.core.floor_engine import StatProfile, LineContext, classify_floor


def load_lines_for_game(game_key: str) -> dict:
    path = Path(__file__).resolve().parents[1] / "data_files" / "lines_input.json"
    with path.open() as f:
        all_data = json.load(f)
    return all_data[game_key]


def _analyze_game_internal(game_key: str, core_only: bool) -> list[dict]:
    game_lines = load_lines_for_game(game_key)
    projections: dict[str, PlayerProjection] = get_external_projections_for_game(game_key)

    results = []

    for p in game_lines["players"]:
        name = p["name"]
        proj = projections.get(name)
        if proj is None:
            continue

        player_ctx = PlayerContext(
            player_id=p.get("player_id", 0),
            name=name,
            team=p["team"],
            position=p["position"],
            is_rookie=p["is_rookie"],
            games_played_role=p["games_played_role"],
            minutes_season_avg=p["minutes_season_avg"],
            minutes_last10_avg=p["minutes_last10_avg"],
            injury_status=p["injury_status"],
            role_stability_flag=p["role_stability_flag"],
        )

        for m in p["markets"]:
            stat_type = m["stat_type"]

            if stat_type == "PTS":
                mean_proj = proj.pts
            elif stat_type == "REB":
                mean_proj = proj.reb
            elif stat_type == "AST":
                mean_proj = proj.ast
            elif stat_type == "RA":
                mean_proj = proj.ra
            elif stat_type == "PRA":
                mean_proj = proj.pra
            else:
                continue

            stat_profile = StatProfile(
                season_mean=m.get("season_mean", mean_proj),
                last10_mean=m.get("last10_mean"),
            )

            line_ctx = LineContext(
                stat_type=stat_type,
                main_line=m["main_line"],
                market_name=m["book"],
                odds=m.get("odds"),
            )

            crash_stats = CrashStats(
                crash_rate=m["crash_rate"],
                sample_size=m["crash_sample_size"],
            )

            floor_result = classify_floor(player_ctx, stat_profile, line_ctx, crash_stats)

            if core_only and floor_result.tier != "core_floor":
                continue

            results.append(floor_result)

    out = [
        {
            "player": r.player_name,
            "stat": r.stat_type,
            "main_line": r.main_line,
            "safe_alt": r.scout_safe_alt_line,
            "tier": r.tier,
            "notes": r.notes,
        }
        for r in results
    ]
    return out


def analyze_game(game_key: str):
    out = _analyze_game_internal(game_key, core_only=False)
    print(json.dumps(out, indent=2))


def analyze_game_core_only(game_key: str):
    out = _analyze_game_internal(game_key, core_only=True)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--game-key", type=str, required=True)
    parser.add_argument(
        "--core-only",
        action="store_true",
        help="Only show props tagged as core_floor",
    )
    args = parser.parse_args()

    if args.core_only:
        analyze_game_core_only(args.game_key)
    else:
        analyze_game(args.game_key)
