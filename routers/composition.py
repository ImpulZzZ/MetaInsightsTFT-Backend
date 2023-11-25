import settings

from core.models.get_compositions import get_compositions
from core.models.load_compositions import load_compositions

from fastapi import Query, APIRouter
from typing import Optional
from datetime import datetime

settings.init()
router = APIRouter()

@router.get("/composition/get-data")
def composition_get_data(
    composition_id: Optional[int] = Query(default=None, description="Considers only compositions with this id"),
    match_id: Optional[str] = Query(default=None, description="Considers only compositions from this match"),
    patch: Optional[str] = settings.PATCH_QUERY,
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY
    ):
    return get_compositions(composition_id, match_id, patch, region, league)


@router.post("/composition/load-data")
def composition_load_data( region: Optional[str] = settings.REGION_QUERY,
                           players_amount: Optional[int] = Query(default = 5, description="Load this many players", ge=0, le=200),
                           games_per_player: Optional[int] = Query(default = 5, description="Load this many games of each player", ge=0, le=50),
                           current_patch: Optional[str] = settings.PATCH_QUERY,
                           ranked_league: Optional[str] = settings.LEAGUE_QUERY,
                           min_datetime: Optional[datetime] = Query(default = settings.five_days_ago, description="Load only matches that happened after this time")
                           ):
    start_time = datetime.now()
    stored_matches = load_compositions(region, players_amount, games_per_player, current_patch, ranked_league, min_datetime)
    if stored_matches is None: return {"Error": "Data could not be loaded"}
    seconds = (datetime.now() - start_time).seconds
    return {"Success": f"Data from {stored_matches} matches was loaded successfully in {seconds} seconds"}