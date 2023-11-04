from fastapi import FastAPI, Query
from typing import Optional

from core.models.mysql_utils import *
from core.models.get_compositions import *
from core.models.group_compositions import *
from core.models.get_placements import *

from datetime import datetime, timedelta

app = FastAPI()

five_days_ago     = datetime.now() - timedelta(days=5)
fourteen_days_ago = datetime.now() - timedelta(days=14)

MAX_PLACEMENT_QUERY = Query(default=4,                 description="Considers only compositions, which placements are lower or equal this value", ge=1, le=8)
MIN_COUNTER_QUERY   = Query(default=4,                 description="Considers only compositions, which occured greater or equal this value",      ge=1)
MIN_DATETIME_QUERY  = Query(default=fourteen_days_ago, description="Considers only matches that happened after this time")

@app.get("/composition/get-data")
def composition_get_data(min_date_time: datetime = datetime(2023,10,25,0,0,0)):
    print(min_date_time)
    return get_sql_data(f"SELECT * FROM composition where match_time > '{min_date_time}'")


@app.get("/compositionGroup/by-trait")
def composition_group_by_trait( 
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_traits(max_placement, min_counter, min_datetime)


@app.get("/compositionGroup/by-champion")
def composition_group_by_champion(
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return group_compositions_by_champions(max_placement, min_counter, min_datetime)


@app.get("/item/placements")
def item_placements(
    item_name: Optional[str] = Query(default = None, description="Name of the item to get placements for. If left blank, all items are returned" ),
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_counter: Optional[int] = MIN_COUNTER_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    
    return get_item_placements(item_name, max_placement, min_counter, min_datetime)


@app.get("/champion/placements")
def champion_placements(
    champion_name: Optional[str] = Query(default = None, description="Name of the champion to get placements for. If left blank, all champions are returned", ),
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
    ):
    return get_champion_placements(champion_name, max_placement, min_datetime)


@app.get("/trait/placements")
def trait_placements(
    trait_name: Optional[str] = Query(default = None, description="Name of the trait to get placements for. If left blank, all traits are returned", ),
    max_placement: Optional[int] = MAX_PLACEMENT_QUERY,
    min_datetime: Optional[datetime] = MIN_DATETIME_QUERY
):
    return get_trait_placements(trait_name, max_placement, min_datetime)

@app.post("/composition/load-data")
def composition_load_data( region: Optional[str] = Query(default = "europe", description="Load only matches from this region", regex="^(europe|korea)$"),
                           players_amount: Optional[int] = Query(default = 5, description="Load this many players", ge=0, le=100),
                           games_per_player: Optional[int] = Query(default = 5, description="Load this many games of each player", ge=0, le=100),
                           current_patch: Optional[str] = Query(default = "13.21", description="Load only matches of this patch", regex="^([0-9]{1,2}\.[0-9]{1,2})$"),
                           ranked_league: Optional[str] = Query(default = "challenger", description="Load only matches in this ranked league", regex="^(challenger|grandmaster|master)$"),
                           min_datetime: Optional[datetime] = Query(default = five_days_ago, description="Load only matches that happened after this time")
                           ):
    start_time = datetime.now()
    stored_matches = get_compositions(region, players_amount, games_per_player, current_patch, ranked_league, min_datetime)
    if stored_matches is None: return {"Error": "Data could not be loaded"}
    seconds = (datetime.now() - start_time).seconds
    return {"Success": f"Data from {stored_matches} matches was loaded successfully in {seconds} seconds"}