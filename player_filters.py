from dataclasses import dataclass


@dataclass
class PlayerContext:
    player_id: int
    name: str
    team: str
    position: str
    is_rookie: bool
    games_played_role: int
    minutes_season_avg: float
    minutes_last10_avg: float
    injury_status: str  # "healthy", "questionable", "out", "minutes_cap", "first_game_back"
    role_stability_flag: bool  # from depth chart / rotation logic


@dataclass
class CrashStats:
    """
    Crash = games where player lands WAY under the floor line
    (e.g. 2+ REB/AST or 5+ PTS below).

    crash_rate: 0–1
    sample_size: number of games checked
    """
    crash_rate: float
    sample_size: int


def is_veteran_floor_candidate(ctx: PlayerContext) -> bool:
    """
    Filters for floor candidates:
    - no rookies
    - >= 25 games in same role
    - no questionable / out / minutes_cap / first_game_back
    - stable minutes
    - stable role
    """
    if ctx.is_rookie:
        return False

    if ctx.games_played_role < 25:
        return False

    if ctx.injury_status in {"questionable", "out", "minutes_cap", "first_game_back"}:
        return False

    if ctx.minutes_season_avg < 24:
        return False

    if abs(ctx.minutes_last10_avg - ctx.minutes_season_avg) > 5:
        return False

    if not ctx.role_stability_flag:
        return False

    return True


def passes_crash_test(crash: CrashStats, max_crash_rate: float = 0.30) -> bool:
    """
    Require:
    - sample_size >= 15
    - crash_rate <= 30%
    """
    if crash.sample_size < 15:
        return False

    return crash.crash_rate <= max_crash_rate
