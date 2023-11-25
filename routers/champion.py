import settings

from core.models.get_bis_items import get_best_in_slot_items
from core.models.get_placements import get_champion_placements
from core.models.get_static_data import get_icons

from datetime import datetime
from fastapi import Query, Path, APIRouter
from typing import Optional

settings.init()
router = APIRouter()

@router.get("/champion/placements")
def champion_placements(
    champion_name: Optional[str] = Query(default = None, description="Name of the champion to get placements for. If left blank, all champions are returned"),
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
    ):
    return get_champion_placements(champion_name, region, league, max_placement, min_datetime)


@router.get("/champion/{champion_name}/items")
def champion_items(
    champion_name: Optional[str] = Path(description="Name of the champion to get best in slot items for. If left blank, all champions are returned"),
    combination_size: Optional[int] = Query(default=3, description="Size of item combinations for each champion", ge=1, le=3),
    patch: Optional[str] = settings.PATCH_QUERY,
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = settings.MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
    ):

    return get_best_in_slot_items(champion_name, combination_size, patch, region, league, max_placement, min_counter, min_datetime)


@router.get("/champion/icons")
def champion_icons(
    name: Optional[str] = Query(default = None, description="Name of the champion to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the champion to get icon path for")
):
    return get_icons(name, display_name, "champion")