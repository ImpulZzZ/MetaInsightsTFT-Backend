from core.models.api_utils import *
from core.models.mysql_utils import *
from core.models.sort_utils import *
from core.models.get_static_data import *

import re
import datetime

def store_match_data(matches, current_patch, min_date_time, regional_routing_value, api_key):
    # Create a mysql connection
    connection = create_mysql_connection()

    for match in matches:
        ## Check if a match was already stored in database and skip if yes
        if len(get_match_by_id(match)) > 0: continue

        api_result = request_match_by_match_id( region   = regional_routing_value,
                                                api_key  = api_key,
                                                match    = match )

        ## Matches are ordered by time. Therefore after the first too old match, consecutive matches are too old aswell
        patch = re.search("<Releases/(.*)>", api_result["info"]["game_version"]).group(1)
        if patch != current_patch: continue
        match_date_time = datetime.datetime.fromtimestamp((api_result["info"]["game_datetime"] // 1000))
        if min_date_time > match_date_time: continue

        for participant in api_result["info"]["participants"]:
            composition_id = insert_composition(match, participant['level'], participant['placement'], patch, match_date_time)

            for unit in participant["units"]:
                ## Get static data of the champion and skip if a unit is not a champion
                display_name = get_static_data("champion", unit['character_id'], "name")
                if display_name is None: continue
                cost = get_static_data("champion", unit['character_id'], "tier")
                icon = get_icon_path("champion", unit['character_id'])

                champion_id = insert_champion(unit['character_id'], display_name, unit['tier'], cost, icon, composition_id)

                ## Get static data of the wearables of a champion and skip if it is not an item
                for item in unit["itemNames"]:
                    display_name = get_static_data("item", item, "name")
                    if display_name is None: continue
                    icon = get_icon_path("item", item)
                    insert_item(item, display_name, icon, champion_id)

            for current_trait in participant["traits"]:
                if current_trait['style'] > 0: continue
                
                ## Get static data of the trait
                display_name = get_static_data("trait", current_trait['name'], "name")
                icon = get_icon_path("trait", current_trait['name'])

                insert_trait(current_trait['name'], display_name, current_trait['style'], current_trait['tier_current'], current_trait['tier_total'], icon, composition_id)

    connection.commit()
    connection.close()
    return None



def get_compositions(region, players_per_region, games_per_player, current_patch, ranked_league, min_date_time):
    api_key = open("apikey.txt", "r").read()

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

    if player_list is None: return 1
    
    player_list  = sort_players_by_rank(player_list)
    best_players = player_list[0:players_per_region]

    for player in best_players:
        puuid = request_puuid_by_summonername( region        = platform_routing_value,
                                               api_key       = api_key,
                                               summoner_name = player["summonerName"] )

        if puuid is None: return 1
                                                    
        matches = request_matches_by_puuid( region  = regional_routing_value,
                                            api_key = api_key,
                                            puuid   = puuid,
                                            count   = games_per_player )

        if matches is None: return 1
        
        store_match_data(matches, current_patch, min_date_time, regional_routing_value, api_key)

    return 0