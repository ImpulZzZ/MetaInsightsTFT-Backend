from datetime import datetime, timedelta
from fastapi import FastAPI, Query, Path

def init():
    global five_days_ago
    global fourteen_days_ago
    global MAX_AVG_PLACEMENT_QUERY
    global MAX_PLACEMENT_QUERY
    global MIN_COUNTER_QUERY
    global MIN_DATETIME_QUERY
    global REGION_QUERY
    global LEAGUE_QUERY
    global PATCH_QUERY

    five_days_ago     = datetime.now() - timedelta(days=5)
    fourteen_days_ago = datetime.now() - timedelta(days=14)

    MAX_AVG_PLACEMENT_QUERY = Query(default=4,                 description="Considers only composition groups, which average placements are lower or equal this value", ge=1, le=8)
    MAX_PLACEMENT_QUERY     = Query(default=4,                 description="Considers only compositions, which placements are lower or equal this value", ge=1, le=8)
    MIN_COUNTER_QUERY       = Query(default=4,                 description="Considers only compositions, which occured greater or equal this value",      ge=1)
    MIN_DATETIME_QUERY      = Query(default=fourteen_days_ago, description="Considers only matches that happened after this time")
    REGION_QUERY            = Query(default="europe",          description="Considers only matches of this region (loading korea needs more time)", regex="^(europe|korea)$")
    LEAGUE_QUERY            = Query(default="challenger",      description="Considers only matches of this league", regex="^(challenger|grandmaster|master)$")
    PATCH_QUERY             = Query(default="13.23",           description="Considers only matches of this patch",  regex="^([0-9]{1,2}\.[0-9]{1,2})$")