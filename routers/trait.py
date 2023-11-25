import settings

from core.models.get_placements import get_trait_placements
from core.models.get_static_data import get_icons, get_trait_names

from datetime import datetime
from fastapi import Query, APIRouter
from typing import Optional

settings.init()
router = APIRouter()

@router.get("/trait/placements")
def trait_placements(
    trait_name: Optional[str] = Query(default = None, description="Name of the trait to get placements for. If left blank, all traits are returned"),
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
):
    return get_trait_placements(trait_name, region, league, max_placement, min_datetime)


@router.get("/trait/icons")
def trait_icons(
    name: Optional[str] = Query(default = None, description="Name of the trait to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the trait to get icon path for")
):
    return get_icons(name, display_name, "trait")


@router.get("/trait")
def trait_names(patch: Optional[str] = settings.PATCH_QUERY):
    return get_trait_names(patch)