from fastapi import FastAPI, Query
from typing import Optional

from core.models.mysql_utils import *
from core.models.get_compositions import *
from core.models.group_compositions import *

from datetime import datetime, timedelta

app = FastAPI()

five_days_ago = datetime.now() - timedelta(days=5)
fourteen_days_ago = datetime.now() - timedelta(days=14)


@app.get("/compositions")
def compositions(min_date_time: datetime = datetime(2023,10,25,0,0,0)):
    print(min_date_time)
    return get_sql_data(f"SELECT * FROM composition where match_time > '{min_date_time}'")


@app.get("/composition_group/by_trait")
def composition_group( max_placement: Optional[int]     = Query(default= 4, description="Considers only compositions, which placements are lower or equal this value", gt=0, le=8),
                       min_counter: Optional[int]       = Query(default= 4, description="Considers only composition groups, which occured greater or equal this value", gt=0),
                       min_datetime: Optional[datetime] = Query(default = fourteen_days_ago, description="Considers only matches that happened after this time")
                      ):
    
    return group_compositions_by_traits(max_placement, min_counter, min_datetime)


@app.get("/composition_group/by_champion")
def composition_group( max_placement: Optional[int]     = Query(default= 4, description="Considers only compositions, which placements are lower or equal this value", gt=0, le=8),
                       min_counter: Optional[int]       = Query(default= 4, description="Considers only composition groups, which occured greater or equal this value", gt=0),
                       min_datetime: Optional[datetime] = Query(default = fourteen_days_ago, description="Considers only matches that happened after this time")
                      ):
    
    return group_compositions_by_champions(max_placement, min_counter, min_datetime)


@app.post("/composition/load_data")
def composition_load_data( region: Optional[str] = Query(default = "europe", description="Load only matches from this region. Valid options: 'europe' and 'korea'"),
                           players_amount: Optional[int] = Query(default = 5, description="Load this many players"),
                           games_per_player: Optional[int] = Query(default = 5, description="Load this many games of each player"),
                           current_patch: Optional[str] = Query(default = "13.21", description="Load only matches that happened after this time"),
                           ranked_league: Optional[str] = Query(default = "challenger", description="Load only matches that happened after this time"),
                           min_datetime: Optional[datetime] = Query(default = five_days_ago, description="Load only matches that happened after this time")
                           ):
    start_time = datetime.now()
    stored_matches = get_compositions(region, players_amount, games_per_player, current_patch, ranked_league, min_datetime)
    if stored_matches is None: return {"Error": "Data could not be loaded"}
    seconds = (datetime.now() - start_time).seconds
    return {"Success": f"Data from {stored_matches} matches was loaded successfully in {seconds} seconds"}


@app.post("/initialize_database")
def initialize_database():
    return initialize_empty_database()