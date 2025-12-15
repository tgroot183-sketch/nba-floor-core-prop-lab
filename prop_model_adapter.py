from dataclasses import dataclass
from typing import Dict


@dataclass
class PlayerProjection:
    pts: float
    reb: float
    ast: float

    @property
    def ra(self) -> float:
        return self.reb + self.ast

    @property
    def pra(self) -> float:
        return self.pts + self.reb + self.ast


ProjectionMap = Dict[str, PlayerProjection]  # key = player name


def get_external_projections_for_game(game_key: str) -> ProjectionMap:
    """
    TEMP: Hard-coded projections for our two example games.

    In Phase 2, this is where you'll call a real ML model or external repo.
    """
    if game_key == "NYK_ORL_CUP_SEMI":
        return {
            "Jalen Brunson": PlayerProjection(pts=29.0, reb=3.0, ast=7.0),
            "Karl-Anthony Towns": PlayerProjection(pts=20.0, reb=13.0, ast=3.0),
            "Desmond Bane": PlayerProjection(pts=24.0, reb=5.0, ast=4.0),
            "Paolo Banchero": PlayerProjection(pts=21.0, reb=7.0, ast=4.0),
        }

    if game_key == "SAS_OKC_CUP_SEMI":
        return {
            "Victor Wembanyama": PlayerProjection(pts=21.0, reb=10.0, ast=3.0),
            "De'Aaron Fox": PlayerProjection(pts=22.0, reb=4.0, ast=7.0),
            "Shai Gilgeous-Alexander": PlayerProjection(pts=31.5, reb=5.0, ast=7.0),
            "Jalen Williams": PlayerProjection(pts=18.0, reb=5.0, ast=6.0),
        }

    return {}
