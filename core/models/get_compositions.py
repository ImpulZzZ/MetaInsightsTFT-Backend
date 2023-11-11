from core.models.mysql_utils import *
#from mysql_utils import *

def build_sql_query(args):
    base_query = "SELECT * FROM composition"

    conditions = []
    for key, value in args.items():
        if value is not None:
            conditions.append(f"{key} = '{value}'")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    return base_query


def get_compositions(composition_id, match_id, patch, region, league):
    args = {
        'id': composition_id,
        'match_id': match_id,
        'patch': patch,
        'region': region,
        'league': league
    }
    sql = build_sql_query(args)
    print(sql)
    return get_sql_data(sql)