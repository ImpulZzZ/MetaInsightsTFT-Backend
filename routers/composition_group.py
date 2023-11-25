import settings

from core.models.group_compositions import group_compositions_by_champions, group_compositions_by_traits

from datetime import datetime
from fastapi import Query, APIRouter
from typing import Optional

settings.init()
router = APIRouter()

@router.get("/compositionGroup/by-trait")
def composition_group_by_trait(
    trait_name: Optional[str] = Query(default = None, description="Name of the trait to get compositions for. If left blank, all compositions are returned"),
    combination_size: Optional[int] = Query(default=None, description="Number of traits to group by. If left blank, all traits are returned", ge=1, le=7),
    ignore_single_unit_traits: Optional[bool] = Query(default=False, description="Ignored traits, that are unique to one champion"),
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    max_avg_placement: Optional[float] = settings.MAX_AVG_PLACEMENT_QUERY,
    min_counter: Optional[int] = settings.MIN_COUNTER_QUERY,
    patch: Optional[str] = settings.PATCH_QUERY,
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_traits(patch, region, league, max_placement, max_avg_placement, min_counter, min_datetime, trait_name, combination_size, ignore_single_unit_traits)


@router.get("/compositionGroup/by-champion")
def composition_group_by_champion(
    champion_name: Optional[str] = Query(default = None, description="Name of the champion to get compositions for. If left blank, all compositions are returned"),
    combination_size: Optional[int] = Query(default=None, description="Number of champions to group by. If left blank, all champions are returned. Limited to 1-2 due to long computation with > 2", ge=1, le=2),
    max_placement: Optional[int] = settings.MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = settings.MIN_COUNTER_QUERY,
    patch: Optional[str] = settings.PATCH_QUERY,
    region: Optional[str] = settings.REGION_QUERY,
    league: Optional[str] = settings.LEAGUE_QUERY,
    min_datetime: Optional[datetime] = settings.MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_champions(patch, region, league, max_placement, min_counter, min_datetime, champion_name, combination_size)