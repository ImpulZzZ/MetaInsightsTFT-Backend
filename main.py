from fastapi import FastAPI, Query
from typing import Optional

from core.models.mysql_utils import *
from core.models.load_compositions import *
from core.models.get_compositions import *
from core.models.group_compositions import *
from core.models.get_placements import *
from core.models.get_static_data import *

from datetime import datetime, timedelta

app = FastAPI()

five_days_ago     = datetime.now() - timedelta(days=5)
fourteen_days_ago = datetime.now() - timedelta(days=14)

MAX_AVG_PLACEMENT_QUERY = Query(default=4,                 description="Considers only composition groups, which average placements are lower or equal this value", ge=1, le=8)
MAX_PLACEMENT_QUERY     = Query(default=4,                 description="Considers only compositions, which placements are lower or equal this value", ge=1, le=8)
MIN_COUNTER_QUERY       = Query(default=4,                 description="Considers only compositions, which occured greater or equal this value",      ge=1)
MIN_DATETIME_QUERY      = Query(default=fourteen_days_ago, description="Considers only matches that happened after this time")
REGION_QUERY            = Query(default="europe",          description="Considers only matches of this region (loading korea needs more time)", regex="^(europe|korea)$")
LEAGUE_QUERY            = Query(default="challenger",      description="Considers only matches of this league", regex="^(challenger|grandmaster|master)$")
PATCH_QUERY             = Query(default="13.22",           description="Considers only matches of this patch",  regex="^([0-9]{1,2}\.[0-9]{1,2})$")

## TODO: Add possibility to show both challenger and grandmaster matches and both regions

@app.get("/composition/get-data")
def composition_get_data(
    composition_id: Optional[int] = Query(default=None, description="Considers only compositions with this id"),
    match_id: Optional[str] = Query(default=None, description="Considers only compositions from this match"),
    patch: Optional[str] = PATCH_QUERY,
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY
    ):
    return get_compositions(composition_id, match_id, patch, region, league)


@app.get("/compositionGroup/by-trait")
def composition_group_by_trait(
    trait_name: Optional[str] = Query(default = None, description="Name of the trait to get compositions for. If left blank, all compositions are returned"),
    combination_size: Optional[int] = Query(default=None, description="Number of traits to group by. If left blank, all traits are returned", ge=1, le=7),
    ignore_single_unit_traits: Optional[bool] = Query(default=False, description="Ignored traits, that are unique to one champion"),
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    max_avg_placement: Optional[float] = MAX_AVG_PLACEMENT_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    patch: Optional[str] = PATCH_QUERY,
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_traits(patch, region, league, max_placement, max_avg_placement, min_counter, min_datetime, trait_name, combination_size, ignore_single_unit_traits)


@app.get("/compositionGroup/by-champion")
def composition_group_by_champion(
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    patch: Optional[str] = PATCH_QUERY,
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_champions(patch, region, league, max_placement, min_counter, min_datetime)


@app.get("/item/placements")
def item_placements(
    item_name: Optional[str] = Query(default = None, description="Name of the item to get placements for. If left blank, all items are returned" ),
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return get_item_placements(item_name, region, league, max_placement, min_counter, min_datetime)


@app.get("/item/icons")
def item_icons(
    name: Optional[str] = Query(default = None, description="Name of the item to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the item to get icon path for")
):
    return get_icons(name, display_name, "item")


@app.get("/champion/placements")
def champion_placements(
    champion_name: Optional[str] = Query(default = None, description="Name of the champion to get placements for. If left blank, all champions are returned"),
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY,
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    return get_champion_placements(champion_name, region, league, max_placement, min_datetime)

@app.get("/champion/icons")
def champion_icons(
    name: Optional[str] = Query(default = None, description="Name of the champion to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the champion to get icon path for")
):
    return get_icons(name, display_name, "champion")


@app.get("/trait/placements")
def trait_placements(
    trait_name: Optional[str] = Query(default = None, description="Name of the trait to get placements for. If left blank, all traits are returned"),
    region: Optional[str] = REGION_QUERY,
    league: Optional[str] = LEAGUE_QUERY,
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
):
    return get_trait_placements(trait_name, region, league, max_placement, min_datetime)


@app.get("/trait/icons")
def trait_icons(
    name: Optional[str] = Query(default = None, description="Name of the trait to get icon path for"),
    display_name: Optional[str] = Query(default = None, description="Display name of the trait to get icon path for")
):
    return get_icons(name, display_name, "trait")


@app.post("/composition/load-data")
def composition_load_data( region: Optional[str] = REGION_QUERY,
                           players_amount: Optional[int] = Query(default = 5, description="Load this many players", ge=0, le=200),
                           games_per_player: Optional[int] = Query(default = 5, description="Load this many games of each player", ge=0, le=50),
                           current_patch: Optional[str] = PATCH_QUERY,
                           ranked_league: Optional[str] = LEAGUE_QUERY,
                           min_datetime: Optional[datetime] = Query(default = five_days_ago, description="Load only matches that happened after this time")
                           ):
    start_time = datetime.now()
    stored_matches = load_compositions(region, players_amount, games_per_player, current_patch, ranked_league, min_datetime)
    if stored_matches is None: return {"Error": "Data could not be loaded"}
    seconds = (datetime.now() - start_time).seconds
    return {"Success": f"Data from {stored_matches} matches was loaded successfully in {seconds} seconds"}