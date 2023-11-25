import settings

from core.models.get_placements import get_item_placements
from core.models.get_static_data import get_icons, get_item_names

from datetime import datetime
from fastapi import Query, APIRouter
from typing import Optional

settings.init()
router = APIRouter()

@router.get("/item/placements")
def item_placements(
    item_name: Optional[str] = Query(default = None, description="Name of the item to get placements for. If left blank, all items are returned" ),
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    min_counter: Optional[int] = settings.MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
    ):
    
    return get_item_placements(item_name, region, league, max_placement, min_counter, min_datetime)


@router.get("/item/icons")
def item_icons(
    name: Optional[str] = Query(default = None, description="Name of the item to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the item to get icon path for")
):
    return get_icons(name, display_name, "item")


@router.get("/item")
def item_names(patch: Optional[str] = settings.PATCH_QUERY):
    return get_item_names(patch)