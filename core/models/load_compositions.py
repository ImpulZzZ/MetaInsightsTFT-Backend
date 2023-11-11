from core.models.api_utils import *
from core.models.mysql_utils import *
from core.models.sort_utils import *
from core.models.get_static_data import *

import re
import datetime

def store_match_data(matches, current_patch, min_date_time, regional_routing_value, region, api_key):
    connection  = create_mysql_connection()
    static_data = get_static_data()

    ## Build string of match ids for sql query
    match_list_string = ""
    for match in matches: match_list_string += f"'{match}',"
    match_list_string = match_list_string[:-1]

    ## Get all matches that are already stored in database
    sql_result = get_sql_data(f"SELECT DISTINCT match_id FROM composition where match_id in ({match_list_string})", dictionary=False, connection=connection)
    known_matches = [x[0] for x in sql_result]

    match_counter = 0
    for match in matches:
        ## Check if a match was already stored in database and skip if yes
        if match in known_matches: continue
        api_result = request_match_by_match_id( region   = regional_routing_value,
                                                api_key  = api_key,
                                                match    = match )

        ## Matches are ordered by time. Therefore after the first too old match, consecutive matches are too old aswell
        patch = re.search("<Releases/(.*)>", api_result["info"]["game_version"]).group(1)
        if patch != current_patch: continue
        match_date_time = datetime.datetime.fromtimestamp((api_result["info"]["game_datetime"] // 1000))
        if min_date_time > match_date_time: continue

        match_counter += 1

        for participant in api_result["info"]["participants"]:
            composition_id = insert_composition(match, participant['level'], participant['placement'], patch, region, match_date_time, connection=connection)

            for unit in participant["units"]:
                ## Insert unit in database if it is a champion
                try: champion_id = insert_champion(
                        unit['character_id'],
                        static_data[unit['character_id']]['name'],
                        unit['tier'],
                        static_data[unit['character_id']]['cost'],
                        static_data[unit['character_id']]['icon'],
                        composition_id,
                        connection = connection )
                except KeyError: continue

                ## Get static data of the wearables of a champion and skip if it is not an item
                for item in unit["itemNames"]:
                    try: insert_item(   
                        item,
                        static_data[item]['name'],
                        static_data[item]['icon'],
                        champion_id,
                        connection = connection )
                    except KeyError: continue

            for current_trait in participant["traits"]:
                if current_trait['style'] > 0:
                    insert_trait( 
                        current_trait['name'],
                        static_data[current_trait['name']]['name'],
                        current_trait['style'],
                        current_trait['tier_current'],
                        current_trait['tier_total'],
                        static_data[current_trait['name']]['icon'],
                        composition_id,
                        connection = connection )
    connection.close()
    return match_counter



def load_compositions(region, players_amount, games_per_player, current_patch, ranked_league, min_date_time):
    api_key = open("apikey.txt", "r").read()
    stored_matches = 0

    if region == "europe":
        platform_routing_value  = "euw1"
        regional_routing_value  = "europe"
    elif region == "korea":
        platform_routing_value  = "kr"
        regional_routing_value  = "asia"
    else:
        platform_routing_value  = "unknown"
        regional_routing_value  = "unknown"

    player_list = request_players_by_league( region        = platform_routing_value, 
                                             api_key       = api_key,
                                             ranked_league = ranked_league )

    if player_list is None: return None
    
    player_list  = sort_players_by_rank(player_list)
    best_players = player_list[0:players_amount]

    for player in best_players:
        puuid = request_puuid_by_summonername( region        = platform_routing_value,
                                               api_key       = api_key,
                                               summoner_name = player["summonerName"] )

        if puuid is None: return None
                                                    
        matches = request_matches_by_puuid( region     = regional_routing_value,
                                            api_key    = api_key,
                                            puuid      = puuid,
                                            start_time = min_date_time,
                                            count      = games_per_player )

        ## Go to next player if current player has no matches
        if len(matches) == 0: continue
        ## Exit if api request failed
        if matches is None: return None

        ## Store matches in database and return count of stored matches
        stored_matches += store_match_data(matches, current_patch, min_date_time, regional_routing_value, region, api_key)
   
    return stored_matches