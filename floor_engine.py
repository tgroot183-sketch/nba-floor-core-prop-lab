from dataclasses import dataclass
from typing import Optional, Literal

from src.core.player_filters import (
    PlayerContext,
    CrashStats,
    is_veteran_floor_candidate,
    passes_crash_test,
)


StatType = Literal["PTS", "REB", "AST", "RA", "PRA"]
TierTag = Literal["core_floor", "tier2_floor", "ceiling_only", "avoid"]


@dataclass
class StatProfile:
    season_mean: float
    last10_mean: Optional[float] = None


@dataclass
class LineContext:
    stat_type: StatType
    main_line: float
    market_name: str  # e.g. "DK", "FD"
    odds: Optional[str] = None


@dataclass
class FloorResult:
    player_name: str
    stat_type: StatType
    main_line: float
    scout_safe_alt_line: float
    tier: TierTag
    notes: str


def compute_safe_alt_line(stat_type: StatType, main_line: float) -> float:
    """
    Alt-line rules:

    - REB / RA: main - 2.0
    - AST: main - 1.5
    - PRA: main - 4.0
    - PTS: main - 5.0
    """
    if stat_type in {"REB", "RA"}:
        return main_line - 2.0
    if stat_type == "AST":
        return main_line - 1.5
    if stat_type == "PRA":
        return main_line - 4.0
    if stat_type == "PTS":
        return main_line - 5.0
    raise ValueError(f"Unsupported stat_type: {stat_type}")


def classify_floor(
    player_ctx: PlayerContext,
    stat_profile: StatProfile,
    line_ctx: LineContext,
    crash_stats: CrashStats,
) -> FloorResult:
    alt_line = compute_safe_alt_line(line_ctx.stat_type, line_ctx.main_line)

    # 1) vet / role / health filters
    if not is_veteran_floor_candidate(player_ctx):
        return FloorResult(
            player_name=player_ctx.name,
            stat_type=line_ctx.stat_type,
            main_line=line_ctx.main_line,
            scout_safe_alt_line=alt_line,
            tier="ceiling_only",
            notes="Fails veteran/role/health filters; treat as upside only.",
        )

    # 2) check averages: safe alt should be at or below season/last10
    mean_ref = stat_profile.season_mean
    if stat_profile.last10_mean is not None:
        mean_ref = min(mean_ref, stat_profile.last10_mean)

    if alt_line > mean_ref:
        return FloorResult(
            player_name=player_ctx.name,
            stat_type=line_ctx.stat_type,
            main_line=line_ctx.main_line,
            scout_safe_alt_line=alt_line,
            tier="ceiling_only",
            notes="Alt line still above averages; not a conservative floor.",
        )

    # 3) crash test (20th percentile idea)
    if not passes_crash_test(crash_stats):
        return FloorResult(
            player_name=player_ctx.name,
            stat_type=line_ctx.stat_type,
            main_line=line_ctx.main_line,
            scout_safe_alt_line=alt_line,
            tier="ceiling_only",
            notes="Crash rate too high for a true floor (>30%).",
        )

    # 4) decide between core_floor vs tier2_floor
    margin = mean_ref - alt_line

    if margin >= 2.0 and crash_stats.crash_rate <= 0.20:
        tier: TierTag = "core_floor"
        notes = "Strong margin vs averages and low crash rate; core floor candidate."
    else:
        tier = "tier2_floor"
        notes = "Passes filters but with thinner margin or higher crash; secondary floor."

    return FloorResult(
        player_name=player_ctx.name,
        stat_type=line_ctx.stat_type,
        main_line=line_ctx.main_line,
        scout_safe_alt_line=alt_line,
        tier=tier,
        notes=notes,
    )
