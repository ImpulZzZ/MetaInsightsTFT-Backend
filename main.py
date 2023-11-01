from fastapi import FastAPI, Path
from typing import Optional

from core.models.mysql_utils import *
from core.models.get_compositions import *

from datetime import datetime

app = FastAPI()

def add_filters_to_sql(sql, filters):
    result_sql = sql
    filter_count = len(filters)
    if filter_count > 0: result_sql += " WHERE"

    for i in range(0, filter_count):
        result_sql += f" {filters[i]}"
        if i < (filter_count - 1): result_sql += " AND"

    return result_sql

@app.get("/composition_groups")
def composition_groups(avg_placement: Optional[float] = None, counter: Optional[int] = None, grouped_by: Optional[str] = None):
    filters = []
    if avg_placement is not None: filters.append(f"avg_placement <= {avg_placement}")
    if counter is not None:       filters.append(f"counter >= {counter}")
    if grouped_by is not None:    filters.append(f"grouped_by = '{grouped_by}'")
    
    sql = add_filters_to_sql("SELECT * FROM composition_group", filters)
    return get_sql_data(sql)


@app.get("/compositions")
def compositions(min_date_time: datetime = datetime(2023,10,25,0,0,0)):
    print(min_date_time)
    return get_sql_data(f"SELECT * FROM composition where match_time > '{min_date_time}'")


@app.get("/composition_group/{composition_group_id}")
def composition_group(composition_group_id: int = Path(description="The ID of the composition group", gt=0)):
    return get_sql_data(f"SELECT * FROM composition_group WHERE id={composition_group_id}")

@app.post("/composition/load_data")
def composition_load_data( region: str = "europe", 
                           games_per_player: int = 5,
                           players_per_region: int = 5,
                           current_patch: str = "13.21",
                           ranked_league: str = "challenger",
                           min_date_time: datetime = datetime(2023,10,25,0,0,0)):

    rc = get_compositions(region, players_per_region, games_per_player, current_patch, ranked_league, min_date_time)
    if rc != 0: return {"Error": "Data could not be loaded"}
    return {"Success": "Data was loaded successfully"}

@app.post("/initialize_database")
def initialize_database():
    return initialize_empty_database()